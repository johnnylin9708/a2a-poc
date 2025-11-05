"""
Rate Limiting Middleware for API protection (Phase 3)
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm
    
    Limits requests per IP address or API key
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # In-memory storage (use Redis in production)
        self.minute_requests: Dict[str, list] = {}
        self.hour_requests: Dict[str, list] = {}
        
        logger.info(f"✅ Rate Limit Middleware initialized: {requests_per_minute}/min, {requests_per_hour}/hour")
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier (IP or API key)
        client_id = self._get_client_id(request)
        
        # Check rate limits
        now = datetime.utcnow()
        
        try:
            # Check minute limit
            self._check_rate_limit(
                client_id,
                now,
                self.minute_requests,
                timedelta(minutes=1),
                self.requests_per_minute,
                "minute"
            )
            
            # Check hour limit
            self._check_rate_limit(
                client_id,
                now,
                self.hour_requests,
                timedelta(hours=1),
                self.requests_per_hour,
                "hour"
            )
            
            # Record request
            self._record_request(client_id, now)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
            response.headers["X-RateLimit-Remaining-Minute"] = str(
                self._get_remaining(client_id, now, self.minute_requests, timedelta(minutes=1), self.requests_per_minute)
            )
            
            return response
            
        except HTTPException as e:
            logger.warning(f"Rate limit exceeded for {client_id}: {e.detail}")
            raise
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    def _check_rate_limit(
        self,
        client_id: str,
        now: datetime,
        storage: Dict[str, list],
        window: timedelta,
        limit: int,
        window_name: str
    ):
        """Check if client has exceeded rate limit"""
        if client_id not in storage:
            return
        
        # Remove old requests outside window
        cutoff = now - window
        storage[client_id] = [ts for ts in storage[client_id] if ts > cutoff]
        
        # Check limit
        if len(storage[client_id]) >= limit:
            retry_after = int((storage[client_id][0] - cutoff).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limit} requests per {window_name}",
                headers={"Retry-After": str(retry_after)}
            )
    
    def _record_request(self, client_id: str, now: datetime):
        """Record a request timestamp"""
        if client_id not in self.minute_requests:
            self.minute_requests[client_id] = []
        if client_id not in self.hour_requests:
            self.hour_requests[client_id] = []
        
        self.minute_requests[client_id].append(now)
        self.hour_requests[client_id].append(now)
    
    def _get_remaining(
        self,
        client_id: str,
        now: datetime,
        storage: Dict[str, list],
        window: timedelta,
        limit: int
    ) -> int:
        """Get remaining requests in window"""
        if client_id not in storage:
            return limit
        
        cutoff = now - window
        current_requests = [ts for ts in storage[client_id] if ts > cutoff]
        return max(0, limit - len(current_requests))


class APIKeyRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Enhanced rate limiting with API key tiers
    
    Different limits for different API key tiers:
    - Free: 60/min, 1000/hour
    - Basic: 120/min, 5000/hour
    - Pro: 300/min, 20000/hour
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        self.tier_limits = {
            "free": {"minute": 60, "hour": 1000},
            "basic": {"minute": 120, "hour": 5000},
            "pro": {"minute": 300, "hour": 20000}
        }
        
        # In-memory API key storage (use database in production)
        self.api_keys = {}
        
        self.requests: Dict[str, Dict[str, list]] = {}
        
        logger.info("✅ API Key Rate Limit Middleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        # Skip for public endpoints
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            # No API key, apply default free tier
            return await self._apply_rate_limit(request, call_next, "free", "anonymous")
        
        # Get tier for API key (default to free if not found)
        tier = self.api_keys.get(api_key, {}).get("tier", "free")
        
        return await self._apply_rate_limit(request, call_next, tier, api_key)
    
    async def _apply_rate_limit(self, request: Request, call_next, tier: str, client_id: str):
        """Apply rate limiting based on tier"""
        limits = self.tier_limits.get(tier, self.tier_limits["free"])
        now = datetime.utcnow()
        
        if client_id not in self.requests:
            self.requests[client_id] = {"minute": [], "hour": []}
        
        # Clean old requests
        minute_cutoff = now - timedelta(minutes=1)
        hour_cutoff = now - timedelta(hours=1)
        
        self.requests[client_id]["minute"] = [
            ts for ts in self.requests[client_id]["minute"] if ts > minute_cutoff
        ]
        self.requests[client_id]["hour"] = [
            ts for ts in self.requests[client_id]["hour"] if ts > hour_cutoff
        ]
        
        # Check limits
        if len(self.requests[client_id]["minute"]) >= limits["minute"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limits['minute']} requests per minute ({tier} tier)",
                headers={"Retry-After": "60"}
            )
        
        if len(self.requests[client_id]["hour"]) >= limits["hour"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limits['hour']} requests per hour ({tier} tier)",
                headers={"Retry-After": "3600"}
            )
        
        # Record request
        self.requests[client_id]["minute"].append(now)
        self.requests[client_id]["hour"].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Tier"] = tier
        response.headers["X-RateLimit-Limit-Minute"] = str(limits["minute"])
        response.headers["X-RateLimit-Limit-Hour"] = str(limits["hour"])
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            limits["minute"] - len(self.requests[client_id]["minute"])
        )
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            limits["hour"] - len(self.requests[client_id]["hour"])
        )
        
        return response

