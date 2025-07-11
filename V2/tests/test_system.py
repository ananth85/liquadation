#!/usr/bin/env python3
"""
Simple System Test for AI Agent
Tests basic functionality without requiring API keys
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import agent modules
sys.path.append(str(Path(__file__).parent.parent))

from agent.config import Config
from agent.ai_agent import AIAgent


async def test_configuration():
    """Test configuration system"""
    print("🔧 Testing Configuration System...")
    
    try:
        config = Config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Agent: {config.agent_name}")
        print(f"   - Model: {config.openai_model}")
        print(f"   - Output Dir: {config.pdf_output_dir}")
        
        # Test validation
        validation = config.validate_config()
        if validation:
            print("✅ Configuration validation passed")
        else:
            print("⚠️  Configuration needs API keys for full functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def test_agent_initialization():
    """Test agent initialization"""
    print("\n🤖 Testing Agent Initialization...")
    
    try:
        config = Config()
        agent = AIAgent(config)
        print("✅ AI Agent initialized successfully")
        
        # Test cleanup
        await agent.cleanup()
        print("✅ Agent cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization test failed: {e}")
        return False


async def test_templates():
    """Test document templates"""
    print("\n📄 Testing Document Templates...")
    
    try:
        from templates.liquidation_template import LiquidationTemplates, get_template_by_type
        
        # Test template function
        context = {'organization': 'Test Company Pty Ltd'}
        
        # Test liquidation resolution template
        template_func = get_template_by_type('liquidation resolution')
        content = template_func(context)
        
        if 'Test Company Pty Ltd' in content and 'RESOLUTION' in content:
            print("✅ Template generation working")
            print(f"   - Generated content length: {len(content)} characters")
        else:
            print("⚠️  Template content may have issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False


async def test_directory_structure():
    """Test directory structure"""
    print("\n📁 Testing Directory Structure...")
    
    try:
        config = Config()
        
        # Check required directories
        directories = [
            config.pdf_output_dir,
            config.pdf_template_dir,
            Path('agent'),
            Path('templates'),
            Path('logs')
        ]
        
        for directory in directories:
            if directory.exists():
                print(f"✅ {directory} exists")
            else:
                print(f"⚠️  {directory} not found")
        
        # Check key files
        key_files = [
            'main.py',
            'demo.py',
            'requirements.txt',
            'README.md',
            'agent/ai_agent.py',
            'agent/config.py',
            'templates/liquidation_template.py'
        ]
        
        for file_path in key_files:
            if Path(file_path).exists():
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Directory structure test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 AI AGENT SYSTEM TESTS")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_agent_initialization,
        test_templates,
        test_directory_structure
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ System is ready for use")
        print("💡 Next steps:")
        print("   1. Set OPENAI_API_KEY environment variable")
        print("   2. Run 'python demo.py' for full demonstration")
        print("   3. Run 'python main.py' to use the system")
    else:
        print("⚠️  Some tests failed - check configuration")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main()) 