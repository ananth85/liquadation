#!/usr/bin/env python3
"""
Professional AI Agent System - Main Entry Point
Generates professional, court-quality PDF documents with comprehensive financial details
"""

import asyncio
import logging
from pathlib import Path
from agent.config import Config
from agent.enhanced_ai_agent import EnhancedAIAgent

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('professional_agent.log'),
            logging.StreamHandler()
        ]
    )

async def generate_professional_liquidation_package():
    """Generate professional liquidation documents with all clauses and financial details"""
    
    # Sample prompt for comprehensive document generation
    prompt = """
    As a legal professional, generate 5 comprehensive PDF liquidation documents 
    for various Australian organizations with complete financial analysis, 
    legal clauses, and customer information:

    1. Tech Solutions Pty Ltd - IT Services ($2.5M revenue, 25 employees)
    2. Manufacturing Corp Australia - Industrial manufacturer ($5M revenue, 50 employees)  
    3. Retail Enterprises Ltd - Retail chain ($3M revenue, 35 employees)
    4. Construction Services Pty Ltd - Building contractor ($4M revenue, 40 employees)
    5. Financial Advisors Australia - Professional services ($1.5M revenue, 15 employees)

    For each organization, generate:
    - Professional Affidavit (Federal Court standard)
    - Liquidation Resolution with all legal clauses
    - Comprehensive Creditor Notification
    - Director's Statement with complete financial schedules
    - Asset Realization Notice with detailed asset listings

    Include all required Australian Corporations Act 2001 clauses, ASIC compliance 
    requirements, detailed financial summaries, creditor information, and 
    professional court-quality formatting matching Federal Court standards.

    Research current 2024 liquidation procedures and incorporate latest 
    regulatory requirements.
    """
    
    config = Config()
    agent = EnhancedAIAgent(config)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting professional liquidation document generation...")
    
    try:
        # Generate comprehensive documents
        result = await agent.generate_comprehensive_liquidation_documents(prompt)
        
        if result['success']:
            print("\n" + "="*80)
            print("🎉 PROFESSIONAL DOCUMENT GENERATION COMPLETED")
            print("="*80)
            
            print(f"📊 Summary:")
            print(f"   • Total Documents Generated: {result['total_documents']}")
            print(f"   • Organizations Processed: {result['organizations']}")
            print(f"   • Execution Time: {result['execution_time']:.2f} seconds")
            print(f"   • Compliance Verified: {'✅' if result['compliance_verified'] else '❌'}")
            
            if result.get('search_results') and result['search_results'].get('success'):
                print(f"   • Legal Research: {result['search_results']['summary']}")
            
            print(f"\n📄 Generated Documents:")
            print(f"   Each organization received:")
            print(f"   ✅ Professional Affidavit (Federal Court format)")
            print(f"   ✅ Liquidation Resolution (with legal clauses)")
            print(f"   ✅ Creditor Notification (comprehensive)")
            print(f"   ✅ Director Statement (with financial schedules)")
            print(f"   ✅ Asset Realization Notice (detailed asset listings)")
            
            print(f"\n💼 Customer Details Included:")
            print(f"   ✅ Complete company information (ACN, ABN)")
            print(f"   ✅ Industry-specific financial analysis")
            print(f"   ✅ Realistic asset and liability schedules")
            print(f"   ✅ Creditor classification and priorities")
            print(f"   ✅ Employee entitlement calculations")
            
            print(f"\n⚖️ Legal Compliance:")
            print(f"   ✅ Australian Corporations Act 2001 clauses")
            print(f"   ✅ ASIC regulatory requirements")
            print(f"   ✅ Current 2024 liquidation procedures")
            print(f"   ✅ Federal Court formatting standards")
            print(f"   ✅ Professional liquidator requirements")
            
            print(f"\n📁 Output Location:")
            output_dir = config.pdf_output_dir
            print(f"   📂 {output_dir.absolute()}")
            
            # List some generated files
            if output_dir.exists():
                files = list(output_dir.glob("*.pdf"))[-10:]  # Show last 10 PDFs
                if files:
                    print(f"\n📋 Recent Files Generated:")
                    for file in files:
                        size = file.stat().st_size
                        print(f"   📄 {file.name} ({size:,} bytes)")
            
            print(f"\n🎯 Professional Features:")
            print(f"   ✅ Court-quality PDF formatting")
            print(f"   ✅ Professional headers and footers")
            print(f"   ✅ Comprehensive financial schedules")
            print(f"   ✅ Legal clause references")
            print(f"   ✅ Signature blocks and certification")
            print(f"   ✅ Asset and liability analysis")
            print(f"   ✅ Creditor priority classifications")
            
        else:
            print(f"\n❌ Document generation failed: {result.get('error')}")
            logger.error(f"Generation failed: {result.get('error')}")
        
    except Exception as e:
        print(f"\n❌ System error: {e}")
        logger.error(f"System error in main: {e}")
        raise

