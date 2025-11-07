"""
Caching implementation using Redis
"""
import json
import logging
import hashlib
from typing import Optional, Any
import redis
from app.config import settings
from app.core.url_validator import extract_domain

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis-based cache manager"""
    
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
            logger.info("✅ Cache manager connected to Redis")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, caching disabled: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _generate_cache_key(self, url: str, feature: str) -> str:
        """
        Generate cache key for URL and feature combination.
        
        Args:
            url: Normalized company URL
            feature: Analysis feature (research, go-to-market, channel)
            
        Returns:
            Cache key string
        """
        # Use domain + feature for key to handle different protocols
        domain = extract_domain(url)
        key_content = f"{domain}:{feature}"
        
        # Hash for consistent length
        key_hash = hashlib.md5(key_content.encode()).hexdigest()
        
        return f"cache:analysis:{feature}:{key_hash}"
    
    def get(self, url: str, feature: str) -> Optional[dict]:
        """
        Get cached analysis result.
        
        Args:
            url: Company URL
            feature: Analysis feature
            
        Returns:
            Cached result dict or None
        """
        if not self.enabled:
            return None
        
        try:
            cache_key = self._generate_cache_key(url, feature)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"✅ Cache HIT for {url} ({feature})")
                return json.loads(cached_data)
            else:
                logger.info(f"❌ Cache MISS for {url} ({feature})")
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, url: str, feature: str, data: dict) -> bool:
        """
        Cache analysis result.
        
        Args:
            url: Company URL
            feature: Analysis feature
            data: Result data to cache
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            cache_key = self._generate_cache_key(url, feature)
            
            # Add metadata
            cache_data = {
                "url": url,
                "feature": feature,
                "data": data,
                "cached_at": int(redis.time.time()) if hasattr(redis, 'time') else 0
            }
            
            # Store with TTL
            self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL_SECONDS,
                json.dumps(cache_data)
            )
            
            logger.info(f"✅ Cached result for {url} ({feature})")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def invalidate(self, url: str, feature: Optional[str] = None) -> int:
        """
        Invalidate cache for URL.
        
        Args:
            url: Company URL
            feature: Specific feature to invalidate, or None for all
            
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            if feature:
                # Invalidate specific feature
                cache_key = self._generate_cache_key(url, feature)
                deleted = self.redis_client.delete(cache_key)
                logger.info(f"🗑️ Invalidated cache for {url} ({feature})")
                return deleted
            else:
                # Invalidate all features for this URL
                domain = extract_domain(url)
                pattern = f"cache:analysis:*:{domain}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"🗑️ Invalidated {deleted} cache entries for {url}")
                    return deleted
                return 0
                
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            # Get total cache keys
            cache_keys = self.redis_client.keys("cache:analysis:*")
            
            return {
                "enabled": True,
                "total_cached_items": len(cache_keys),
                "ttl_days": settings.CACHE_TTL_DAYS
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}

# Singleton instance
cache_manager = CacheManager()