"""
Monitoring and Error Tracking API endpoints (Phase 3)
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.services.error_tracking import error_tracker, request_logger

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/errors/stats", response_model=dict)
async def get_error_statistics(hours: int = 24):
    """
    Get error statistics for the last N hours
    
    - Total errors
    - Errors by type
    - Errors by severity
    """
    try:
        stats = await error_tracker.get_error_stats(hours)
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get error stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get error stats: {str(e)}"
        )


@router.get("/errors/recent", response_model=dict)
async def get_recent_errors(limit: int = 50):
    """
    Get recent errors
    
    Returns list of recent errors with details
    """
    try:
        errors = await error_tracker.get_recent_errors(limit)
        
        return {
            "errors": errors,
            "total": len(errors)
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent errors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent errors: {str(e)}"
        )


@router.post("/errors/{error_id}/resolve", response_model=dict)
async def mark_error_resolved(error_id: str):
    """
    Mark an error as resolved
    """
    try:
        success = await error_tracker.mark_resolved(error_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error not found"
            )
        
        return {
            "message": "Error marked as resolved",
            "error_id": error_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark error as resolved: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark error as resolved: {str(e)}"
        )


@router.get("/requests/stats", response_model=dict)
async def get_request_statistics(hours: int = 24):
    """
    Get API request statistics
    
    - Total requests
    - Requests by status code
    - Top endpoints
    - Average response time
    """
    try:
        stats = await request_logger.get_request_stats(hours)
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get request stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get request stats: {str(e)}"
        )


@router.get("/health/detailed", response_model=dict)
async def get_detailed_health():
    """
    Get detailed system health information
    
    - Error rate
    - Request stats
    - System status
    """
    try:
        error_stats = await error_tracker.get_error_stats(hours=1)
        request_stats = await request_logger.get_request_stats(hours=1)
        
        # Calculate error rate
        total_requests = request_stats["total_requests"]
        total_errors = error_stats["total_errors"]
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # Determine health status
        if error_rate < 1:
            health_status = "healthy"
        elif error_rate < 5:
            health_status = "degraded"
        else:
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "error_rate_percent": round(error_rate, 2),
            "last_hour": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "average_response_time_ms": request_stats["average_response_time_ms"]
            },
            "errors_by_type": error_stats["errors_by_type"][:5],  # Top 5 errors
            "top_endpoints": request_stats["top_endpoints"][:5]  # Top 5 endpoints
        }
        
    except Exception as e:
        logger.error(f"Failed to get detailed health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get detailed health: {str(e)}"
        )

