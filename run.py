"""
Entry point for Smart GTM Agent with proper cleanup
"""
import logging
import signal
import sys
from app.agent.gtm_agent import SmartGTMAgent
from sentient_agent_framework import DefaultServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global agent reference for cleanup
agent = None

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logger.info("\n🛑 Received shutdown signal, cleaning up...")
    if agent:
        agent.cleanup()
    logger.info("✅ Cleanup complete, exiting")
    sys.exit(0)

if __name__ == "__main__":
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create agent instance
        agent = SmartGTMAgent(name="MarketMind AI")
        
        # Create server
        server = DefaultServer(agent)
        
        # Run server
        logger.info("🚀 Starting MarketMind AI Agent server on port 8080...")
        logger.info("💡 Press Ctrl+C to stop gracefully")
        server.run()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Keyboard interrupt, cleaning up...")
        if agent:
            agent.cleanup()
        logger.info("✅ Cleanup complete")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}", exc_info=True)
        if agent:
            agent.cleanup()
        raise