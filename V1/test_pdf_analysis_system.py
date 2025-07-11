#!/usr/bin/env python3
"""
Test Script for Enhanced PDF Analysis and Template Generation System
Tests document analysis, template generation, and RAG knowledge updates
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
import time
import json

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from agents import (
    SupervisorAgent, 
    DocumentAnalysisAgent, 
    TemplateEngineAgent, 
    RAGKnowledgeAgent,
    AgentTask
)
from agents.base_agent import AgentStatus
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_pdf_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PDFAnalysisTestSuite:
    """Test suite for PDF analysis and template generation"""
    
    def __init__(self):
        self.sample_dir = Path("sample")
        self.templates_dir = Path("templates")
        self.output_dir = Path("output")
        
        # Ensure directories exist
        for directory in [self.sample_dir, self.templates_dir, self.output_dir]:
            directory.mkdir(exist_ok=True)
        
        # Initialize agents
        self.config = {
            # LLM Provider Configuration
            "llm_api_key": "your-custom-llm-api-key-here",  # Replace with actual key
            "llm_base_url": "https://your-custom-provider-url.com/v1",
            "llm_model": "gpt-3.5-turbo",
            "llm_max_tokens": 4000,
            "llm_temperature": 0.7,
            "llm_timeout": 30,
            
            # Legacy OpenAI (fallback)
            "openai_api_key": "",
            
            # Directories
            "sample_folder": str(self.sample_dir),
            "templates_folder": str(self.templates_dir),
            
            # System settings
            "auto_analyze_new_pdfs": True,
            "auto_generate_templates": True
        }
        
        self.supervisor = None
        self.doc_analyzer = None
        self.template_agent = None
        self.rag_agent = None
        
        self.test_results = {}

    def _create_task(self, task_type: str, input_data: Dict[str, Any]) -> AgentTask:
        """Helper to create AgentTask with required parameters"""
        return AgentTask(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            input_data=input_data,
            status=AgentStatus.IDLE
        )

    async def initialize_agents(self):
        """Initialize all agents for testing"""
        try:
            logger.info("Initializing agents for PDF analysis testing...")
            
            # Initialize individual agents
            self.doc_analyzer = DocumentAnalysisAgent(
                sample_dir=str(self.sample_dir),
                templates_dir=str(self.templates_dir),
                logger=logger
            )
            
            self.template_agent = TemplateEngineAgent(
                templates_dir=str(self.templates_dir),
                logger=logger
            )
            
            self.rag_agent = RAGKnowledgeAgent(logger=logger)
            
            # Initialize supervisor with enhanced config
            self.supervisor = SupervisorAgent(self.config, logger=logger)
            
            logger.info("All agents initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            return False

    async def test_pdf_discovery(self) -> Dict[str, Any]:
        """Test PDF discovery in sample folder"""
        logger.info("🔍 Testing PDF discovery...")
        
        try:
            # List PDF files in sample directory
            pdf_files = list(self.sample_dir.glob("*.pdf"))
            
            result = {
                "test_name": "PDF Discovery",
                "success": len(pdf_files) > 0,
                "pdf_files_found": [str(pdf.name) for pdf in pdf_files],
                "total_files": len(pdf_files),
                "details": f"Found {len(pdf_files)} PDF files in sample directory"
            }
            
            if result["success"]:
                logger.info(f"✅ Found {len(pdf_files)} PDF files: {', '.join(result['pdf_files_found'])}")
            else:
                logger.warning("⚠️ No PDF files found in sample directory")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ PDF discovery failed: {e}")
            return {
                "test_name": "PDF Discovery",
                "success": False,
                "error": str(e)
            }

    async def test_single_pdf_analysis(self, pdf_file: Path) -> Dict[str, Any]:
        """Test analysis of a single PDF file"""
        logger.info(f"📄 Analyzing PDF: {pdf_file.name}")
        
        try:
            # Analyze the PDF
            task = self._create_task(
                task_type="analyze_pdf_document",
                input_data={"file_path": str(pdf_file)}
            )
            
            start_time = time.time()
            result = await self.doc_analyzer.process_task(task)
            analysis_time = time.time() - start_time
            
            analysis_result = {
                "test_name": f"Single PDF Analysis - {pdf_file.name}",
                "success": result.get("success", False),
                "analysis_time": round(analysis_time, 2),
                "file_name": pdf_file.name,
                "document_id": result.get("document_id"),
                "engine_used": result.get("engine_used")
            }
            
            if result["success"]:
                analysis_data = result.get("analysis", {})
                analysis_result.update({
                    "total_pages": analysis_data.get("total_pages", 0),
                    "sections_found": len(analysis_data.get("sections", [])),
                    "content_types": analysis_data.get("content_types", []),
                    "has_logo": "has_logo" in analysis_data.get("content_types", []),
                    "has_tables": "has_tables" in analysis_data.get("content_types", []),
                    "multipage": analysis_data.get("total_pages", 1) > 1,
                    "images_found": len(analysis_data.get("logos_images", [])),
                    "tables_found": len(analysis_data.get("tables", [])),
                    "form_fields": len(analysis_data.get("form_fields", []))
                })
                
                logger.info(f"✅ Analysis completed in {analysis_time:.2f}s - {analysis_result['total_pages']} pages, {analysis_result['sections_found']} sections")
            else:
                error_msg = result.get("error", "Unknown error")
                analysis_result["error"] = error_msg
                logger.error(f"❌ Analysis failed: {error_msg}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ PDF analysis exception: {e}")
            return {
                "test_name": f"Single PDF Analysis - {pdf_file.name}",
                "success": False,
                "error": str(e)
            }

    async def test_batch_pdf_analysis(self) -> Dict[str, Any]:
        """Test batch analysis of all PDFs"""
        logger.info("📊 Testing batch PDF analysis...")
        
        try:
            # Batch analyze all PDFs
            task = self._create_task(
                task_type="batch_analyze_folder",
                input_data={"folder_path": str(self.sample_dir)}
            )
            
            start_time = time.time()
            result = await self.doc_analyzer.process_task(task)
            batch_time = time.time() - start_time
            
            batch_result = {
                "test_name": "Batch PDF Analysis",
                "success": result.get("success", False),
                "batch_time": round(batch_time, 2),
                "total_files": result.get("total_files", 0),
                "successful": result.get("successful", 0),
                "failed": result.get("failed", 0)
            }
            
            if result["success"]:
                logger.info(f"✅ Batch analysis completed in {batch_time:.2f}s - {batch_result['successful']}/{batch_result['total_files']} successful")
                
                # Add details about analyzed documents
                results = result.get("results", {})
                batch_result["analysis_details"] = {}
                
                for filename, file_result in results.items():
                    if file_result.get("success"):
                        analysis = file_result.get("analysis", {})
                        batch_result["analysis_details"][filename] = {
                            "pages": analysis.get("total_pages", 0),
                            "sections": len(analysis.get("sections", [])),
                            "content_types": analysis.get("content_types", [])
                        }
            else:
                error_msg = result.get("error", "Unknown error")
                batch_result["error"] = error_msg
                logger.error(f"❌ Batch analysis failed: {error_msg}")
            
            return batch_result
            
        except Exception as e:
            logger.error(f"❌ Batch analysis exception: {e}")
            return {
                "test_name": "Batch PDF Analysis",
                "success": False,
                "error": str(e)
            }

    async def test_template_generation(self, pdf_file: Path) -> Dict[str, Any]:
        """Test template generation from analyzed PDF"""
        logger.info(f"🎨 Testing template generation from: {pdf_file.name}")
        
        try:
            # Generate template from PDF
            template_name = f"{pdf_file.stem}_auto_template"
            
            task = self._create_task(
                task_type="generate_template_from_pdf",
                input_data={
                    "file_path": str(pdf_file),
                    "template_name": template_name
                }
            )
            
            start_time = time.time()
            result = await self.doc_analyzer.process_task(task)
            generation_time = time.time() - start_time
            
            template_result = {
                "test_name": f"Template Generation - {pdf_file.name}",
                "success": result.get("success", False),
                "generation_time": round(generation_time, 2),
                "source_pdf": pdf_file.name,
                "template_name": template_name
            }
            
            if result["success"]:
                template_result.update({
                    "template_file": result.get("template_file"),
                    "css_file": result.get("css_file"),
                    "features": {
                        "multipage": result.get("supports_multipage", False),
                        "logo": result.get("has_logo", False),
                        "tables": result.get("has_tables", False)
                    },
                    "sections_generated": result.get("generated_sections", [])
                })
                
                # Verify template files exist
                template_file = Path(result["template_file"])
                css_file = Path(result["css_file"])
                
                template_result["files_created"] = {
                    "template_exists": template_file.exists(),
                    "css_exists": css_file.exists(),
                    "template_size": template_file.stat().st_size if template_file.exists() else 0,
                    "css_size": css_file.stat().st_size if css_file.exists() else 0
                }
                
                logger.info(f"✅ Template generated in {generation_time:.2f}s - {template_result['features']}")
            else:
                error_msg = result.get("error", "Unknown error")
                template_result["error"] = error_msg
                logger.error(f"❌ Template generation failed: {error_msg}")
            
            return template_result
            
        except Exception as e:
            logger.error(f"❌ Template generation exception: {e}")
            return {
                "test_name": f"Template Generation - {pdf_file.name}",
                "success": False,
                "error": str(e)
            }

    async def test_rag_integration(self) -> Dict[str, Any]:
        """Test RAG knowledge base integration with PDF analysis"""
        logger.info("🧠 Testing RAG knowledge integration...")
        
        try:
            # Get analyzed documents
            analyzed_docs = self.doc_analyzer.get_analyzed_documents()
            
            if not analyzed_docs:
                return {
                    "test_name": "RAG Integration",
                    "success": False,
                    "error": "No analyzed documents found for RAG integration"
                }
            
            # Integrate analysis results into RAG
            analysis_results = {}
            for doc_id, analysis in analyzed_docs.items():
                analysis_results[doc_id] = {
                    "success": True,
                    "analysis": {
                        "document_name": analysis.document_name,
                        "total_pages": analysis.total_pages,
                        "sections": analysis.sections,
                        "content_types": analysis.content_types,
                        "design_elements": analysis.design_elements
                    }
                }
            
            task = self._create_task(
                task_type="integrate_pdf_analysis",
                input_data={"analysis_results": analysis_results}
            )
            
            start_time = time.time()
            result = await self.rag_agent.process_task(task)
            integration_time = time.time() - start_time
            
            rag_result = {
                "test_name": "RAG Integration",
                "success": result.get("success", False),
                "integration_time": round(integration_time, 2),
                "documents_processed": len(analyzed_docs)
            }
            
            if result["success"]:
                rag_result.update({
                    "integrated_documents": result.get("integrated_documents", 0),
                    "new_patterns": result.get("new_patterns", 0),
                    "updated_knowledge": result.get("updated_knowledge", 0),
                    "total_patterns": result.get("total_patterns", 0),
                    "cache_size": result.get("cache_size", 0)
                })
                
                logger.info(f"✅ RAG integration completed in {integration_time:.2f}s - {rag_result['new_patterns']} new patterns")
            else:
                error_msg = result.get("error", "Unknown error")
                rag_result["error"] = error_msg
                logger.error(f"❌ RAG integration failed: {error_msg}")
            
            return rag_result
            
        except Exception as e:
            logger.error(f"❌ RAG integration exception: {e}")
            return {
                "test_name": "RAG Integration",
                "success": False,
                "error": str(e)
            }

    async def test_enhanced_document_generation(self) -> Dict[str, Any]:
        """Test enhanced document generation using analyzed templates"""
        logger.info("📝 Testing enhanced document generation...")
        
        try:
            # Test data for document generation
            test_data = {
                "prompt": "Generate liquidation documents for a tech startup in Sydney that cannot meet its financial obligations",
                "company_name": "TechStart Innovations Pty Ltd",
                "abn": "12345678901",
                "acn": "123456789",
                "director_name": "John Smith",
                "liquidator_name": "Jane Doe",
                "liquidation_reason": "Unable to meet financial obligations due to market conditions",
                "resolution_date": "2024-01-15",
                "document_type": "liquidation_resolution",
                "output_path": str(self.output_dir / "enhanced_test_document.pdf"),
                "logo_integration": True,
                "multipage_support": True
            }
            
            # Use supervisor for enhanced document generation
            task = self._create_task(
                task_type="generate_liquidation_documents",
                input_data=test_data
            )
            
            start_time = time.time()
            result = await self.supervisor.process_task(task)
            generation_time = time.time() - start_time
            
            doc_result = {
                "test_name": "Enhanced Document Generation",
                "success": result.get("success", False),
                "generation_time": round(generation_time, 2),
                "test_company": test_data["company_name"]
            }
            
            if result["success"]:
                doc_result.update({
                    "documents_generated": result.get("documents_generated", []),
                    "template_used": result.get("template_used"),
                    "multipage_support": result.get("multipage_support", False),
                    "logo_integration": result.get("logo_integration", False),
                    "rag_insights": len(result.get("rag_insights", [])),
                    "compliance_warnings": len(result.get("compliance_warnings", [])),
                    "data_sources": result.get("data_sources", []),
                    "llm_confidence": result.get("llm_confidence", 0)
                })
                
                # Check if output files exist
                generated_files = result.get("documents_generated", [])
                doc_result["files_verification"] = {}
                
                for file_path in generated_files:
                    file_obj = Path(file_path)
                    doc_result["files_verification"][file_obj.name] = {
                        "exists": file_obj.exists(),
                        "size": file_obj.stat().st_size if file_obj.exists() else 0
                    }
                
                logger.info(f"✅ Enhanced generation completed in {generation_time:.2f}s - Template: {doc_result['template_used']}")
            else:
                error_msg = result.get("error", "Unknown error")
                doc_result["error"] = error_msg
                logger.error(f"❌ Enhanced generation failed: {error_msg}")
            
            return doc_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced generation exception: {e}")
            return {
                "test_name": "Enhanced Document Generation",
                "success": False,
                "error": str(e)
            }

    async def test_template_validation(self) -> Dict[str, Any]:
        """Test template validation functionality"""
        logger.info("🔍 Testing template validation...")
        
        try:
            # Get available templates
            task = self._create_task(
                task_type="list_available_templates",
                input_data={}
            )
            
            templates_result = await self.template_agent.process_task(task)
            
            if not templates_result.get("success"):
                return {
                    "test_name": "Template Validation",
                    "success": False,
                    "error": "Failed to list available templates"
                }
            
            templates = templates_result.get("templates", [])
            validation_results = []
            
            # Validate each template
            for template_info in templates:
                template_name = template_info["name"]
                
                validate_task = self._create_task(
                    task_type="validate_template",
                    input_data={"template_name": template_name}
                )
                
                validation = await self.template_agent.process_task(validate_task)
                validation_results.append({
                    "template": template_name,
                    "valid": validation.get("valid", False),
                    "error": validation.get("error")
                })
            
            valid_templates = sum(1 for v in validation_results if v["valid"])
            
            validation_result = {
                "test_name": "Template Validation",
                "success": True,
                "total_templates": len(templates),
                "valid_templates": valid_templates,
                "invalid_templates": len(templates) - valid_templates,
                "validation_details": validation_results
            }
            
            logger.info(f"✅ Template validation completed - {valid_templates}/{len(templates)} valid")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Template validation exception: {e}")
            return {
                "test_name": "Template Validation",
                "success": False,
                "error": str(e)
            }

    async def test_multi_user_document_generation(self) -> Dict[str, Any]:
        """Test multi-user document generation"""
        logger.info("👥 Testing multi-user document generation...")
        
        try:
            # Test data for multiple entities
            entities = [
                {
                    "company_name": "Alpha Corp Pty Ltd",
                    "abn": "11111111111",
                    "director_name": "Alice Johnson",
                    "liquidation_reason": "Market downturn"
                },
                {
                    "company_name": "Beta Solutions Pty Ltd", 
                    "abn": "22222222222",
                    "director_name": "Bob Williams",
                    "liquidation_reason": "Cash flow issues"
                },
                {
                    "company_name": "Gamma Industries Pty Ltd",
                    "abn": "33333333333", 
                    "director_name": "Carol Davis",
                    "liquidation_reason": "Strategic restructuring"
                }
            ]
            
            test_data = {
                "entities": entities,
                "document_type": "liquidation_resolution",
                "liquidator_name": "Professional Liquidator Services",
                "resolution_date": "2024-01-15"
            }
            
            task = self._create_task(
                task_type="process_multi_user_documents",
                input_data=test_data
            )
            
            start_time = time.time()
            result = await self.supervisor.process_task(task)
            generation_time = time.time() - start_time
            
            multi_result = {
                "test_name": "Multi-User Document Generation",
                "success": result.get("success", False),
                "generation_time": round(generation_time, 2),
                "entities_count": len(entities)
            }
            
            if result["success"]:
                multi_result.update({
                    "total_entities": result.get("total_entities", 0),
                    "successful": result.get("successful", 0),
                    "failed": result.get("failed", 0),
                    "success_rate": f"{(result.get('successful', 0) / result.get('total_entities', 1) * 100):.1f}%"
                })
                
                # Add details about each entity
                entity_results = result.get("results", [])
                multi_result["entity_details"] = []
                
                for entity_result in entity_results:
                    entity_info = {
                        "entity": entity_result.get("entity", "Unknown"),
                        "success": entity_result.get("result", {}).get("success", False),
                        "documents": len(entity_result.get("result", {}).get("documents_generated", []))
                    }
                    multi_result["entity_details"].append(entity_info)
                
                logger.info(f"✅ Multi-user generation completed in {generation_time:.2f}s - {multi_result['successful']}/{multi_result['total_entities']} successful")
            else:
                error_msg = result.get("error", "Unknown error")
                multi_result["error"] = error_msg
                logger.error(f"❌ Multi-user generation failed: {error_msg}")
            
            return multi_result
            
        except Exception as e:
            logger.error(f"❌ Multi-user generation exception: {e}")
            return {
                "test_name": "Multi-User Document Generation",
                "success": False,
                "error": str(e)
            }

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        logger.info("🚀 Starting comprehensive PDF analysis test suite...")
        
        # Initialize agents
        if not await self.initialize_agents():
            return {"success": False, "error": "Failed to initialize agents"}
        
        test_start_time = time.time()
        
        # Test 1: PDF Discovery
        self.test_results["pdf_discovery"] = await self.test_pdf_discovery()
        
        if not self.test_results["pdf_discovery"]["success"]:
            logger.warning("⚠️ No PDFs found - creating sample test scenarios")
            return {"success": False, "error": "No sample PDFs found for testing"}
        
        # Get PDF files for further testing
        pdf_files = [self.sample_dir / name for name in self.test_results["pdf_discovery"]["pdf_files_found"]]
        
        # Test 2: Single PDF Analysis (test first PDF)
        if pdf_files:
            self.test_results["single_analysis"] = await self.test_single_pdf_analysis(pdf_files[0])
        
        # Test 3: Batch PDF Analysis
        self.test_results["batch_analysis"] = await self.test_batch_pdf_analysis()
        
        # Test 4: Template Generation (test first PDF)
        if pdf_files:
            self.test_results["template_generation"] = await self.test_template_generation(pdf_files[0])
        
        # Test 5: RAG Integration
        self.test_results["rag_integration"] = await self.test_rag_integration()
        
        # Test 6: Template Validation
        self.test_results["template_validation"] = await self.test_template_validation()
        
        # Test 7: Enhanced Document Generation
        self.test_results["enhanced_generation"] = await self.test_enhanced_document_generation()
        
        # Test 8: Multi-User Document Generation
        self.test_results["multi_user_generation"] = await self.test_multi_user_document_generation()
        
        total_time = time.time() - test_start_time
        
        # Calculate overall results
        successful_tests = sum(1 for test in self.test_results.values() if test.get("success", False))
        total_tests = len(self.test_results)
        
        summary = {
            "success": True,
            "total_time": round(total_time, 2),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": f"{(successful_tests / total_tests * 100):.1f}%",
            "test_results": self.test_results
        }
        
        logger.info(f"🎯 Test suite completed in {total_time:.2f}s - {successful_tests}/{total_tests} tests passed")
        
        return summary

    def save_test_results(self, results: Dict[str, Any], filename: str = "pdf_analysis_test_results.json"):
        """Save test results to file"""
        try:
            results_file = Path(filename)
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Test results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save test results: {e}")

    def print_test_summary(self, results: Dict[str, Any]):
        """Print formatted test summary"""
        print("\n" + "="*80)
        print("📋 PDF ANALYSIS SYSTEM TEST SUMMARY")
        print("="*80)
        print(f"⏱️  Total Time: {results['total_time']}s")
        print(f"✅ Success Rate: {results['success_rate']} ({results['successful_tests']}/{results['total_tests']})")
        print(f"📁 Output Directory: {self.output_dir}")
        print(f"📄 Templates Directory: {self.templates_dir}")
        
        print("\n📝 DETAILED RESULTS:")
        print("-" * 50)
        
        for test_name, test_result in results["test_results"].items():
            status = "✅ PASS" if test_result.get("success") else "❌ FAIL"
            print(f"{status} {test_result.get('test_name', test_name)}")
            
            if test_result.get("success"):
                # Print key metrics for successful tests
                if "analysis_time" in test_result:
                    print(f"    ⏱️  Time: {test_result['analysis_time']}s")
                if "total_pages" in test_result:
                    print(f"    📄 Pages: {test_result['total_pages']}")
                if "sections_found" in test_result:
                    print(f"    📋 Sections: {test_result['sections_found']}")
                if "template_name" in test_result:
                    print(f"    🎨 Template: {test_result['template_name']}")
                if "new_patterns" in test_result:
                    print(f"    🧩 New Patterns: {test_result['new_patterns']}")
                if "success_rate" in test_result:
                    print(f"    📊 Success Rate: {test_result['success_rate']}")
            else:
                error = test_result.get("error", "Unknown error")
                print(f"    ❌ Error: {error}")
            
            print()
        
        print("="*80)
        print("🎉 PDF Analysis System Test Complete!")
        print("="*80)


async def main():
    """Main test function"""
    test_suite = PDFAnalysisTestSuite()
    
    try:
        # Run comprehensive test
        results = await test_suite.run_comprehensive_test()
        
        # Save and display results
        test_suite.save_test_results(results)
        test_suite.print_test_summary(results)
        
        # Return appropriate exit code
        return 0 if results.get("success") and results.get("failed_tests", 0) == 0 else 1
        
    except Exception as e:
        logger.error(f"❌ Test suite failed with exception: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 