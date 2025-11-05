"""
API Key Management Service (Phase 3)
"""

from typing import Optional, Dict, List
import secrets
import hashlib
from datetime import datetime, timedelta
import logging

from app.database import get_api_keys_collection

logger = logging.getLogger(__name__)


class APIKeyService:
    """Service for managing API keys and tiers"""
    
    TIERS = {
        "free": {
            "name": "Free",
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "price": 0
        },
        "basic": {
            "name": "Basic",
            "requests_per_minute": 120,
            "requests_per_hour": 5000,
            "price": 29
        },
        "pro": {
            "name": "Pro",
            "requests_per_minute": 300,
            "requests_per_hour": 20000,
            "price": 99
        }
    }
    
    def __init__(self):
        self._api_keys_collection = None
        self._usage_collection = None
        logger.info("✅ API Key Service initialized")
    
    @property
    def api_keys_collection(self):
        if self._api_keys_collection is None:
            self._api_keys_collection = get_api_keys_collection()
        return self._api_keys_collection
    
    @property
    def usage_collection(self):
        if self._usage_collection is None:
            # For now, we track usage in the api_keys collection itself
            # Future: separate collection for detailed usage logs
            self._usage_collection = get_api_keys_collection()
        return self._usage_collection
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        # Convert to hex string with 'ak_' prefix
        api_key = f"ak_{random_bytes.hex()}"
        return api_key
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def create_api_key(
        self,
        owner_address: str,
        tier: str = "free",
        name: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> Dict:
        """
        Create a new API key
        
        Args:
            owner_address: Wallet address of owner
            tier: API key tier (free, basic, pro)
            name: Optional name for the API key
            expires_in_days: Optional expiration period
        
        Returns:
            API key info including the unhashed key (show once)
        """
        try:
            if tier not in self.TIERS:
                raise ValueError(f"Invalid tier: {tier}")
            
            # Generate API key
            api_key = self.generate_api_key()
            key_hash = self.hash_api_key(api_key)
            
            # Calculate expiration
            created_at = datetime.utcnow()
            expires_at = None
            if expires_in_days:
                expires_at = created_at + timedelta(days=expires_in_days)
            
            # Create document
            key_doc = {
                "key_hash": key_hash,
                "owner_address": owner_address,
                "tier": tier,
                "name": name or f"{tier.capitalize()} API Key",
                "created_at": created_at,
                "expires_at": expires_at,
                "is_active": True,
                "last_used_at": None,
                "total_requests": 0,
                "requests_this_month": 0
            }
            
            await self.api_keys_collection.insert_one(key_doc)
            
            logger.info(f"✅ API Key created for {owner_address} ({tier} tier)")
            
            # Return key info (include unhashed key only once)
            return {
                "api_key": api_key,  # ⚠️ Show once only
                "key_hash": key_hash,
                "tier": tier,
                "tier_limits": self.TIERS[tier],
                "name": key_doc["name"],
                "created_at": created_at,
                "expires_at": expires_at,
                "warning": "Save this API key now. You won't be able to see it again."
            }
            
        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            raise
    
    async def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """
        Validate API key and return key info
        
        Args:
            api_key: API key to validate
        
        Returns:
            Key info if valid, None if invalid
        """
        try:
            key_hash = self.hash_api_key(api_key)
            
            key_doc = await self.api_keys_collection.find_one({
                "key_hash": key_hash,
                "is_active": True
            })
            
            if not key_doc:
                return None
            
            # Check expiration
            if key_doc.get("expires_at"):
                if datetime.utcnow() > key_doc["expires_at"]:
                    logger.warning(f"API key expired: {key_hash[:16]}...")
                    return None
            
            # Update last used
            await self.api_keys_collection.update_one(
                {"key_hash": key_hash},
                {
                    "$set": {"last_used_at": datetime.utcnow()},
                    "$inc": {
                        "total_requests": 1,
                        "requests_this_month": 1
                    }
                }
            )
            
            key_doc.pop("_id", None)
            return key_doc
            
        except Exception as e:
            logger.error(f"Failed to validate API key: {e}")
            return None
    
    async def get_user_keys(self, owner_address: str) -> List[Dict]:
        """Get all API keys for a user"""
        try:
            cursor = self.api_keys_collection.find({
                "owner_address": owner_address
            }).sort("created_at", -1)
            
            keys = await cursor.to_list(length=100)
            
            for key in keys:
                key.pop("_id", None)
                key.pop("key_hash", None)  # Don't expose hash
            
            return keys
            
        except Exception as e:
            logger.error(f"Failed to get user keys: {e}")
            raise
    
    async def revoke_api_key(self, key_hash: str, owner_address: str) -> bool:
        """Revoke an API key"""
        try:
            result = await self.api_keys_collection.update_one(
                {"key_hash": key_hash, "owner_address": owner_address},
                {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ API key revoked: {key_hash[:16]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            raise
    
    async def upgrade_tier(self, key_hash: str, owner_address: str, new_tier: str) -> bool:
        """Upgrade API key tier"""
        try:
            if new_tier not in self.TIERS:
                raise ValueError(f"Invalid tier: {new_tier}")
            
            result = await self.api_keys_collection.update_one(
                {"key_hash": key_hash, "owner_address": owner_address},
                {
                    "$set": {
                        "tier": new_tier,
                        "upgraded_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ API key upgraded to {new_tier}: {key_hash[:16]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to upgrade API key: {e}")
            raise
    
    async def get_usage_stats(self, key_hash: str) -> Dict:
        """Get usage statistics for an API key"""
        try:
            key_doc = await self.api_keys_collection.find_one({"key_hash": key_hash})
            
            if not key_doc:
                return None
            
            tier_limits = self.TIERS[key_doc["tier"]]
            
            return {
                "tier": key_doc["tier"],
                "total_requests": key_doc.get("total_requests", 0),
                "requests_this_month": key_doc.get("requests_this_month", 0),
                "last_used_at": key_doc.get("last_used_at"),
                "limits": tier_limits,
                "created_at": key_doc.get("created_at"),
                "expires_at": key_doc.get("expires_at")
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            raise
    
    async def reset_monthly_usage(self):
        """Reset monthly usage counters (run as cron job)"""
        try:
            result = await self.api_keys_collection.update_many(
                {},
                {"$set": {"requests_this_month": 0}}
            )
            
            logger.info(f"✅ Reset monthly usage for {result.modified_count} API keys")
            
        except Exception as e:
            logger.error(f"Failed to reset monthly usage: {e}")
            raise
    
    @staticmethod
    def get_tier_info() -> Dict:
        """Get information about all tiers"""
        return APIKeyService.TIERS


api_key_service = APIKeyService()

