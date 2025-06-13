from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.base import BaseHTTPMiddleware
import redis
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    limit: int = 100  # Default limit per period
    period: int = 60  # Default period in seconds
    prefix: str = "rate_limit"

    def get_key(self, client_id: str) -> str:
        return f"{self.prefix}:{client_id}"

class RateLimiter:
    def __init__(self, config: RateLimitConfig, redis_url: str):
        self.config = config
        self.redis = redis.from_url(redis_url)

    def _get_client_id(self, request: Request) -> str:
        # Use IP address as client identifier
        return request.client.host

    def _get_rate_limit_key(self, client_id: str) -> str:
        return self.config.get_key(client_id)

    def check_limit(self, request: Request) -> bool:
        client_id = self._get_client_id(request)
        key = self._get_rate_limit_key(client_id)

        # Check if key exists and get remaining time
        if self.redis.exists(key):
            remaining = self.redis.ttl(key)
            if remaining == -1:  # If no expiration set
                remaining = self.config.period
        else:
            remaining = self.config.period

        # Get current count
        count = int(self.redis.get(key) or 0)

        if count >= self.config.limit:
            reset_time = datetime.now() + timedelta(seconds=remaining)
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Too many requests",
                    "reset": reset_time.isoformat()
                }
            )

        # Increment count and set expiration
        self.redis.incr(key)
        self.redis.expire(key, self.config.period)

        return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config: RateLimitConfig, redis_url: str):
        super().__init__(app)
        self.limiter = RateLimiter(config, redis_url)

    async def dispatch(self, request: Request, call_next):
        try:
            # Check rate limit for non-static routes
            if not request.url.path.startswith('/static'):
                self.limiter.check_limit(request)

            response = await call_next(request)
            return response

        except HTTPException as e:
            logger.warning(f"Rate limit exceeded: {str(e)}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "message": e.detail.get("message", "Too many requests"),
                    "errors": {
                        "rate_limit": e.detail
                    }
                }
            )