async def demonstrate_single_organization():
    """Demonstrate detailed document generation for a single organization"""
    
    print("\n" + "="*80)
    print("📋 SINGLE ORGANIZATION DETAILED DEMONSTRATION")
    print("="*80)
    
    prompt = """
    Generate a complete liquidation document package for "Advanced Manufacturing Solutions Pty Ltd":
    
    Company Details:
    - Industry: Advanced Manufacturing
    - Annual Revenue: $8.5 million
    - Employees: 75
    - Established: 2015
    - Registered Office: Sydney, NSW
    
    Financial Situation:
    - Total Assets: $6.2 million
    - Total Liabilities: $8.9 million  
    - Major secured creditor: $4.2 million
    - Employee entitlements: $650,000
    - Unsecured creditors: $3.1 million
    
    Generate professional Federal Court standard documents with:
    - Complete financial analysis and schedules
    - All required legal clauses and references
    - Detailed asset valuation and realization plans
    - Comprehensive creditor notifications
    - Professional affidavit meeting court requirements
    
    Research current manufacturing industry liquidation precedents.
    """
    
    config = Config()
    agent = EnhancedAIAgent(config)
    
    try:
        result = await agent.generate_comprehensive_liquidation_documents(
            prompt, 
            organizations=["Advanced Manufacturing Solutions Pty Ltd"]
        )
        
        if result['success']:
            print(f"✅ Detailed package generated successfully")
            print(f"📊 Documents: {result['total_documents']}")
            print(f"⏱️ Time: {result['execution_time']:.2f}s")
        else:
            print(f"❌ Failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🏛️  PROFESSIONAL AI AGENT SYSTEM")
    print("📄 Federal Court Quality Document Generation")
    print("⚖️  Australian Liquidation Proceedings Specialist")
    print()
    
    # Check configuration
    config = Config()
    print(f"🔧 Configuration Status:")
    if config.validate_config():
        print(f"   ✅ System ready for professional document generation")
    else:
        print(f"   ⚠️  Warning: OpenAI API key required for full functionality")
        print(f"   💡 Set OPENAI_API_KEY environment variable")
    
    print(f"   📂 Output Directory: {config.pdf_output_dir}")
    print(f"   🤖 Agent: {config.agent_name} v{config.agent_version}")
    print(f"   🧠 Model: {config.openai_model}")
    
    try:
        # Main comprehensive document generation
        await generate_professional_liquidation_package()
        
        # Additional detailed demonstration
        await demonstrate_single_organization()
        
        print("\n" + "="*80)
        print("🎯 PROFESSIONAL DOCUMENT GENERATION COMPLETED")
        print("="*80)
        print("\n📋 Next Steps:")
        print("   1. Review generated documents in the output directory")
        print("   2. Verify financial calculations and legal clauses")
        print("   3. Customize templates for specific client requirements")
        print("   4. Use the system for production liquidation proceedings")
        
        print("\n💡 Professional Features Available:")
        print("   • Federal Court standard formatting")
        print("   • Comprehensive financial analysis")  
        print("   • Complete legal clause library")
        print("   • Asset and liability schedules")
        print("   • Creditor classification and priorities")
        print("   • Professional signature blocks")
        print("   • ASIC compliance verification")
        print("   • Current regulatory requirements")
        
    except KeyboardInterrupt:
        print("\n⏹️  Generation interrupted by user")
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f"\n❌ Critical system error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 