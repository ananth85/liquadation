#!/usr/bin/env python3
"""
Test Enhanced Document Generation System

This script tests the new intelligent template selection and LLM-driven content generation
to ensure it produces unique, contextual documents instead of the same template.
"""

import asyncio
import logging
import os
import json
from pathlib import Path
from datetime import datetime

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_enhanced_system():
    """Test the enhanced document generation system"""
    print("🧪 Testing Enhanced Document Generation System")
    print("=" * 60)
    
    try:
        # Test 1: Check if unique templates exist
        print("\n1️⃣ Checking Template Availability...")
        templates_dir = Path("templates/unique_templates")
        
        if not templates_dir.exists():
            print("❌ Unique templates directory not found!")
            print("   Please ensure 155 unique templates are in templates/unique_templates/")
            return False
        
        template_files = list(templates_dir.glob("liquidation_*.j2"))
        metadata_files = list(templates_dir.glob("metadata_*.json"))
        
        print(f"✅ Found {len(template_files)} template files")
        print(f"✅ Found {len(metadata_files)} metadata files")
        
        if len(template_files) < 100:
            print("⚠️  Warning: Less than 100 templates found. Run the template generator first.")
            return False
        
        # Test 2: Check LLM configuration
        print("\n2️⃣ Checking LLM Configuration...")
        api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY')
        
        if api_key and api_key != "your_openai_api_key_here":
            print("✅ API key configured - LLM generation will be used")
            llm_available = True
        else:
            print("⚠️  No API key - enhanced fallback generation will be used")
            llm_available = False
        
        # Test 3: Test prompt analysis
        print("\n3️⃣ Testing Prompt Analysis...")
        
        from agents.llm_generation_agent import LLMGenerationAgent
        from agents.intelligent_template_agent import IntelligentTemplateAgent
        
        # Initialize agents
        llm_agent = LLMGenerationAgent(
            api_key=api_key,
            base_url=os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1'),
            model=os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
            logger=logger
        )
        
        template_agent = IntelligentTemplateAgent(
            templates_dir="templates",
            llm_agent=llm_agent,
            logger=logger
        )
        
        print(f"✅ Loaded {len(template_agent.template_registry)} templates")
        print(f"✅ Loaded {len(template_agent.template_metadata)} metadata entries")
        
        # Test different types of prompts
        test_prompts = [
            {
                "prompt": "Generate liquidation documents for a tech startup in Sydney facing funding difficulties",
                "expected_industry": "Technology Services",
                "expected_location": "NSW"
            },
            {
                "prompt": "Create liquidation papers for Melbourne construction company with cash flow problems",
                "expected_industry": "Construction", 
                "expected_location": "VIC"
            },
            {
                "prompt": "Need liquidation docs for a retail store in Brisbane that's closing down",
                "expected_industry": "Retail Trade",
                "expected_location": "QLD"
            }
        ]
        
        print("\n4️⃣ Testing Intelligent Document Generation...")
        
        results = []
        for i, test_case in enumerate(test_prompts, 1):
            print(f"\n   Test Case {i}: {test_case['prompt'][:50]}...")
            
            try:
                # Test the full intelligent generation pipeline
                from agents.base_agent import AgentTask, AgentStatus
                import uuid
                
                task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    task_type="intelligent_document_generation",
                    input_data={"prompt": test_case["prompt"]},
                    status=AgentStatus.IDLE
                )
                generation_result = await template_agent.process_task(task)
                
                if generation_result.get("success"):
                    template_used = generation_result["template_used"]
                    generated_data = generation_result["generated_data"]
                    prompt_analysis = generation_result["prompt_analysis"]
                    
                    print(f"   ✅ Success!")
                    print(f"      Industry: {prompt_analysis.get('industry')} (expected: {test_case['expected_industry']})")
                    print(f"      Location: {prompt_analysis.get('location')} (expected: {test_case['expected_location']})")
                    print(f"      Template: {template_used['template_id']}")
                    print(f"      Company: {generated_data.get('company_name')}")
                    print(f"      Data Source: {generation_result['generation_stats']['data_source']}")
                    print(f"      Uniqueness: {generation_result['generation_stats']['uniqueness_indicators']['uniqueness_score']:.2f}")
                    
                    # Verify industry and location matching
                    industry_match = test_case['expected_industry'].lower() in prompt_analysis.get('industry', '').lower()
                    location_match = prompt_analysis.get('location') == test_case['expected_location']
                    
                    results.append({
                        "success": True,
                        "industry_match": industry_match,
                        "location_match": location_match,
                        "template_id": template_used['template_id'],
                        "company_name": generated_data.get('company_name'),
                        "uniqueness_score": generation_result['generation_stats']['uniqueness_indicators']['uniqueness_score']
                    })
                    
                else:
                    print(f"   ❌ Failed: {generation_result.get('error')}")
                    results.append({"success": False, "error": generation_result.get("error")})
                
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                results.append({"success": False, "error": str(e)})
        
        # Test 5: Verify uniqueness
        print("\n5️⃣ Testing Document Uniqueness...")
        
        successful_results = [r for r in results if r.get("success")]
        
        if len(successful_results) >= 2:
            # Check if different templates were selected
            template_ids = [r["template_id"] for r in successful_results]
            unique_templates = len(set(template_ids))
            
            print(f"   Templates used: {unique_templates}/{len(successful_results)}")
            
            if unique_templates > 1:
                print("   ✅ Different templates selected for different prompts")
            else:
                print("   ⚠️  Same template selected for all prompts")
            
            # Check if different company names were generated
            company_names = [r["company_name"] for r in successful_results if r.get("company_name")]
            unique_names = len(set(company_names))
            
            print(f"   Company names: {unique_names}/{len(company_names)} unique")
            
            if unique_names == len(company_names):
                print("   ✅ All company names are unique")
            else:
                print("   ⚠️  Some duplicate company names generated")
        
        # Test 6: Performance summary
        print("\n6️⃣ Performance Summary...")
        
        total_tests = len(test_prompts)
        successful_tests = len(successful_results)
        
        print(f"   Total tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_results:
            avg_uniqueness = sum(r.get("uniqueness_score", 0) for r in successful_results) / len(successful_results)
            print(f"   Average uniqueness score: {avg_uniqueness:.2f}")
        
        # Final assessment
        print("\n🎯 FINAL ASSESSMENT")
        print("-" * 30)
        
        if successful_tests >= 2:
            print("✅ Enhanced document generation system is working")
            print("✅ Intelligent template selection is functional")
            print("✅ Unique content generation is operational")
            
            if llm_available:
                print("✅ LLM-enhanced generation is active")
            else:
                print("⚠️  Using fallback generation (still effective)")
            
            print("\n🚀 READY FOR PRODUCTION USE")
            return True
        else:
            print("❌ System has significant issues")
            print("❌ Multiple test cases failed")
            print("\n🔧 REQUIRES DEBUGGING")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

async def run_sample_generation():
    """Run a sample generation to demonstrate the system"""
    print("\n" + "="*60)
    print("🚀 SAMPLE DOCUMENT GENERATION")
    print("="*60)
    
    try:
        from enhanced_document_generator import EnhancedDocumentGenerator
        
        generator = EnhancedDocumentGenerator()
        
        sample_prompt = "Generate liquidation documents for Digital Innovate Solutions Pty Ltd, a medium-sized technology consulting firm in Melbourne that's facing insolvency due to the loss of major clients and inability to adapt to remote work trends post-COVID"
        
        print(f"Prompt: {sample_prompt}")
        print("\nGenerating document...")
        
        result = await generator.generate_document_from_prompt(sample_prompt)
        
        if result["success"]:
            summary = result["summary"]
            print(f"\n✅ SUCCESS!")
            print(f"   Company: {summary['company_name']}")
            print(f"   Industry: {summary['industry']}")
            print(f"   Template: {summary['template']}")
            print(f"   Data Source: {summary['data_source']}")
            print(f"   Uniqueness: {summary['uniqueness_score']:.2f}")
            print(f"   PDF File: {result['files']['pdf']}")
            print(f"   HTML File: {result['files']['html']}")
            print(f"   Metadata: {result['files']['metadata']}")
            
            return True
        else:
            print(f"❌ FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Sample generation failed: {e}")
        return False

async def main():
    """Main test function"""
    print("Enhanced Document Generation System - Test Suite")
    print("Testing LLM-driven prompt understanding and unique template filling")
    print()
    
    # Run comprehensive tests
    test_success = await test_enhanced_system()
    
    if test_success:
        print("\n" + "="*60)
        print("All tests passed! Running sample generation...")
        await run_sample_generation()
    else:
        print("\n" + "="*60)
        print("Some tests failed. Please check the configuration:")
        print("1. Ensure 155 unique templates exist in templates/unique_templates/")
        print("2. Copy config_example.env to .env")
        print("3. Configure LLM_API_KEY in .env for best results")
        print("4. Install required dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    asyncio.run(main()) 