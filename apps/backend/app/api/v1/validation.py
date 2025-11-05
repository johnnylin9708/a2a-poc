"""
Validation System API endpoints
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.services.blockchain import blockchain_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{agent_id}")
async def get_agent_validations(agent_id: int):
    """
    Get validation history and statistics for an agent
    """
    try:
        # Get validation stats from blockchain
        stats = await blockchain_service.get_validation_stats(agent_id)
        
        # Calculate validation score
        if stats["total_validations"] > 0:
            score = (stats["passed_validations"] / stats["total_validations"]) * 100
        else:
            score = 0
        
        return {
            "agent_id": agent_id,
            "validation_score": score,
            "total_validations": stats["total_validations"],
            "passed_validations": stats["passed_validations"],
            "failed_validations": stats["failed_validations"],
            "last_validation_time": stats["last_validation_time"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get validations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get validations: {str(e)}"
        )

