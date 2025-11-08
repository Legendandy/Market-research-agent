"""
Smart GTM Agent - Main agent implementation with Natural Language Query Support
FIXED: Proper async/executor handling to prevent hanging between requests
"""
import logging
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from sentient_agent_framework import AbstractAgent, Session, Query, ResponseHandler
from app.config import settings
from app.core import normalize_url, is_valid_url, extract_company_name, rate_limiter, cache_manager
from app.services import smartcrawler_service, searchscraper_service
from app.agent.handlers import AnalysisHandlers
from app.core.query_parser import parse_query

logger = logging.getLogger(__name__)

class SmartGTMAgent(AbstractAgent):
    """
    Smart GTM Agent - AI-powered Go-To-Market Strategy Assistant
    
    Compliant with Sentient Agent Framework for lightning-fast market 
    intelligence & GTM execution.
    
    NOW SUPPORTS:
    - Natural language queries: "Give me channel analysis for example.com"
    - Legacy format: "example.com | channel"
    - Conversational: "I need go-to-market strategy for github.com"
    """
    
    def __init__(self, name: str = "Smart GTM Agent"):
        super().__init__(name)
        
        # Don't create a shared executor - we'll create per-request executors
        # to prevent thread leaks
        self.executor = None
        
        # Don't initialize handlers yet - we'll create them per request
        # to avoid sharing executor state
        self.handlers = None
        
        logger.info(f"✅ {name} initialized successfully with natural language support")
    
    async def _run_with_keepalive(self, executor, func, response_handler, status_key, timeout_seconds, *args):
        """
        Run a blocking function with periodic keepalive messages and timeout.
        
        Args:
            executor: ThreadPoolExecutor to use for this request
            func: Blocking function to run
            response_handler: Response handler for keepalive messages
            status_key: Key for status messages
            timeout_seconds: Maximum seconds to wait
            *args: Arguments to pass to func
        """
        loop = asyncio.get_event_loop()
        
        # Create the main task with timeout
        task = asyncio.create_task(
            asyncio.wait_for(
                loop.run_in_executor(executor, func, *args),
                timeout=timeout_seconds
            )
        )
        
        # Create keepalive task
        async def send_keepalive():
            counter = 0
            while not task.done():
                await asyncio.sleep(settings.KEEPALIVE_INTERVAL)
                if not task.done():
                    counter += 1
                    elapsed = counter * settings.KEEPALIVE_INTERVAL
                    await response_handler.emit_text_block(
                        f"{status_key}_KEEPALIVE_{counter}",
                        f"⏳ Still processing {status_key.lower()}... ({elapsed}s elapsed)\n"
                    )
        
        # Run both tasks concurrently
        keepalive_task = asyncio.create_task(send_keepalive())
        
        try:
            result = await task
            keepalive_task.cancel()
            return result
        except asyncio.TimeoutError:
            keepalive_task.cancel()
            logger.error(f"{status_key} operation timed out after {timeout_seconds}s")
            raise TimeoutError(f"{status_key} operation exceeded timeout")
        except Exception as e:
            keepalive_task.cancel()
            logger.error(f"{status_key} operation failed: {e}")
            raise
    
    async def assist(self, session: Session, query: Query, response_handler: ResponseHandler):
        """
        Main entry point for the GTM agent with natural language support.
        
        Supported query formats:
        1. Natural Language:
           - "Give me a channel analysis for example.com"
           - "I need go-to-market strategy for github.com"
           - "Research shopify.com for me"
        
        2. Legacy Format:
           - "example.com | research"
           - "https://example.com | go-to-market"
           - "www.example.com | channel"
        
        3. URL Only (defaults to research):
           - "https://example.com"
           - "example.com"
        """
        # Create a fresh executor for this request to prevent thread leaks
        request_executor = ThreadPoolExecutor(
            max_workers=3,
            thread_name_prefix=f"gtm_req_{id(query)}_"
        )
        
        # Create handlers for this request with its own executor
        request_handlers = AnalysisHandlers(request_executor)
        
        try:
            # Parse query using natural language parser
            raw_url, feature, error_message = parse_query(query.prompt)
            
            # If parsing failed, emit helpful error message
            if error_message:
                await response_handler.emit_text_block(
                    "PARSING_ERROR",
                    error_message
                )
                await response_handler.complete()
                return
            
            # Normalize and validate URL
            company_url = normalize_url(raw_url)
            
            if not company_url or not is_valid_url(company_url):
                await response_handler.emit_text_block(
                    "URL_VALIDATION_ERROR",
                    f"❌ **Invalid URL format: '{raw_url}'**\n\n"
                    "**Please provide a valid URL:**\n"
                    "✅ https://example.com\n"
                    "✅ www.example.com\n"
                    "✅ example.com\n\n"
                    "**Example requests:**\n"
                    "• \"Give me channel analysis for stripe.com\"\n"
                    "• \"I need go-to-market strategy for https://github.com\"\n"
                    "• \"Research shopify.com\""
                )
                await response_handler.complete()
                return
            
            # Extract user ID for rate limiting
            user_id = getattr(session, 'user_id', None) or getattr(query, 'user_id', 'default_user')
            
            # Check rate limit
            allowed, rate_msg = rate_limiter.check_rate_limit(user_id)
            if not allowed:
                await response_handler.emit_text_block(
                    "RATE_LIMIT_ERROR",
                    f"⚠️ **Rate Limit Exceeded**\n\n"
                    f"{rate_msg}\n\n"
                    f"**Please wait a moment before making more requests.**\n"
                    f"This helps ensure optimal performance for all users."
                )
                await response_handler.complete()
                return
            
            logger.info(f"✅ Parsed query - URL: {company_url}, Type: {feature}, {rate_msg}")
            
            # Check cache
            cached_result = cache_manager.get(company_url, feature)
            if cached_result:
                await response_handler.emit_text_block(
                    "CACHE_HIT",
                    "✅ **Found cached result!** Returning stored analysis...\n\n"
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
            
            # Start fresh analysis with user-friendly messages
            feature_emoji = {
                'research': '🔍',
                'go-to-market': '🚀',
                'channel': '📢'
            }
            
            feature_names = {
                'research': 'Market Research',
                'go-to-market': 'Go-To-Market Strategy',
                'channel': 'Channel Strategy'
            }
            
            await response_handler.emit_text_block(
                "ANALYSIS_START",
                f"{feature_emoji.get(feature, '🚀')} **Starting {feature_names.get(feature, feature.upper())} for {company_name}**\n\n"
                f"📍 **Website:** {company_url}\n"
                f"⏱️ **Estimated time:** 2-5 minutes\n\n"
                "I'll analyze the company website and gather competitive intelligence...\n"
            )
            
            # Run data collection with timeouts
            await response_handler.emit_text_block(
                "DATA_COLLECTION",
                "🕷️ **Step 1/3:** Crawling company website for data extraction...\n"
                "⏱️ *This may take 2-3 minutes*\n"
            )
            
            try:
                # Run SmartCrawler with keepalive and timeout (5 minutes max)
                scrawler_result = await self._run_with_keepalive(
                    request_executor,
                    smartcrawler_service.crawl,
                    response_handler,
                    "SMARTCRAWLER",
                    300,  # 5 minute timeout
                    company_url
                )
                
                await response_handler.emit_json(
                    "SMARTCRAWLER_COMPLETE",
                    {"status": "success", "data_length": len(scrawler_result)}
                )
                
                await response_handler.emit_text_block(
                    "COMPETITOR_SEARCH",
                    "🔍 **Step 2/3:** Searching for competitor intelligence...\n"
                    "⏱️ *This may take 1-2 minutes*\n"
                )
                
                # Run SearchScraper with keepalive and timeout (3 minutes max)
                search_result = await self._run_with_keepalive(
                    request_executor,
                    searchscraper_service.search_competitors,
                    response_handler,
                    "SEARCHSCRAPER",
                    180,  # 3 minute timeout
                    scrawler_result,
                    company_url
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
                    f"🤖 **Step 3/3:** Generating {feature_names.get(feature, feature)} analysis...\n"
                )
                
                # Create text stream for final response
                final_response_stream = response_handler.create_text_stream("FINAL_RESPONSE")
                
                # Collect full analysis for caching
                full_analysis = []
                
                # Process with appropriate analysis
                if feature == "research":
                    async for chunk in request_handlers.run_research_analysis(combined_data):
                        await final_response_stream.emit_chunk(chunk)
                        full_analysis.append(chunk)
                        
                elif feature == "go-to-market":
                    async for chunk in request_handlers.run_gtm_analysis(combined_data):
                        await final_response_stream.emit_chunk(chunk)
                        full_analysis.append(chunk)
                        
                elif feature == "channel":
                    async for chunk in request_handlers.run_channel_analysis(combined_data):
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
                
            except TimeoutError as e:
                logger.error(f"Timeout error: {e}")
                await response_handler.emit_text_block(
                    "TIMEOUT_ERROR",
                    f"⏱️ **Operation Timed Out**\n\n"
                    f"{str(e)}\n\n"
                    "**This can happen when:**\n"
                    "• The website is very large or slow to respond\n"
                    "• The website blocks automated crawling\n"
                    "• Network issues\n\n"
                    "**Please try again or try a different website.**"
                )
                await response_handler.complete()
                return
                
            except Exception as e:
                logger.error(f"Error during processing: {e}", exc_info=True)
                raise
            
            await response_handler.complete()
            logger.info(f"✅ Analysis completed for {company_url}")
            
        except Exception as e:
            logger.error(f"Error in assist method: {e}", exc_info=True)
            await response_handler.emit_text_block(
                "SYSTEM_ERROR",
                f"❌ **An unexpected error occurred:**\n\n"
                f"```\n{str(e)}\n```\n\n"
                "**Please try again or contact support if the issue persists.**"
            )
            await response_handler.complete()
        
        finally:
            # CRITICAL: Always cleanup the executor, even if errors occur
            request_executor.shutdown(wait=True, cancel_futures=True)
    
    def cleanup(self):
        """Explicit cleanup method (executor is per-request now)"""
        logger.info("✅ SmartGTMAgent cleanup called (no global executor to clean)")