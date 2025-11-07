"""
Rate limiting implementation using Redis
"""
import time
import logging
from typing import Tuple
import redis
from app.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("✅ Rate limiter connected to Redis")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, rate limiting disabled: {e}")
            self.redis_client = None
            self.enabled = False
    
    def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """
        Check if request is allowed under rate limits.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Tuple of (allowed: bool, message: str)
        """
        if not self.enabled:
            return True, "Rate limiting disabled"
        
        try:
            current_time = int(time.time())
            window_start = current_time - settings.RATE_LIMIT_WINDOW
            
            # User-specific rate limit
            user_key = f"ratelimit:user:{user_id}"
            
            # Remove old entries
            self.redis_client.zremrangebyscore(user_key, 0, window_start)
            
            # Count requests in current window
            user_count = self.redis_client.zcard(user_key)
            
            if user_count >= settings.RATE_LIMIT_PER_USER:
                return False, f"User rate limit exceeded: {settings.RATE_LIMIT_PER_USER} requests per minute"
            
            # Platform-wide rate limit
            platform_key = "ratelimit:platform"
            
            # Remove old entries
            self.redis_client.zremrangebyscore(platform_key, 0, window_start)
            
            # Count platform requests
            platform_count = self.redis_client.zcard(platform_key)
            
            if platform_count >= settings.RATE_LIMIT_PLATFORM:
                return False, f"Platform rate limit exceeded: {settings.RATE_LIMIT_PLATFORM} requests per minute"
            
            # Add current request
            request_id = f"{user_id}:{current_time}"
            self.redis_client.zadd(user_key, {request_id: current_time})
            self.redis_client.zadd(platform_key, {request_id: current_time})
            
            # Set expiry on keys
            self.redis_client.expire(user_key, settings.RATE_LIMIT_WINDOW * 2)
            self.redis_client.expire(platform_key, settings.RATE_LIMIT_WINDOW * 2)
            
            remaining = settings.RATE_LIMIT_PER_USER - user_count - 1
            return True, f"Request allowed ({remaining} remaining)"
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Fail open - allow request if rate limiter fails
            return True, "Rate limit check failed, allowing request"
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get current rate limit stats for user"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            current_time = int(time.time())
            window_start = current_time - settings.RATE_LIMIT_WINDOW
            
            user_key = f"ratelimit:user:{user_id}"
            platform_key = "ratelimit:platform"
            
            # Clean old entries
            self.redis_client.zremrangebyscore(user_key, 0, window_start)
            self.redis_client.zremrangebyscore(platform_key, 0, window_start)
            
            user_count = self.redis_client.zcard(user_key)
            platform_count = self.redis_client.zcard(platform_key)
            
            return {
                "enabled": True,
                "user_requests": user_count,
                "user_limit": settings.RATE_LIMIT_PER_USER,
                "user_remaining": max(0, settings.RATE_LIMIT_PER_USER - user_count),
                "platform_requests": platform_count,
                "platform_limit": settings.RATE_LIMIT_PLATFORM,
                "window_seconds": settings.RATE_LIMIT_WINDOW
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit stats: {e}")
            return {"enabled": True, "error": str(e)}

# Singleton instance
rate_limiter = RateLimiter()