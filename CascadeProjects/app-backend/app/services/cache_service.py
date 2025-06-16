from redis import Redis
from typing import Any, Optional
from app.core.config import settings
import json
from datetime import datetime, timedelta

class CacheService:
    def __init__(self):
        """
        Initialize Redis cache service
        """
        self.client = Redis.from_url(settings.REDIS_URL)
        self.default_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[Any]:
        """
        Get cached value
        
        Args:
            key: Cache key
            
        Returns:
            Optional[Any]: Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache value: {str(e)}")
            return None

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Optional expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            if not expire:
                expire = self.default_ttl
            
            self.client.set(key, json.dumps(value), ex=expire)
            return True
        except Exception as e:
            logger.error(f"Error setting cache value: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete cache value
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache value: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if key exists
        """
        try:
            return self.client.exists(key) == 1
        except Exception as e:
            logger.error(f"Error checking cache key: {str(e)}")
            return False

    async def clear(self, pattern: str = "*") -> bool:
        """
        Clear cache entries matching pattern
        
        Args:
            pattern: Pattern to match keys
            
        Returns:
            bool: True if successful
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get time to live for a cache key
        
        Args:
            key: Cache key
            
        Returns:
            Optional[int]: TTL in seconds or None if key doesn't exist
        """
        try:
            ttl = self.client.ttl(key)
            if ttl == -1:
                return None
            return ttl
        except Exception as e:
            logger.error(f"Error getting TTL: {str(e)}")
            return None
