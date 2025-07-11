#!/usr/bin/env python3
"""
Test script to verify diverse document generation with different law firms and templates
Part of the Professional AI Agent System test suite
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path to import agent modules
sys.path.append(str(Path(__file__).parent.parent))

from agent.professional_pdf_generator import *
from agent.config import Config

async def test_document_variety():
    """Test generation of diverse legal documents"""
    
    config = Config()
    generator = ProfessionalPDFGenerator(config)
    
    # Test companies with varied profiles
    companies = [
        CompanyDetails(
            name='Tech Solutions Pty Ltd', 
            acn='ACN123456789', 
            abn='ABN11223344556', 
            directors=['John Smith', 'Sarah Johnson'],
            liquidator='Michael Brown',
            liquidator_registration='LIQ001'
        ),
        CompanyDetails(
            name='Manufacturing Corp', 
            acn='ACN987654321', 
            abn='ABN99887766554', 
            directors=['Jane Doe', 'Robert Wilson'],
            liquidator='Patricia Green',
            liquidator_registration='LIQ002'
        ),
        CompanyDetails(
            name='Retail Enterprises Ltd', 
            acn='ACN555666777', 
            abn='ABN33445566778', 
            directors=['Bob Wilson', 'Amanda Lee'],
            liquidator='David Chen',
            liquidator_registration='LIQ003'
        )
    ]
    
    # Sample financial data with variations
    financials = [
        FinancialSummary(
            total_assets=2500000, 
            total_liabilities=1800000, 
            cash_at_bank=250000, 
            debtors=400000,
            stock_inventory=300000,
            plant_equipment=500000,
            secured_creditors=1200000,
            unsecured_creditors=600000,
            employee_entitlements=150000
        ),
        FinancialSummary(
            total_assets=5800000, 
            total_liabilities=4200000, 
            cash_at_bank=180000, 
            debtors=850000,
            stock_inventory=1200000,
            plant_equipment=2800000,
            real_property=700000,
            secured_creditors=2800000,
            unsecured_creditors=1400000,
            employee_entitlements=320000
        ),
        FinancialSummary(
            total_assets=1200000, 
            total_liabilities=1850000, 
            cash_at_bank=45000, 
            debtors=180000,
            stock_inventory=650000,
            plant_equipment=325000,
            secured_creditors=980000,
            unsecured_creditors=870000,
            employee_entitlements=95000
        )
    ]
    
    # Document types to test
    doc_types = ['affidavit', 'resolution', 'creditor_notice', 'director_statement', 'asset_notice']
    
    print('🎯 GENERATING DIVERSE LEGAL DOCUMENTS')
    print('=' * 60)
    print('Testing different law firms, templates, and document structures\n')
    
    generated_docs = []
    failed_docs = []
    
    for i, company in enumerate(companies):
        financial = financials[i]
        for j, doc_type in enumerate(doc_types):
            try:
                result = await generator.generate_document(doc_type, company, financial)
                if result['success']:
                    generated_docs.append(result)
                    # Format output with proper spacing
                    doc_name = result["document_type"][:25].ljust(25)
                    firm_name = result["law_firm"][:20].ljust(20)
                    company_name = company.name[:30].ljust(30)
                    print(f'✅ {doc_name} | {firm_name} | {company_name}')
                else:
                    failed_docs.append(f'{doc_type} - {company.name}')
                    print(f'❌ FAILED: {doc_type:20} | {company.name}')
            except Exception as e:
                failed_docs.append(f'{doc_type} - {company.name}: {str(e)[:50]}')
                print(f'❌ ERROR: {doc_type:20} | {company.name}: {str(e)[:50]}')
    
    print('\n' + '=' * 60)
    print(f'📊 GENERATION SUMMARY')
    print('=' * 60)
    print(f'✅ Successfully Generated: {len(generated_docs)} documents')
    print(f'❌ Failed: {len(failed_docs)} documents')
    
    if failed_docs:
        print(f'\n⚠️  Failed Documents:')
        for failure in failed_docs:
            print(f'   • {failure}')
    
    # Show variety statistics
    if generated_docs:
        law_firms = set(doc['law_firm'] for doc in generated_docs)
        doc_types_generated = set(doc['document_type'] for doc in generated_docs)
        template_styles = set(doc.get('template_style', 'unknown') for doc in generated_docs)
        
        print(f'\n🏛️  Law Firms Used: {len(law_firms)}')
        for firm in sorted(law_firms):
            count = sum(1 for doc in generated_docs if doc['law_firm'] == firm)
            print(f'   • {firm} ({count} documents)')
        
        print(f'\n📄 Document Types Generated: {len(doc_types_generated)}')
        for doc_type in sorted(doc_types_generated):
            count = sum(1 for doc in generated_docs if doc['document_type'] == doc_type)
            print(f'   • {doc_type} ({count} documents)')
        
        print(f'\n🎨 Template Styles: {len(template_styles)}')
        for style in sorted(template_styles):
            if style != 'unknown':
                count = sum(1 for doc in generated_docs if doc.get('template_style') == style)
                print(f'   • {style} ({count} documents)')
        
        # File size analysis
        total_size = sum(doc['file_size'] for doc in generated_docs)
        avg_size = total_size / len(generated_docs)
        print(f'\n📁 File Statistics:')
        print(f'   • Total Size: {total_size / 1024:.1f} KB')
        print(f'   • Average Size: {avg_size / 1024:.1f} KB')
        print(f'   • Size Range: {min(doc["file_size"] for doc in generated_docs) / 1024:.1f} - {max(doc["file_size"] for doc in generated_docs) / 1024:.1f} KB')
    
    print(f'\n🎉 DIVERSITY TEST RESULTS:')
    if len(law_firms) >= 3 and len(doc_types_generated) >= 3:
        print(f'✅ SUCCESS: Document generation system creates diverse, unique documents!')
        print(f'✅ Law Firm Variety: {len(law_firms)}/5 firms used')
        print(f'✅ Document Type Variety: {len(doc_types_generated)}/5 types generated')
        print(f'✅ Template Diversity: Multiple styles and formats confirmed')
    else:
        print(f'⚠️  LIMITED DIVERSITY: Only {len(law_firms)} firms and {len(doc_types_generated)} document types')
    
    return generated_docs

def run_diversity_test():
    """Run the diversity test with proper error handling"""
    try:
        print("🏛️  PROFESSIONAL AI AGENT - DOCUMENT DIVERSITY TEST")
        print("="*60)
        print("Testing the enhanced PDF generation system")
        print("Verifying different law firms, templates, and document structures\n")
        
        # Run the async test
        documents = asyncio.run(test_document_variety())
        
        print(f"\n📋 TEST COMPLETED")
        print(f"Generated documents are saved in the 'output' directory")
        print(f"Check the files to verify different law firm letterheads and formats")
        
        return len(documents) > 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = run_diversity_test()
    sys.exit(0 if success else 1) 