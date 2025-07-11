"""
Test Internal LLM Integration and Fallback Functionality
Demonstrates the new multi-provider LLM client capabilities
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agent.config import Config
from agent.llm_client import LLMClient, LLMService

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_provider_detection():
    """Test automatic provider detection and availability"""
    print("\n" + "="*80)
    print("TESTING PROVIDER DETECTION AND AVAILABILITY")
    print("="*80)
    
    config = Config()
    
    async with LLMClient(config) as client:
        current_provider = client.get_current_provider()
        available_providers = client.get_available_providers()
        
        print(f"Current Provider: {current_provider}")
        print(f"Available Providers: {available_providers}")
        
        # Test provider availability
        for provider in ['openai', 'internal']:
            available = client._is_provider_available(provider)
            print(f"  {provider}: {'✅ Available' if available else '❌ Not configured'}")


async def test_provider_switching():
    """Test manual provider switching"""
    print("\n" + "="*80)
    print("TESTING MANUAL PROVIDER SWITCHING")
    print("="*80)
    
    config = Config()
    
    async with LLMClient(config) as client:
        original_provider = client.get_current_provider()
        print(f"Starting with provider: {original_provider}")
        
        # Try switching to each available provider
        for provider in client.get_available_providers():
            if provider != original_provider:
                print(f"\nAttempting to switch to: {provider}")
                success = await client.switch_provider(provider)
                if success:
                    print(f"✅ Successfully switched to {provider}")
                    current = client.get_current_provider()
                    print(f"Current provider confirmed: {current}")
                else:
                    print(f"❌ Failed to switch to {provider}")


async def test_llm_request_with_fallback():
    """Test LLM request with automatic fallback"""
    print("\n" + "="*80)
    print("TESTING LLM REQUEST WITH AUTOMATIC FALLBACK")
    print("="*80)
    
    config = Config()
    
    async with LLMClient(config) as client:
        # Test a simple request
        response = await client.generate_response(
            prompt="What is professional document generation?",
            system_message="You are a helpful assistant specializing in legal document creation.",
            max_tokens=100,
            temperature=0.3
        )
        
        print(f"Request successful: {response.success}")
        print(f"Model used: {response.model}")
        print(f"Current provider: {client.get_current_provider()}")
        
        if response.success:
            print(f"Response preview: {response.content[:200]}...")
        else:
            print(f"Error: {response.error}")


async def test_llm_service_integration():
    """Test high-level LLM service with multi-provider support"""
    print("\n" + "="*80)
    print("TESTING LLM SERVICE WITH MULTI-PROVIDER SUPPORT")
    print("="*80)
    
    config = Config()
    service = LLMService(config)
    
    try:
        # Test prompt analysis
        analysis = await service.analyze_prompt(
            "Generate a liquidation resolution for a technology company"
        )
        print(f"Prompt analysis successful: {bool(analysis)}")
        if analysis:
            print(f"Task type: {analysis.get('task_type', 'unknown')}")
            print(f"Document types: {analysis.get('document_types', [])}")
        
        # Test document generation
        context = {
            "company_name": "Tech Solutions Pty Ltd",
            "industry": "Technology",
            "liquidation_type": "Voluntary"
        }
        
        content = await service.generate_document_content(
            document_type="liquidation_resolution",
            context=context,
            organization="Harrison Legal Partners"
        )
        
        print(f"Document generation successful: {bool(content)}")
        if content:
            print(f"Generated content preview: {content[:200]}...")
            
    except Exception as e:
        print(f"LLM Service test failed: {e}")


def test_configuration_display():
    """Test configuration display with internal LLM settings"""
    print("\n" + "="*80)
    print("TESTING CONFIGURATION DISPLAY")
    print("="*80)
    
    config = Config()
    print(config)


async def main():
    """Run all tests"""
    print("INTERNAL LLM INTEGRATION TEST SUITE")
    print("="*80)
    print("Testing multi-provider LLM support with automatic fallback")
    
    # Test configuration display
    test_configuration_display()
    
    # Test provider detection
    await test_provider_detection()
    
    # Test provider switching
    await test_provider_switching()
    
    # Test LLM request with fallback
    await test_llm_request_with_fallback()
    
    # Test high-level service integration
    await test_llm_service_integration()
    
    print("\n" + "="*80)
    print("INTERNAL LLM INTEGRATION TESTS COMPLETED")
    print("="*80)
    print("\nTo use internal LLM:")
    print("1. Set INTERNAL_LLM_ENABLED=true in your .env file")
    print("2. Configure INTERNAL_LLM_API_BASE with your server URL")
    print("3. Set INTERNAL_LLM_API_KEY with your API key")
    print("4. Choose INTERNAL_LLM_MODEL (e.g., llama2-70b-chat)")
    print("5. Set PRIMARY_LLM_PROVIDER=internal to use as primary")
    print("6. AUTO_FALLBACK_ENABLED=true allows switching when primary fails")


if __name__ == "__main__":
    asyncio.run(main()) 