"""
Error Tracking and Logging Service (Phase 3)
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback
import sys

from app.database import get_errors_collection, get_api_requests_collection

logger = logging.getLogger(__name__)


class ErrorTracker:
    """
    Error tracking service for monitoring and analyzing errors
    
    Features:
    - Error logging and aggregation
    - Stack trace capture
    - Error frequency tracking
    - Alert thresholds
    """
    
    def __init__(self):
        self._errors_collection = None
        self.error_count = 0
        self.alert_threshold = 10  # Alert after 10 errors of same type
        logger.info("✅ Error Tracker initialized")
    
    @property
    def errors_collection(self):
        if self._errors_collection is None:
            self._errors_collection = get_errors_collection()
        return self._errors_collection
    
    async def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error"
    ):
        """
        Track an error with context
        
        Args:
            error: Exception object
            context: Additional context (user, endpoint, params, etc.)
            severity: error, warning, critical
        """
        try:
            error_type = type(error).__name__
            error_message = str(error)
            
            # Get stack trace
            exc_type, exc_value, exc_traceback = sys.exc_info()
            stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            
            # Create error document
            error_doc = {
                "error_type": error_type,
                "error_message": error_message,
                "severity": severity,
                "stack_trace": stack_trace,
                "context": context or {},
                "timestamp": datetime.utcnow(),
                "resolved": False
            }
            
            # Save to database
            await self.errors_collection.insert_one(error_doc)
            
            # Check for error frequency
            await self._check_error_frequency(error_type)
            
            # Log error
            logger.error(f"[{severity.upper()}] {error_type}: {error_message}")
            
            self.error_count += 1
            
        except Exception as e:
            # Don't let error tracking break the app
            logger.error(f"Failed to track error: {e}")
    
    async def _check_error_frequency(self, error_type: str):
        """Check if error frequency exceeds threshold"""
        try:
            # Count occurrences in last hour
            from datetime import timedelta
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            count = await self.errors_collection.count_documents({
                "error_type": error_type,
                "timestamp": {"$gte": one_hour_ago},
                "resolved": False
            })
            
            if count >= self.alert_threshold:
                logger.critical(
                    f"🚨 ALERT: {error_type} occurred {count} times in the last hour!"
                )
                # TODO: Send notification (email, Slack, etc.)
            
        except Exception as e:
            logger.error(f"Failed to check error frequency: {e}")
    
    async def get_error_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for the last N hours"""
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            # Total errors
            total_errors = await self.errors_collection.count_documents({
                "timestamp": {"$gte": cutoff}
            })
            
            # Errors by type
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff}}},
                {"$group": {
                    "_id": "$error_type",
                    "count": {"$sum": 1},
                    "last_occurrence": {"$max": "$timestamp"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            errors_by_type = await self.errors_collection.aggregate(pipeline).to_list(length=10)
            
            # Errors by severity
            severity_pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff}}},
                {"$group": {
                    "_id": "$severity",
                    "count": {"$sum": 1}
                }}
            ]
            
            errors_by_severity = await self.errors_collection.aggregate(severity_pipeline).to_list(length=10)
            
            return {
                "period_hours": hours,
                "total_errors": total_errors,
                "errors_by_type": errors_by_type,
                "errors_by_severity": {
                    item["_id"]: item["count"] for item in errors_by_severity
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get error stats: {e}")
            raise
    
    async def get_recent_errors(self, limit: int = 50) -> list:
        """Get recent errors"""
        try:
            cursor = self.errors_collection.find().sort("timestamp", -1).limit(limit)
            errors = await cursor.to_list(length=limit)
            
            for error in errors:
                error.pop("_id", None)
                # Truncate stack trace for brevity
                if "stack_trace" in error and len(error["stack_trace"]) > 500:
                    error["stack_trace"] = error["stack_trace"][:500] + "..."
            
            return errors
            
        except Exception as e:
            logger.error(f"Failed to get recent errors: {e}")
            raise
    
    async def mark_resolved(self, error_id: str):
        """Mark an error as resolved"""
        try:
            from bson import ObjectId
            
            result = await self.errors_collection.update_one(
                {"_id": ObjectId(error_id)},
                {
                    "$set": {
                        "resolved": True,
                        "resolved_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to mark error as resolved: {e}")
            raise
    
    async def clear_old_errors(self, days: int = 30):
        """Clear errors older than N days"""
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            result = await self.errors_collection.delete_many({
                "timestamp": {"$lt": cutoff}
            })
            
            logger.info(f"✅ Cleared {result.deleted_count} old errors")
            
        except Exception as e:
            logger.error(f"Failed to clear old errors: {e}")
            raise


class RequestLogger:
    """Log API requests for monitoring and debugging"""
    
    def __init__(self):
        self._requests_collection = None
        logger.info("✅ Request Logger initialized")
    
    @property
    def requests_collection(self):
        if self._requests_collection is None:
            self._requests_collection = get_api_requests_collection()
        return self._requests_collection
    
    async def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: str,
        user_agent: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """Log an API request"""
        try:
            request_doc = {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "api_key_hash": api_key[:16] if api_key else None,  # Only store prefix
                "timestamp": datetime.utcnow()
            }
            
            await self.requests_collection.insert_one(request_doc)
            
        except Exception as e:
            # Don't break app if logging fails
            logger.error(f"Failed to log request: {e}")
    
    async def get_request_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get request statistics"""
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            # Total requests
            total_requests = await self.requests_collection.count_documents({
                "timestamp": {"$gte": cutoff}
            })
            
            # Requests by status code
            status_pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff}}},
                {"$group": {
                    "_id": "$status_code",
                    "count": {"$sum": 1}
                }}
            ]
            
            requests_by_status = await self.requests_collection.aggregate(status_pipeline).to_list(length=20)
            
            # Top endpoints
            endpoint_pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff}}},
                {"$group": {
                    "_id": "$path",
                    "count": {"$sum": 1},
                    "avg_duration": {"$avg": "$duration_ms"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            top_endpoints = await self.requests_collection.aggregate(endpoint_pipeline).to_list(length=10)
            
            # Average response time
            avg_duration_pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff}}},
                {"$group": {
                    "_id": None,
                    "avg_duration": {"$avg": "$duration_ms"}
                }}
            ]
            
            avg_duration_result = await self.requests_collection.aggregate(avg_duration_pipeline).to_list(length=1)
            avg_duration = avg_duration_result[0]["avg_duration"] if avg_duration_result else 0
            
            return {
                "period_hours": hours,
                "total_requests": total_requests,
                "requests_by_status": {
                    item["_id"]: item["count"] for item in requests_by_status
                },
                "top_endpoints": top_endpoints,
                "average_response_time_ms": round(avg_duration, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get request stats: {e}")
            raise


# Singleton instances
error_tracker = ErrorTracker()
request_logger = RequestLogger()

