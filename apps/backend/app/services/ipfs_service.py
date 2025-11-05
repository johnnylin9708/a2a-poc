"""
IPFS service for decentralized file storage
"""

import json
import logging
from typing import Dict, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class IPFSService:
    """Service for IPFS interactions"""
    
    def __init__(self):
        self.api_url = settings.IPFS_API_URL
        self.gateway_url = settings.IPFS_GATEWAY_URL
        self.pinata_api_key = settings.PINATA_API_KEY
        self.pinata_secret = settings.PINATA_SECRET_KEY
        self.use_pinata = bool(self.pinata_api_key and self.pinata_secret)
        
        if self.use_pinata:
            logger.info("✅ IPFS Service initialized with Pinata")
        else:
            logger.info("✅ IPFS Service initialized with local node")
    
    async def upload_json(self, data: Dict) -> str:
        """
        Upload JSON data to IPFS
        
        Args:
            data: Dictionary to upload
            
        Returns:
            IPFS CID (Content Identifier)
        """
        if self.use_pinata:
            return await self._upload_to_pinata(data)
        else:
            # Fallback to mock for local development without IPFS
            try:
                return await self._upload_to_local(data)
            except Exception as e:
                logger.warning(f"⚠️ Local IPFS not available, using mock CID: {e}")
                # Generate a mock IPFS CID for development
                import hashlib
                import json
                data_str = json.dumps(data, sort_keys=True)
                mock_cid = hashlib.sha256(data_str.encode()).hexdigest()[:46]
                logger.info(f"✅ Mock IPFS upload: Qm{mock_cid}")
                return f"ipfs://Qm{mock_cid}"
    
    async def _upload_to_pinata(self, data: Dict) -> str:
        """Upload to Pinata IPFS pinning service"""
        try:
            headers = {
                "pinata_api_key": self.pinata_api_key,
                "pinata_secret_api_key": self.pinata_secret,
                "Content-Type": "application/json"
            }
            
            payload = {
                "pinataContent": data,
                "pinataOptions": {
                    "cidVersion": 1
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.pinata.cloud/pinning/pinJSONToIPFS",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                cid = result["IpfsHash"]
                
                logger.info(f"✅ Uploaded to Pinata: {cid}")
                return f"ipfs://{cid}"
                
        except Exception as e:
            logger.error(f"❌ Failed to upload to Pinata: {e}")
            raise
    
    async def _upload_to_local(self, data: Dict) -> str:
        """Upload to local IPFS node"""
        try:
            json_data = json.dumps(data).encode('utf-8')
            
            async with httpx.AsyncClient() as client:
                files = {'file': json_data}
                response = await client.post(
                    f"{self.api_url}/api/v0/add",
                    files=files,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                cid = result["Hash"]
                
                logger.info(f"✅ Uploaded to local IPFS: {cid}")
                return f"ipfs://{cid}"
                
        except Exception as e:
            logger.error(f"❌ Failed to upload to local IPFS: {e}")
            raise
    
    async def get_json(self, cid: str) -> Optional[Dict]:
        """
        Retrieve JSON data from IPFS
        
        Args:
            cid: IPFS CID (with or without ipfs:// prefix)
            
        Returns:
            Dictionary of data
        """
        # Remove ipfs:// prefix if present
        if cid.startswith("ipfs://"):
            cid = cid[7:]
        
        try:
            # Try gateway first
            url = f"{self.gateway_url}/ipfs/{cid}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ Retrieved from IPFS: {cid}")
                return data
                
        except Exception as e:
            logger.error(f"❌ Failed to retrieve from IPFS: {e}")
            return None
    
    def get_gateway_url(self, cid: str) -> str:
        """Get gateway URL for a CID"""
        if cid.startswith("ipfs://"):
            cid = cid[7:]
        return f"{self.gateway_url}/ipfs/{cid}"


# Create singleton instance
ipfs_service = IPFSService()

