"""
API Key Management endpoints (Phase 3)
"""

from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
import logging

from app.services.api_key_service import api_key_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    owner_address: str,
    tier: str = "free",
    name: Optional[str] = None,
    expires_in_days: Optional[int] = None
):
    """
    Create a new API key
    
    - Generates secure API key
    - Sets tier and limits
    - Optional expiration
    
    ⚠️ API key is shown only once!
    """
    try:
        result = await api_key_service.create_api_key(
            owner_address=owner_address,
            tier=tier,
            name=name,
            expires_in_days=expires_in_days
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/validate", response_model=dict)
async def validate_api_key(x_api_key: str = Header(...)):
    """
    Validate an API key
    
    Checks:
    - Key exists and is active
    - Not expired
    - Returns tier and limits
    """
    try:
        key_info = await api_key_service.validate_api_key(x_api_key)
        
        if not key_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key"
            )
        
        return {
            "valid": True,
            "tier": key_info["tier"],
            "owner_address": key_info["owner_address"],
            "name": key_info["name"],
            "expires_at": key_info.get("expires_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate API key: {str(e)}"
        )


@router.get("/user/{owner_address}", response_model=dict)
async def get_user_api_keys(owner_address: str):
    """
    Get all API keys for a user
    
    Returns list of keys (without sensitive data)
    """
    try:
        keys = await api_key_service.get_user_keys(owner_address)
        
        return {
            "keys": keys,
            "total": len(keys)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user keys: {str(e)}"
        )


@router.post("/revoke", response_model=dict)
async def revoke_api_key(key_hash: str, owner_address: str):
    """
    Revoke an API key
    
    Permanently disables the key
    """
    try:
        success = await api_key_service.revoke_api_key(key_hash, owner_address)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found or already revoked"
            )
        
        return {
            "message": "API key revoked successfully",
            "key_hash": key_hash[:16] + "..."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {str(e)}"
        )


@router.post("/upgrade", response_model=dict)
async def upgrade_api_key_tier(key_hash: str, owner_address: str, new_tier: str):
    """
    Upgrade API key tier
    
    Tiers: free, basic, pro
    """
    try:
        success = await api_key_service.upgrade_tier(key_hash, owner_address, new_tier)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        tier_info = api_key_service.TIERS[new_tier]
        
        return {
            "message": f"API key upgraded to {new_tier}",
            "new_tier": new_tier,
            "new_limits": tier_info
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upgrade API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade API key: {str(e)}"
        )


@router.get("/usage/{key_hash}", response_model=dict)
async def get_api_key_usage(key_hash: str):
    """
    Get usage statistics for an API key
    
    - Total requests
    - Monthly requests
    - Last used
    - Limits
    """
    try:
        stats = await api_key_service.get_usage_stats(key_hash)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage stats: {str(e)}"
        )


@router.get("/tiers", response_model=dict)
async def get_tier_information():
    """
    Get information about all API key tiers
    
    - Limits
    - Pricing
    - Features
    """
    return {
        "tiers": api_key_service.get_tier_info()
    }

