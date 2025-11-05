"""
Analytics API endpoints (Phase 3)
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.services.analytics_service import analytics_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/agent/{agent_id}/performance", response_model=dict)
async def get_agent_performance(agent_id: int, days: int = 30):
    """
    Get detailed performance metrics for an agent
    
    - Task statistics and timeline
    - Reputation trends
    - Earnings summary
    """
    try:
        performance = await analytics_service.get_agent_performance(agent_id, days)
        
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent performance: {str(e)}"
        )


@router.get("/ecosystem/health", response_model=dict)
async def get_ecosystem_health():
    """
    Get overall ecosystem health metrics
    
    - Agent activity
    - Task statistics
    - Reputation trends
    - Payment activity
    - Overall health score (0-100)
    """
    try:
        health = await analytics_service.get_ecosystem_health()
        return health
        
    except Exception as e:
        logger.error(f"Failed to get ecosystem health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ecosystem health: {str(e)}"
        )


@router.get("/categories/insights", response_model=dict)
async def get_category_insights():
    """
    Get insights by agent category/capability
    
    - Agent count per category
    - Average reputation
    - Task volume
    """
    try:
        insights = await analytics_service.get_category_insights()
        
        return {
            "categories": insights,
            "total_categories": len(insights)
        }
        
    except Exception as e:
        logger.error(f"Failed to get category insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category insights: {str(e)}"
        )


@router.get("/agents/trending", response_model=dict)
async def get_trending_agents(days: int = 7, limit: int = 10):
    """
    Get trending agents based on recent activity
    
    Uses composite score based on:
    - Recent tasks
    - Recent feedback
    - Completion rate
    - Average rating
    """
    try:
        trending = await analytics_service.get_trending_agents(days, limit)
        
        return {
            "trending_agents": trending,
            "period_days": days,
            "total": len(trending)
        }
        
    except Exception as e:
        logger.error(f"Failed to get trending agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending agents: {str(e)}"
        )


@router.get("/dashboard/summary", response_model=dict)
async def get_dashboard_summary():
    """
    Get comprehensive dashboard summary
    
    Combines multiple analytics for a complete overview
    """
    try:
        # Get all key metrics
        health = await analytics_service.get_ecosystem_health()
        trending = await analytics_service.get_trending_agents(days=7, limit=5)
        categories = await analytics_service.get_category_insights()
        
        return {
            "ecosystem_health": health,
            "trending_agents": trending[:5],
            "top_categories": categories[:10],
            "generated_at": health["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )

