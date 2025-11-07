"""
Smart GTM Agent - Main agent implementation
FIXED: Pass company_url to SearchScraper
"""
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sentient_agent_framework import AbstractAgent, Session, Query, ResponseHandler
from app.config import settings
from app.core import normalize_url, is_valid_url, extract_company_name, rate_limiter, cache_manager
from app.services import smartcrawler_service, searchscraper_service
from app.agent.handlers import AnalysisHandlers

logger = logging.getLogger(__name__)

class SmartGTMAgent(AbstractAgent):
    """
    Smart GTM Agent - AI-powered Go-To-Market Strategy Assistant
    
    Compliant with Sentient Agent Framework for lightning-fast market 
    intelligence & GTM execution.
    """
    
    def __init__(self, name: str = "Smart GTM Agent"):
        super().__init__(name)
        
        # Create thread pool executor
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Initialize handlers
        self.handlers = AnalysisHandlers(self.executor)
        
        logger.info(f"✅ {name} initialized successfully")
    
    async def _run_with_keepalive(self, func, response_handler, status_key, *args):
        """Run a blocking function with periodic keepalive messages"""
        loop = asyncio.get_event_loop()
        
        # Create the main task
        task = loop.run_in_executor(self.executor, func, *args)
        
        # Create keepalive task
        async def send_keepalive():
            counter = 0
            while not task.done():
                await asyncio.sleep(settings.KEEPALIVE_INTERVAL)
                if not task.done():
                    counter += 1
                    await response_handler.emit_text_block(
                        f"{status_key}_KEEPALIVE_{counter}",
                        f"⏳ Still processing {status_key.lower()}... ({counter * settings.KEEPALIVE_INTERVAL}s elapsed)\n"
                    )
        
        # Run both tasks concurrently
        keepalive_task = asyncio.create_task(send_keepalive())
        
        try:
            result = await task
            keepalive_task.cancel()
            return result
        except Exception as e:
            keepalive_task.cancel()
            raise e
    
    async def assist(self, session: Session, query: Query, response_handler: ResponseHandler):
        """
        Main entry point for the GTM agent.
        
        Expected query format:
        - "https://example.com" (defaults to research)
        - "https://example.com | research"
        - "www.example.com | go-to-market"
        - "example.com | channel"
        """
        try:
            # Parse query
            prompt_parts = query.prompt.strip().split('|')
            raw_url = prompt_parts[0].strip()
            
            # Normalize and validate URL
            company_url = normalize_url(raw_url)
            
            if not company_url or not is_valid_url(company_url):
                await response_handler.emit_error(
                    error_code=400,
                    error_data={
                        "message": f"Invalid URL: '{raw_url}'. Please provide a valid URL like: https://example.com, www.example.com, or example.com"
                    }
                )
                await response_handler.complete()
                return
            
            # Extract feature
            if len(prompt_parts) > 1:
                feature = prompt_parts[1].strip().lower()
            else:
                feature = getattr(query, 'feature', 'research').lower()
            
            # Validate feature
            if feature not in ['research', 'go-to-market', 'channel']:
                await response_handler.emit_error(
                    error_code=400,
                    error_data={
                        "message": f"Invalid feature '{feature}'. Must be one of: research, go-to-market, channel"
                    }
                )
                await response_handler.complete()
                return
            
            # Extract user ID for rate limiting (from session or use a default)
            user_id = getattr(session, 'user_id', None) or getattr(query, 'user_id', 'default_user')
            
            # Check rate limit
            allowed, rate_msg = rate_limiter.check_rate_limit(user_id)
            if not allowed:
                await response_handler.emit_error(
                    error_code=429,
                    error_data={"message": f"⚠️ {rate_msg}. Please wait before making more requests."}
                )
                await response_handler.complete()
                return
            
            logger.info(f"Rate limit check: {rate_msg}")
            
            # Check cache
            cached_result = cache_manager.get(company_url, feature)
            if cached_result:
                await response_handler.emit_text_block(
                    "CACHE_HIT",
                    "✅ Found cached result! Returning stored analysis...\n\n"
                )
                
                # Stream cached result
                final_response_stream = response_handler.create_text_stream("FINAL_RESPONSE")
                cached_data = cached_result.get("data", {}).get("analysis", "")
                
                for i in range(0, len(cached_data), settings.STREAM_CHUNK_SIZE):
                    await final_response_stream.emit_chunk(cached_data[i:i + settings.STREAM_CHUNK_SIZE])
                    await asyncio.sleep(0.01)
                
                await final_response_stream.complete()
                
            
                
                await response_handler.complete()
                return
            
            # Extract company name
            company_name = extract_company_name(company_url)
            
            # Start fresh analysis
            await response_handler.emit_text_block(
                "ANALYSIS_START",
                f"🚀 Starting {feature.upper()} analysis for {company_name}...\n\n"
                f"📍 URL: {company_url}\n"
                "⏳ This process may take 2-5 minutes. Please wait...\n"
            )
            
            # Run data collection
            await response_handler.emit_text_block(
                "DATA_COLLECTION",
                "🕷️ Step 1/3: Running SmartCrawler for company data extraction...\n"
                "⏱️ Estimated time: 2-3 minutes\n"
            )
            
            try:
                # Run SmartCrawler with keepalive
                scrawler_result = await self._run_with_keepalive(
                    smartcrawler_service.crawl,
                    response_handler,
                    "SMARTCRAWLER",
                    company_url
                )
                
                await response_handler.emit_json(
                    "SMARTCRAWLER_COMPLETE",
                    {"status": "success", "data_length": len(scrawler_result)}
                )
                
                await response_handler.emit_text_block(
                    "COMPETITOR_SEARCH",
                    "🔍 Step 2/3: Running SearchScraper for competitor analysis...\n"
                    "⏱️ Estimated time: 1-2 minutes\n"
                )
                
                # ✅ FIXED: Pass BOTH scrawler_result AND company_url to SearchScraper
                search_result = await self._run_with_keepalive(
                    searchscraper_service.search_competitors,
                    response_handler,
                    "SEARCHSCRAPER",
                    scrawler_result,  # company_overview
                    company_url       # ✅ NOW PASSING THE URL!
                )
                
                await response_handler.emit_json(
                    "SEARCHSCRAPER_COMPLETE",
                    {"status": "success", "data_length": len(search_result)}
                )
                
                # Combine results
                combined_data = f"## 🕷️ Crawler Data:\n{scrawler_result}\n\n## 🔍 Scraper Data:\n{search_result}"
                
                # Process based on selected feature
                await response_handler.emit_text_block(
                    "AGENT_PROCESSING",
                    f"🤖 Step 3/3: Running {feature.upper()} analysis...\n"
                )
                
                # Create text stream for final response
                final_response_stream = response_handler.create_text_stream("FINAL_RESPONSE")
                
                # Collect full analysis for caching
                full_analysis = []
                
                # Process with appropriate analysis
                if feature == "research":
                    async for chunk in self.handlers.run_research_analysis(combined_data):
                        await final_response_stream.emit_chunk(chunk)
                        full_analysis.append(chunk)
                        
                elif feature == "go-to-market":
                    async for chunk in self.handlers.run_gtm_analysis(combined_data):
                        await final_response_stream.emit_chunk(chunk)
                        full_analysis.append(chunk)
                        
                elif feature == "channel":
                    async for chunk in self.handlers.run_channel_analysis(combined_data):
                        await final_response_stream.emit_chunk(chunk)
                        full_analysis.append(chunk)
                
                await final_response_stream.complete()
                
                # Cache the result
                full_analysis_text = "".join(full_analysis)
                cache_manager.set(
                    company_url,
                    feature,
                    {
                        "analysis": full_analysis_text,
                        "company_name": company_name,
                        "crawler_data_length": len(scrawler_result),
                        "search_data_length": len(search_result)
                    }
                )
                
        
                
            except Exception as e:
                logger.error(f"Error during processing: {e}", exc_info=True)
                raise
            
            await response_handler.complete()
            logger.info(f"✅ Analysis completed for {company_url}")
            
        except Exception as e:
            logger.error(f"Error in assist method: {e}", exc_info=True)
            await response_handler.emit_error(
                error_code=500,
                error_data={"message": f"An error occurred: {str(e)}"}
            )
            await response_handler.complete()
    
    def __del__(self):
        """Cleanup executor on agent destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)