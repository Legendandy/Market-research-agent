"""
SmartCrawler Service - FIXED based on working code
"""
import json
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from scrapegraph_py import Client
from app.config import settings
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class SmartCrawlerService:
    """SmartCrawler wrapper service"""
    
    def __init__(self):
        """Initialize SmartCrawler client"""
        self.client = Client(api_key=settings.SMARTCRAWLER_API_KEY)
        logger.info("✅ SmartCrawler Service initialized")
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
    def crawl(self, url: str) -> str:
        """
        Extract structured company data using SmartCrawler.
        Fixed based on working code pattern.
        
        Args:
            url: Company website URL (normalized)
            
        Returns:
            Structured company information as markdown
        """
        try:
            schema = {
                "type": "object",
                "properties": {
                    "Overview": {"type": "string"},
                    "Founders": {"type": "array"},
                    "Funding": {"type": "array"},
                    "Industry": {"type": "string"},
                    "Market Size": {"type": "string"},
                    "Competitors": {"type": "array"},
                },
            }
            
            logger.info(f"[SmartCrawler] Starting crawl for: {url}")
            
            # Start crawl (matching working code - WITH cache_website parameter)
            crawl_response = self.client.crawl(
                url=url,
                prompt="Extract detailed company information",
                data_schema=schema,
                cache_website=True,  # Keep this from working code
                depth=settings.CRAWL_DEPTH,
                max_pages=settings.CRAWL_MAX_PAGES,
                same_domain_only=True,
            )
            
            # Get crawl ID
            crawl_id = crawl_response.get("id") or crawl_response.get("task_id")
            
            if not crawl_id:
                logger.error(f"No crawl ID in response: {crawl_response}")
                return f"❌ No crawl ID found. Please check URL ({url}) or API key."
            
            logger.info(f"[SmartCrawler] Crawl started with ID: {crawl_id}")
            
            # Poll for results (matching working code pattern - 60 attempts * 5 seconds = 5 minutes)
            max_attempts = 60
            
            for attempt in range(max_attempts):
                time.sleep(5)
                
                try:
                    result = self.client.get_crawl(crawl_id)
                    status = result.get("status")
                    
                    # Log every 30 seconds (every 6 attempts)
                    if attempt % 6 == 0:
                        logger.info(f"[SmartCrawler] Status: {status} ({5 * (attempt + 1)}s elapsed)")
                    
                    # Handle success
                    if status == "success" and result.get("result"):
                        logger.info("[SmartCrawler] ✅ Crawl completed successfully")
                        return self._process_crawl_result(result["result"])
                    
                    # Handle failure
                    elif status == "failed":
                        error_msg = result.get("error", "Unknown error")
                        logger.error(f"[SmartCrawler] Crawl failed: {error_msg}")
                        return f"❌ Crawl failed: {error_msg}"
                    
                    # Continue polling for other statuses (queued, processing, pending)
                    else:
                        continue
                        
                except Exception as poll_error:
                    logger.warning(f"[SmartCrawler] Polling error: {poll_error}")
                    if attempt == max_attempts - 1:
                        raise
                    continue
            
            # Timeout after all attempts
            logger.error("[SmartCrawler] Crawl timeout after 5 minutes")
            return "⏱️ Crawl timeout after 5 minutes. The website may be too large or slow."
            
        except Exception as e:
            logger.error(f"[SmartCrawler] Exception: {e}", exc_info=True)
            return f"❌ Exception during crawling: {str(e)}"
    
    def _process_crawl_result(self, result: dict) -> str:
        """
        Process and summarize crawl result.
        Matching working code pattern.
        """
        try:
            # Extract content from pages
            pages = result.get("pages", [])
            
            if pages:
                # Extract markdown from each page
                markdown_content = "\n\n".join(
                    p.get(
                        "markdown",
                        json.dumps(p.get("content", {}), indent=2, ensure_ascii=False)
                    )
                    for p in pages
                )
            else:
                # Fallback to entire result
                markdown_content = json.dumps(result, indent=2, ensure_ascii=False)
            
            # Limit content size
            if len(markdown_content) > settings.MAX_CONTENT_LENGTH:
                markdown_content = markdown_content[:settings.MAX_CONTENT_LENGTH] + "\n\n[Content truncated due to length]"
            
            # LLM summarize (matching working code prompt)
            prompt = (
                "You are a precise company research assistant.\n"
                "Summarize the following data into structured company insights.\n"
                "Required sections: Overview, Founders, Funding, Industry, Market Size, Competitors.\n"
                "Keep your response concise and well-structured.\n\n"
                f"DATA:\n{markdown_content}"
            )
            
            summary = llm_service.invoke(prompt)
            
            # Return the summary
            return summary
            
        except Exception as e:
            logger.error(f"Error processing crawl result: {e}", exc_info=True)
            return f"❌ Error processing crawl data: {str(e)}"

# Singleton instance
smartcrawler_service = SmartCrawlerService()