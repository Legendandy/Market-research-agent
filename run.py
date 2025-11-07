"""
Entry point for Smart GTM Agent
"""
import logging
from app.agent.gtm_agent import SmartGTMAgent
from sentient_agent_framework import DefaultServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Create agent instance
        agent = SmartGTMAgent(name="Smart GTM Agent")
        
        # Create server
        server = DefaultServer(agent)
        
        # Run server
        logger.info("🚀 Starting Smart GTM Agent server on port 8080...")
        server.run()
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}", exc_info=True)
        raise