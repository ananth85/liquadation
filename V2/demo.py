#!/usr/bin/env python3
"""
AI Agent System Demo
Demonstrates the capabilities of the AI agent system
"""

import asyncio
import logging
import json
from pathlib import Path
from agent.ai_agent import AIAgent
from agent.config import Config

# Setup logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_liquidation_documents():
    """Demo: Generate Australian liquidation documents"""
    print("\n" + "="*80)
    print("DEMO 1: AUSTRALIAN LIQUIDATION DOCUMENT GENERATION")
    print("="*80)
    
    config = Config()
    agent = AIAgent(config)
    
    prompt = """
    As a Liquidity tester generate 5 PDF documents for liquidity notification 
    as a lawyer for various organizations:
    
    1. Tech Solutions Pty Ltd - Software company
    2. Manufacturing Corp Australia - Industrial manufacturer  
    3. Retail Enterprises Ltd - Retail chain
    4. Construction Services Pty Ltd - Building contractor
    5. Financial Advisors Australia - Professional services
    
    Generate complete liquidation documentation including resolutions, 
    creditor notifications, and director statements for each organization.
    Ensure Australian Corporations Act 2001 compliance.
    """
    
    print(f"Processing prompt: {prompt[:100]}...")
    
    try:
        result = await agent.process_prompt(prompt)
        
        print(f"\n✅ Processing completed successfully!")
        print(f"⏱️  Total execution time: {result.total_execution_time:.2f} seconds")
        
        if result.analysis:
            print(f"\n📋 Analysis:")
            print(f"   - Task Type: {result.analysis.get('task_type', 'N/A')}")
            print(f"   - Complexity: {result.analysis.get('complexity', 'N/A')}")
            print(f"   - Organizations: {len(result.analysis.get('organizations', []))}")
        
        if result.generated_documents:
            docs = result.generated_documents
            print(f"\n📄 Documents Generated:")
            print(f"   - Total Documents: {docs.get('total_generated', 0)}")
            print(f"   - Successful PDFs: {docs.get('successful_pdfs', 0)}")
            
            # List generated files
            print(f"\n📁 Generated Files:")
            for i, doc in enumerate(docs.get('documents', [])[:5], 1):
                file_path = doc.get('file_path')
                org = doc.get('organization', 'Unknown')
                doc_type = doc.get('document_type', 'Unknown')
                print(f"   {i}. {org} - {doc_type}")
                if file_path:
                    print(f"      📁 {file_path}")
        
        # Generate summary report
        summary = await agent.generate_summary_report(result)
        print(f"\n📊 EXECUTION SUMMARY:")
        print("-" * 80)
        print(summary)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo 1 failed: {e}")


async def demo_web_search_integration():
    """Demo: Web search with document generation"""
    print("\n" + "="*80)
    print("DEMO 2: WEB SEARCH + DOCUMENT GENERATION")
    print("="*80)
    
    config = Config()
    agent = AIAgent(config)
    
    prompt = """
    Research the latest Australian liquidation procedures and ASIC guidelines 
    from 2024, then generate a comprehensive liquidator appointment notice 
    for "Digital Innovations Pty Ltd" that incorporates the most current 
    regulatory requirements and compliance standards.
    """
    
    print(f"Processing research prompt...")
    
    try:
        result = await agent.process_prompt(prompt)
        
        print(f"\n✅ Research and generation completed!")
        print(f"⏱️  Total execution time: {result.total_execution_time:.2f} seconds")
        
        if result.search_results:
            search = result.search_results
            print(f"\n🔍 Search Results:")
            print(f"   - Successful searches: {search.get('successful_searches', 0)}")
            print(f"   - Total results found: {search.get('total_results', 0)}")
            
            # Show some search snippets
            results = search.get('results', {})
            for query, response in list(results.items())[:2]:
                if response.success and response.results:
                    print(f"\n   Query: '{query}'")
                    for result_item in response.results[:2]:
                        print(f"   • {result_item.title[:60]}...")
        
        if result.generated_documents:
            docs = result.generated_documents
            print(f"\n📄 Research-Based Documents:")
            print(f"   - Documents incorporating search data: {docs.get('total_generated', 0)}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo 2 failed: {e}")


