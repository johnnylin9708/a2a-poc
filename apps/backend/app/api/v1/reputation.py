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


# ========== Specific routes first (to avoid conflicts with path parameters) ==========

@router.get("/all-feedbacks")
async def get_all_feedbacks(limit: int = 50, offset: int = 0, agent_id: int = None):
    """
    Get all feedback history (optionally filtered by agent_id)
    """
    try:
        from app.database import get_feedbacks_collection, get_agents_collection
        feedbacks_collection = get_feedbacks_collection()
        agents_collection = get_agents_collection()
        
        # Build query filter
        query = {}
        if agent_id is not None:
            query["agent_id"] = agent_id
        
        # Get total count
        total = await feedbacks_collection.count_documents(query)
        
        # Get feedbacks with pagination
        cursor = feedbacks_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        feedbacks = await cursor.to_list(length=limit)
        
        # Enrich with agent names
        for feedback in feedbacks:
            feedback["_id"] = str(feedback["_id"])
            # Get agent name
            agent = await agents_collection.find_one({"token_id": feedback["agent_id"]})
            if agent:
                feedback["agent_name"] = agent.get("name", f"Agent #{feedback['agent_id']}")
            else:
                feedback["agent_name"] = f"Agent #{feedback['agent_id']}"
        
        return {
            "feedbacks": feedbacks,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get all feedbacks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get all feedbacks: {str(e)}"
        )


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for an agent
    
    Requires x402 payment proof to prevent spam
    """
    try:
        from datetime import datetime, timezone
        from app.database import get_feedbacks_collection
        
        # Convert payment proof string to bytes32
        payment_proof_bytes = bytes.fromhex(request.payment_proof.replace("0x", ""))
        
        # 1. 提交到区块链
        tx_receipt = await blockchain_service.submit_feedback(
            agent_id=request.agent_id,
            rating=request.rating,
            comment=request.comment,
            payment_proof=payment_proof_bytes,
            reviewer_address=request.reviewer_address,
            private_key=request.private_key
        )
        
        # 2. 存入数据库
        feedbacks_collection = get_feedbacks_collection()
        feedback_doc = {
            "agent_id": request.agent_id,
            "rating": request.rating,
            "comment": request.comment,
            "reviewer_address": request.reviewer_address,
            "payment_proof": request.payment_proof,
            "tx_hash": tx_receipt['transactionHash'].hex() if tx_receipt else None,
            "block_number": tx_receipt['blockNumber'] if tx_receipt else None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "confirmed"
        }
        
        result = await feedbacks_collection.insert_one(feedback_doc)
        
        logger.info(f"✅ Feedback submitted and saved: agent {request.agent_id}, doc_id {result.inserted_id}")
        
        return {
            "message": "Feedback submitted successfully",
            "agent_id": request.agent_id,
            "rating": request.rating,
            "feedback_id": str(result.inserted_id),
            "tx_hash": feedback_doc.get("tx_hash")
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


# ========== Path parameter routes last (to avoid conflicts) ==========

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

