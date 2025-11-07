"""
Response handlers for streaming analysis results
"""
import asyncio
import logging
from typing import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from app.services import llm_service
from app.config import settings
from app.prompts import RESEARCH_PROMPT_TEMPLATE, GTM_PROMPT_TEMPLATE, CHANNEL_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

class AnalysisHandlers:
    """Handlers for different analysis types"""
    
    def __init__(self, executor: ThreadPoolExecutor):
        """
        Initialize handlers.
        
        Args:
            executor: ThreadPoolExecutor for blocking operations
        """
        self.executor = executor
    
    async def run_research_analysis(self, context: str) -> AsyncIterator[str]:
        """Run research analysis and stream results"""
        try:
            prompt = RESEARCH_PROMPT_TEMPLATE.format(context=context)
            
            # Run LLM in executor
            loop = asyncio.get_event_loop()
            
            def _invoke():
                return llm_service.invoke(prompt)
            
            result = await loop.run_in_executor(self.executor, _invoke)
            
            # Stream the result in chunks
            for i in range(0, len(result), settings.STREAM_CHUNK_SIZE):
                yield result[i:i + settings.STREAM_CHUNK_SIZE]
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Research analysis error: {e}", exc_info=True)
            yield f"\n\n❌ Error in research analysis: {str(e)}"
    
    async def run_gtm_analysis(self, context: str) -> AsyncIterator[str]:
        """Run GTM analysis and stream results"""
        try:
            prompt = GTM_PROMPT_TEMPLATE.format(context=context)
            
            # Run LLM in executor
            loop = asyncio.get_event_loop()
            
            def _invoke():
                return llm_service.invoke(prompt)
            
            result = await loop.run_in_executor(self.executor, _invoke)
            
            # Stream the result in chunks
            for i in range(0, len(result), settings.STREAM_CHUNK_SIZE):
                yield result[i:i + settings.STREAM_CHUNK_SIZE]
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"GTM analysis error: {e}", exc_info=True)
            yield f"\n\n❌ Error in GTM analysis: {str(e)}"
    
    async def run_channel_analysis(self, context: str) -> AsyncIterator[str]:
        """Run channel analysis and stream results"""
        try:
            prompt = CHANNEL_PROMPT_TEMPLATE.format(context=context)
            
            # Run LLM in executor
            loop = asyncio.get_event_loop()
            
            def _invoke():
                return llm_service.invoke(prompt)
            
            result = await loop.run_in_executor(self.executor, _invoke)
            
            # Stream the result in chunks
            for i in range(0, len(result), settings.STREAM_CHUNK_SIZE):
                yield result[i:i + settings.STREAM_CHUNK_SIZE]
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Channel analysis error: {e}", exc_info=True)
            yield f"\n\n❌ Error in channel analysis: {str(e)}"