async def demo_multiple_document_types():
    """Demo: Generate multiple document types"""
    print("\n" + "="*80)
    print("DEMO 3: MULTIPLE DOCUMENT TYPES")
    print("="*80)
    
    config = Config()
    agent = AIAgent(config)
    
    prompt = """
    For "Global Enterprises Pty Ltd" generate the complete liquidation package:
    
    1. Liquidation Resolution
    2. Creditor Notification Letter  
    3. Liquidator Appointment Notice
    4. Director's Statement as to Affairs
    5. Asset Realization Notice
    
    Ensure all documents are interconnected and reference each other appropriately.
    Include specific Australian legal clauses and compliance requirements.
    """
    
    print(f"Generating complete liquidation package...")
    
    try:
        result = await agent.process_prompt(prompt)
        
        print(f"\n✅ Complete package generated!")
        print(f"⏱️  Total execution time: {result.total_execution_time:.2f} seconds")
        
        if result.generated_documents:
            docs = result.generated_documents
            print(f"\n📋 Document Package:")
            
            for i, doc in enumerate(docs.get('documents', []), 1):
                doc_type = doc.get('document_type', 'Unknown')
                validation = doc.get('validation', {})
                is_valid = validation.get('valid', True)
                status = "✅ Valid" if is_valid else "⚠️  Issues"
                
                print(f"   {i}. {doc_type} - {status}")
                
                if not is_valid and validation.get('issues'):
                    for issue in validation['issues'][:2]:
                        print(f"      ⚠️  {issue}")
        
        # Show task breakdown
        if result.task_results:
            print(f"\n🔧 Task Execution:")
            for task in result.task_results:
                status = "✅" if task.success else "❌"
                time_str = f"{task.execution_time:.2f}s" if task.execution_time else "N/A"
                print(f"   {status} {task.task_type} ({time_str})")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo 3 failed: {e}")


async def demo_configuration_showcase():
    """Demo: Show configuration and capabilities"""
    print("\n" + "="*80)
    print("DEMO 4: SYSTEM CONFIGURATION & CAPABILITIES")
    print("="*80)
    
    config = Config()
    
    print("🔧 System Configuration:")
    print(config)
    
    print(f"\n🚀 System Capabilities:")
    print(f"   ✅ LLM Integration (OpenAI GPT-4.1)")
    print(f"   ✅ Multi-engine web search")
    print(f"   ✅ Professional PDF generation")
    print(f"   ✅ Australian legal templates")
    print(f"   ✅ Document validation")
    print(f"   ✅ Async processing")
    print(f"   ✅ Security & memory cleanup")
    
    validation_result = config.validate_config()
    status = "✅ Ready" if validation_result else "⚠️  Configuration needed"
    print(f"\n🔍 Configuration Status: {status}")
    
    # Show output directory contents
    output_dir = config.pdf_output_dir
    if output_dir.exists():
        files = list(output_dir.glob("*"))
        print(f"\n📁 Output Directory ({output_dir}):")
        if files:
            for file in files[-5:]:  # Show last 5 files
                size = file.stat().st_size if file.is_file() else 0
                print(f"   📄 {file.name} ({size:,} bytes)")
        else:
            print("   (Empty - ready for new documents)")


async def main():
    """Run all demos"""
    print("🤖 AI AGENT SYSTEM DEMONSTRATION")
    print("🎯 Showcasing document generation, web search, and PDF creation")
    print("\nNote: Ensure OPENAI_API_KEY is configured for full functionality")
    
    try:
        # Run configuration demo first
        await demo_configuration_showcase()
        
        # Run document generation demos
        await demo_liquidation_documents()
        await demo_web_search_integration()
        await demo_multiple_document_types()
        
        print("\n" + "="*80)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n📋 Next Steps:")
        print("   1. Check the 'output' directory for generated documents")
        print("   2. Review the agent.log file for detailed execution logs")
        print("   3. Customize prompts for your specific use cases")
        print("   4. Integrate the agent into your applications")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo suite failed: {e}")
        logger.error(f"Demo suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 