"""
LLM Service for Smart GTM Agent
"""
import logging
from langchain_nebius import ChatNebius
from pydantic import SecretStr
from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """LLM Service wrapper"""
    
    def __init__(self):
        """Initialize LLM client"""
        self.llm = ChatNebius(
            model="NousResearch/Hermes-4-70B",
            api_key=SecretStr(settings.NEBIUS_API_KEY)
        )
        logger.info("✅ LLM Service initialized")
    
    def invoke(self, prompt: str) -> str:
        """
        Invoke LLM with prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            LLM response content
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"LLM invocation error: {e}", exc_info=True)
            raise

# Singleton instance
llm_service = LLMService()