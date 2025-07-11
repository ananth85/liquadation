#!/usr/bin/env python3
"""
Simple Test for Enhanced Document Generation System
"""

import asyncio
import os
from pathlib import Path

async def test_system():
    """Simple test of the enhanced system"""
    print("Testing Enhanced Document Generation System")
    print("=" * 50)
    
    # Check templates
    templates_dir = Path("templates/unique_templates")
    if templates_dir.exists():
        template_files = list(templates_dir.glob("liquidation_*.j2"))
        print(f"✅ Found {len(template_files)} template files")
    else:
        print("❌ Template directory not found")
        return
    
    # Test prompts
    test_prompts = [
        "Generate liquidation documents for a tech startup in Sydney",
        "Create liquidation papers for Melbourne construction company",
        "Need liquidation docs for a retail store in Brisbane"
    ]
    
    print("\nTesting document generation...")
    
    try:
        from enhanced_document_generator import EnhancedDocumentGenerator
        
        generator = EnhancedDocumentGenerator()
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\nTest {i}: {prompt}")
            
            result = await generator.generate_document_from_prompt(
                prompt, 
                output_filename=f"test_document_{i}"
            )
            
            if result["success"]:
                summary = result["summary"]
                print(f"   ✅ Generated: {summary['company_name']}")
                print(f"   Industry: {summary['industry']}")
                print(f"   Template: {summary['template'][:50]}...")
                print(f"   Data Source: {summary['data_source']}")
            else:
                print(f"   ❌ Failed: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_system()) 