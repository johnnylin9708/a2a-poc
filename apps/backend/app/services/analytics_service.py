"""
Analytics Service for ecosystem metrics and insights (Phase 3)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_agents_collection, get_tasks_collection, get_feedbacks_collection, get_payments_collection

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating analytics and insights"""
    
    def __init__(self):
        self._agents_collection = None
        self._tasks_collection = None
        self._feedbacks_collection = None
        self._payments_collection = None
        logger.info("✅ Analytics Service initialized")
    
    @property
    def agents_collection(self):
        if self._agents_collection is None:
            self._agents_collection = get_agents_collection()
        return self._agents_collection
    
    @property
    def tasks_collection(self):
        if self._tasks_collection is None:
            self._tasks_collection = get_tasks_collection()
        return self._tasks_collection
    
    @property
    def feedbacks_collection(self):
        if self._feedbacks_collection is None:
            self._feedbacks_collection = get_feedbacks_collection()
        return self._feedbacks_collection
    
    @property
    def payments_collection(self):
        if self._payments_collection is None:
            self._payments_collection = get_payments_collection()
        return self._payments_collection
    
    async def get_agent_performance(self, agent_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed performance metrics for an agent
        
        Args:
            agent_id: Agent token ID
            days: Number of days to analyze
        
        Returns:
            Performance metrics including tasks, reputation trends, earnings
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get agent info
            agent = await self.agents_collection.find_one({"token_id": agent_id})
            if not agent:
                return None
            
            # Task metrics
            task_pipeline = [
                {"$match": {"agent_id": agent_id, "created_at": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]
            task_stats = await self.tasks_collection.aggregate(task_pipeline).to_list(length=10)
            
            task_summary = {status["_id"]: status["count"] for status in task_stats}
            
            # Task timeline (daily breakdown)
            task_timeline_pipeline = [
                {"$match": {"agent_id": agent_id, "created_at": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                    },
                    "total": {"$sum": 1},
                    "completed": {
                        "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                    }
                }},
                {"$sort": {"_id": 1}}
            ]
            task_timeline = await self.tasks_collection.aggregate(task_timeline_pipeline).to_list(length=days)
            
            # Reputation trends
            feedback_pipeline = [
                {"$match": {"agent_id": agent_id, "created_at": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                    },
                    "avg_rating": {"$avg": "$rating"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            reputation_trend = await self.feedbacks_collection.aggregate(feedback_pipeline).to_list(length=days)
            
            # Payment metrics
            payment_pipeline = [
                {"$match": {"agent_id": agent_id, "created_at": {"$gte": cutoff_date}}},
                {"$group": {
                    "_id": None,
                    "total_earnings": {"$sum": {"$toDouble": "$payment_proof.amount"}},
                    "payment_count": {"$sum": 1}
                }}
            ]
            payment_stats = await self.payments_collection.aggregate(payment_pipeline).to_list(length=1)
            
            earnings = payment_stats[0] if payment_stats else {"total_earnings": 0, "payment_count": 0}
            
            return {
                "agent_id": agent_id,
                "agent_name": agent.get("name"),
                "period_days": days,
                "summary": {
                    "total_tasks": sum(task_summary.values()),
                    "completed_tasks": task_summary.get("completed", 0),
                    "in_progress_tasks": task_summary.get("in_progress", 0),
                    "failed_tasks": task_summary.get("failed", 0),
                    "success_rate": (task_summary.get("completed", 0) / sum(task_summary.values()) * 100) 
                                    if sum(task_summary.values()) > 0 else 0,
                    "current_reputation": agent.get("reputation_score", 0) / 100,
                    "total_earnings": earnings.get("total_earnings", 0),
                    "payment_count": earnings.get("payment_count", 0)
                },
                "task_breakdown": task_summary,
                "task_timeline": task_timeline,
                "reputation_trend": reputation_trend
            }
            
        except Exception as e:
            logger.error(f"Failed to get agent performance: {e}")
            raise
    
    async def get_ecosystem_health(self) -> Dict[str, Any]:
        """
        Get overall ecosystem health metrics
        
        Returns:
            Comprehensive ecosystem metrics
        """
        try:
            now = datetime.utcnow()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            last_30d = now - timedelta(days=30)
            
            # Agent metrics
            total_agents = await self.agents_collection.count_documents({})
            active_agents_24h = await self.agents_collection.count_documents({
                "updated_at": {"$gte": last_24h}
            })
            new_agents_7d = await self.agents_collection.count_documents({
                "created_at": {"$gte": last_7d}
            })
            
            # Task metrics
            total_tasks = await self.tasks_collection.count_documents({})
            tasks_24h = await self.tasks_collection.count_documents({
                "created_at": {"$gte": last_24h}
            })
            completed_tasks = await self.tasks_collection.count_documents({"status": "completed"})
            
            # Reputation metrics
            total_feedback = await self.feedbacks_collection.count_documents({})
            feedback_7d = await self.feedbacks_collection.count_documents({
                "created_at": {"$gte": last_7d}
            })
            
            avg_rep_pipeline = [
                {"$match": {"feedback_count": {"$gt": 0}}},
                {"$group": {
                    "_id": None,
                    "avg_reputation": {"$avg": "$reputation_score"}
                }}
            ]
            avg_rep_result = await self.agents_collection.aggregate(avg_rep_pipeline).to_list(length=1)
            avg_reputation = avg_rep_result[0]["avg_reputation"] / 100 if avg_rep_result else 0
            
            # Payment metrics
            total_payments = await self.payments_collection.count_documents({})
            payments_30d = await self.payments_collection.count_documents({
                "created_at": {"$gte": last_30d}
            })
            
            # Calculate health score (0-100)
            health_score = self._calculate_health_score(
                total_agents, active_agents_24h, tasks_24h, 
                completed_tasks / total_tasks if total_tasks > 0 else 0,
                avg_reputation
            )
            
            return {
                "timestamp": now,
                "health_score": health_score,
                "agents": {
                    "total": total_agents,
                    "active_24h": active_agents_24h,
                    "new_7d": new_agents_7d,
                    "activity_rate": (active_agents_24h / total_agents * 100) if total_agents > 0 else 0
                },
                "tasks": {
                    "total": total_tasks,
                    "created_24h": tasks_24h,
                    "completed": completed_tasks,
                    "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                },
                "reputation": {
                    "total_feedback": total_feedback,
                    "feedback_7d": feedback_7d,
                    "average_rating": round(avg_reputation, 2)
                },
                "payments": {
                    "total": total_payments,
                    "payments_30d": payments_30d
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get ecosystem health: {e}")
            raise
    
    async def get_category_insights(self) -> List[Dict[str, Any]]:
        """
        Get insights by agent category/capability
        
        Returns:
            List of category metrics
        """
        try:
            # Aggregate by capability
            pipeline = [
                {"$unwind": "$capabilities"},
                {"$group": {
                    "_id": "$capabilities",
                    "agent_count": {"$sum": 1},
                    "avg_reputation": {"$avg": "$reputation_score"},
                    "total_tasks": {"$sum": "$total_tasks"},
                    "avg_tasks_per_agent": {"$avg": "$total_tasks"}
                }},
                {"$sort": {"agent_count": -1}},
                {"$limit": 20}
            ]
            
            results = await self.agents_collection.aggregate(pipeline).to_list(length=20)
            
            insights = []
            for result in results:
                insights.append({
                    "category": result["_id"],
                    "agent_count": result["agent_count"],
                    "average_reputation": round(result["avg_reputation"] / 100, 2),
                    "total_tasks": result["total_tasks"],
                    "avg_tasks_per_agent": round(result["avg_tasks_per_agent"], 1)
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get category insights: {e}")
            raise
    
    async def get_trending_agents(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending agents based on recent activity and feedback
        
        Args:
            days: Number of days to analyze
            limit: Number of agents to return
        
        Returns:
            List of trending agents
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get agents with recent activity
            pipeline = [
                {"$match": {"updated_at": {"$gte": cutoff_date}, "is_active": True}},
                {"$lookup": {
                    "from": "tasks",
                    "let": {"agent_id": "$token_id"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {"$eq": ["$agent_id", "$$agent_id"]},
                            "created_at": {"$gte": cutoff_date}
                        }},
                        {"$group": {
                            "_id": None,
                            "recent_tasks": {"$sum": 1},
                            "completed": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}
                        }}
                    ],
                    "as": "recent_activity"
                }},
                {"$lookup": {
                    "from": "feedbacks",
                    "let": {"agent_id": "$token_id"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {"$eq": ["$agent_id", "$$agent_id"]},
                            "created_at": {"$gte": cutoff_date}
                        }},
                        {"$group": {
                            "_id": None,
                            "recent_feedback": {"$sum": 1},
                            "avg_recent_rating": {"$avg": "$rating"}
                        }}
                    ],
                    "as": "recent_feedback"
                }},
                {"$addFields": {
                    "recent_tasks": {"$ifNull": [{"$arrayElemAt": ["$recent_activity.recent_tasks", 0]}, 0]},
                    "recent_completed": {"$ifNull": [{"$arrayElemAt": ["$recent_activity.completed", 0]}, 0]},
                    "recent_feedback_count": {"$ifNull": [{"$arrayElemAt": ["$recent_feedback.recent_feedback", 0]}, 0]},
                    "recent_rating": {"$ifNull": [{"$arrayElemAt": ["$recent_feedback.avg_recent_rating", 0]}, 0]},
                    # Trending score: tasks + feedback + completion rate
                    "trending_score": {
                        "$add": [
                            {"$multiply": [{"$ifNull": [{"$arrayElemAt": ["$recent_activity.recent_tasks", 0]}, 0]}, 2]},
                            {"$multiply": [{"$ifNull": [{"$arrayElemAt": ["$recent_feedback.recent_feedback", 0]}, 0]}, 3]},
                            {"$multiply": [{"$ifNull": [{"$arrayElemAt": ["$recent_feedback.avg_recent_rating", 0]}, 0]}, 5]}
                        ]
                    }
                }},
                {"$match": {"trending_score": {"$gt": 0}}},
                {"$sort": {"trending_score": -1}},
                {"$limit": limit},
                {"$project": {
                    "token_id": 1,
                    "name": 1,
                    "description": 1,
                    "capabilities": 1,
                    "reputation_score": 1,
                    "recent_tasks": 1,
                    "recent_completed": 1,
                    "recent_feedback_count": 1,
                    "recent_rating": 1,
                    "trending_score": 1
                }}
            ]
            
            trending = await self.agents_collection.aggregate(pipeline).to_list(length=limit)
            
            # Clean up results
            for agent in trending:
                agent.pop("_id", None)
                agent["reputation"] = agent.pop("reputation_score", 0) / 100
                agent["recent_rating"] = round(agent.get("recent_rating", 0), 2)
            
            return trending
            
        except Exception as e:
            logger.error(f"Failed to get trending agents: {e}")
            raise
    
    def _calculate_health_score(
        self,
        total_agents: int,
        active_agents: int,
        recent_tasks: int,
        completion_rate: float,
        avg_reputation: float
    ) -> float:
        """
        Calculate ecosystem health score (0-100)
        
        Weighted scoring:
        - Active agents rate: 30%
        - Task activity: 25%
        - Completion rate: 25%
        - Average reputation: 20%
        """
        if total_agents == 0:
            return 0.0
        
        activity_score = (active_agents / total_agents) * 30
        task_score = min(recent_tasks / 100, 1.0) * 25  # Normalize to 100 tasks
        completion_score = completion_rate * 25
        reputation_score = (avg_reputation / 5.0) * 20
        
        health_score = activity_score + task_score + completion_score + reputation_score
        
        return round(health_score, 2)


analytics_service = AnalyticsService()

