from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import redis
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)

class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str, cache_timeout: int = 300):
        super().__init__(app)
        self.redis = redis.from_url(redis_url)
        self.cache_timeout = cache_timeout  # Default 5 minutes

    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Generate cache key based on request path and query parameters
        cache_key = self._generate_cache_key(request)

        # Check if response is in cache
        cached_response = self.redis.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit: {request.url.path}")
            response = json.loads(cached_response)
            return Response(
                content=response["content"],
                media_type=response["media_type"],
                status_code=response["status_code"]
            )

        # If not cached, proceed with request
        response = await call_next(request)

        # Cache the response if it's successful
        if response.status_code == 200:
            self._cache_response(cache_key, response)

        return response

    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key based on request details"""
        path = request.url.path
        query = request.url.query
        return f"cache:{path}:{query}"

    def _cache_response(self, cache_key: str, response: Response):
        """Cache the response in Redis"""
        try:
            # Convert response to JSON
            cached_data = {
                "content": response.body.decode("utf-8"),
                "media_type": response.media_type,
                "status_code": response.status_code
            }
            
            # Store in Redis with timeout
            self.redis.setex(
                cache_key,
                self.cache_timeout,
                json.dumps(cached_data)
            )
            
            logger.info(f"Cached response for {cache_key} - TTL: {self.cache_timeout}s")
            
        except Exception as e:
            logger.error(f"Error caching response: {str(e)}")
