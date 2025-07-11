#!/usr/bin/env python3
"""
AI Agent System - Main Entry Point
Performs prompt-based tasks including web search, API integration, and PDF generation
"""

import asyncio
import logging
from pathlib import Path
from agent.ai_agent import AIAgent
from agent.config import Config

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('agent.log'),
            logging.StreamHandler()
        ]
    )

async def main():
    """Main entry point for the AI Agent system"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration
        config = Config()
        
        # Initialize AI Agent
        agent = AIAgent(config)
        
        logger.info("AI Agent System initialized successfully")
        
        # Example usage
        prompt = """
        As a Liquidity tester generate 5 PDF documents for liquidity notification 
        as a lawyer for various organizations. Validate and generate various types 
        of documents for different customers.
        """
        
        # Process the prompt
        result = await agent.process_prompt(prompt)
        print(f"Agent Result: {result}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 