"""
Reputation System API endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging

from app.services.blockchain import blockchain_service

router = APIRouter()
logger = logging.getLogger(__name__)


class FeedbackRequest(BaseModel):
    """Request body for submitting feedback"""
    agent_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., max_length=1000)
    payment_proof: str = Field(..., description="x402 payment proof hash")
    reviewer_address: str
    private_key: str


@router.get("/{agent_id}")
async def get_agent_reputation(agent_id: int):
    """
    Get reputation score and statistics for an agent
    """
    try:
        # Get reputation from blockchain
        avg_rating, feedback_count = await blockchain_service.get_reputation_score(agent_id)
        
        # Get validation stats
        validation_stats = await blockchain_service.get_validation_stats(agent_id)
        
        return {
            "agent_id": agent_id,
            "average_rating": avg_rating,
            "feedback_count": feedback_count,
            "reputation_tier": _get_reputation_tier(avg_rating, feedback_count),
            "validation_stats": validation_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get reputation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reputation: {str(e)}"
        )


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for an agent
    
    Requires x402 payment proof to prevent spam
    """
    try:
        # Convert payment proof string to bytes32
        payment_proof_bytes = bytes.fromhex(request.payment_proof.replace("0x", ""))
        
        await blockchain_service.submit_feedback(
            agent_id=request.agent_id,
            rating=request.rating,
            comment=request.comment,
            payment_proof=payment_proof_bytes,
            reviewer_address=request.reviewer_address,
            private_key=request.private_key
        )
        
        logger.info(f"✅ Feedback submitted for agent {request.agent_id}")
        
        return {
            "message": "Feedback submitted successfully",
            "agent_id": request.agent_id,
            "rating": request.rating
        }
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/{agent_id}/history")
async def get_feedback_history(agent_id: int, limit: int = 20, offset: int = 0):
    """
    Get feedback history for an agent
    """
    try:
        from app.database import get_feedbacks_collection
        feedbacks_collection = get_feedbacks_collection()
        
        # Get total count
        total = await feedbacks_collection.count_documents({"agent_id": agent_id})
        
        # Get feedbacks with pagination
        cursor = feedbacks_collection.find(
            {"agent_id": agent_id}
        ).sort("created_at", -1).skip(offset).limit(limit)
        
        feedbacks = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id and format
        feedback_list = []
        for feedback in feedbacks:
            feedback_list.append({
                "agent_id": feedback["agent_id"],
                "rating": feedback["rating"],
                "comment": feedback.get("comment", ""),
                "reviewer_address": feedback["reviewer_address"],
                "tx_hash": feedback.get("tx_hash", ""),
                "created_at": feedback["created_at"]
            })
        
        return {
            "feedbacks": feedback_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback history: {str(e)}"
        )


@router.get("/leaderboard/top")
async def get_reputation_leaderboard(limit: int = 50, min_feedback_count: int = 5):
    """
    Get reputation leaderboard
    
    Shows top rated agents with minimum feedback threshold
    """
    try:
        from app.database import get_agents_collection
        agents_collection = get_agents_collection()
        
        # Find agents with minimum feedback and sort by reputation
        cursor = agents_collection.find({
            "feedback_count": {"$gte": min_feedback_count},
            "is_active": True
        }).sort("reputation_score", -1).limit(limit)
        
        agents = await cursor.to_list(length=limit)
        
        leaderboard = []
        for rank, agent in enumerate(agents, 1):
            leaderboard.append({
                "rank": rank,
                "token_id": agent["token_id"],
                "name": agent["name"],
                "reputation_score": agent["reputation_score"],
                "feedback_count": agent["feedback_count"],
                "capabilities": agent["capabilities"][:3],  # Top 3 capabilities
                "reputation_tier": _get_reputation_tier(
                    agent["reputation_score"],
                    agent["feedback_count"]
                )
            })
        
        return {
            "leaderboard": leaderboard,
            "total": len(leaderboard),
            "min_feedback_count": min_feedback_count
        }
        
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {str(e)}"
        )


def _get_reputation_tier(avg_rating: float, feedback_count: int) -> str:
    """Calculate reputation tier"""
    if feedback_count == 0:
        return "New"
    elif avg_rating >= 4.5 and feedback_count >= 100:
        return "Platinum"
    elif avg_rating >= 4.0 and feedback_count >= 50:
        return "Gold"
    elif avg_rating >= 3.5 and feedback_count >= 20:
        return "Silver"
    elif avg_rating >= 3.0 and feedback_count >= 5:
        return "Bronze"
    else:
        return "New"

