"""
Configuration settings for Smart GTM Agent
"""
import os
from dotenv import load_dotenv

load_dotenv("api.env")

class Settings:
    """Application settings"""
    
    # API Keys
    NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
    SMARTCRAWLER_API_KEY = os.getenv("SMARTCRAWLER_API_KEY")
    
    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Rate Limiting
    RATE_LIMIT_PER_USER = int(os.getenv("RATE_LIMIT_PER_USER", "3"))
    RATE_LIMIT_PLATFORM = int(os.getenv("RATE_LIMIT_PLATFORM", "200"))
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Caching
    CACHE_TTL_DAYS = int(os.getenv("CACHE_TTL_DAYS", "7"))
    CACHE_TTL_SECONDS = CACHE_TTL_DAYS * 24 * 60 * 60
    
    # SmartCrawler Settings
    CRAWL_DEPTH = 2
    CRAWL_MAX_PAGES = 5
    CRAWL_TIMEOUT = 300  # 5 minutes
    
    # Content Limits
    MAX_CONTENT_LENGTH = 10000
    MAX_SEARCH_DATA_LENGTH = 8000
    
    # Streaming
    STREAM_CHUNK_SIZE = 100
    KEEPALIVE_INTERVAL = 15  # seconds
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.NEBIUS_API_KEY:
            raise ValueError("NEBIUS_API_KEY is not set in environment")
        if not cls.SMARTCRAWLER_API_KEY:
            raise ValueError("SMARTCRAWLER_API_KEY is not set in environment")

# Validate on import
Settings.validate()

# Export singleton
settings = Settings()