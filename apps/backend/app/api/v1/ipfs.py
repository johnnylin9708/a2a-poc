"""
IPFS API endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.services.ipfs_service import ipfs_service

router = APIRouter()
logger = logging.getLogger(__name__)


class IPFSUploadRequest(BaseModel):
    """Request body for IPFS upload"""
    data: Dict[Any, Any] = None
    
    class Config:
        extra = "allow"


@router.post("/upload")
async def upload_to_ipfs(data: Dict[Any, Any]):
    """
    Upload JSON data to IPFS
    
    Returns the IPFS URI (ipfs://...)
    """
    try:
        ipfs_uri = await ipfs_service.upload_json(data)
        
        logger.info(f"✅ Uploaded to IPFS: {ipfs_uri}")
        
        return {
            "ipfs_uri": ipfs_uri,
            "gateway_url": ipfs_service.get_gateway_url(ipfs_uri)
        }
        
    except Exception as e:
        logger.error(f"Failed to upload to IPFS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload to IPFS: {str(e)}"
        )


@router.get("/get/{cid}")
async def get_from_ipfs(cid: str):
    """
    Retrieve JSON data from IPFS by CID
    """
    try:
        data = await ipfs_service.get_json(cid)
        
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data not found for CID: {cid}"
            )
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve from IPFS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve from IPFS: {str(e)}"
        )

