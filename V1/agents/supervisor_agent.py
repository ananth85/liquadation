#!/usr/bin/env python3
"""
Supervisor Agent for Liquidation Document Generation
Coordinates all agent activities and manages the document generation workflow
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from .base_agent import BaseAgent, AgentTask, AgentStatus
from .data_fetch_agent import DataFetchAgent
from .csv_ingest_agent import CSVIngestAgent
from .llm_generation_agent import LLMGenerationAgent
from .template_engine_agent import TemplateEngineAgent
from .pdf_generation_agent import PDFGenerationAgent
from .rag_knowledge_agent import RAGKnowledgeAgent
from .document_analysis_agent import DocumentAnalysisAgent


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Orchestrates the entire liquidation document generation process
    
    Enhanced with Document Analysis capabilities:
    - Automatic PDF template generation from sample documents
    - Multi-page document support
    - Logo and image handling
    - Advanced layout analysis
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        super().__init__("Supervisor Agent", logger)
        self.config = config
        
        # Initialize all agents
        self.agents = {}
        self._initialize_agents()
        
        # Document analysis tracking
        self.analyzed_documents = {}
        self.generated_templates = {}
        self.sample_folder = Path(config.get("sample_folder", "sample"))
        
        # Auto-analysis settings
        self.auto_analyze_new_pdfs = config.get("auto_analyze_new_pdfs", True)
        self.auto_generate_templates = config.get("auto_generate_templates", True)
        
        self.logger.info("Supervisor Agent initialized with document analysis capabilities")

    def _initialize_agents(self):
        """Initialize all child agents"""
        try:
            # Core agents
            self.agents['data_fetch'] = DataFetchAgent(logger=self.logger)
            self.agents['csv'] = CSVIngestAgent(logger=self.logger)
            
            # Initialize LLM agent with custom provider support
            llm_config = {
                'api_key': self.config.get('llm_api_key') or self.config.get('openai_api_key'),
                'base_url': self.config.get('llm_base_url'),
                'model': self.config.get('llm_model', 'gpt-3.5-turbo'),
                'max_tokens': self.config.get('llm_max_tokens', 4000),
                'temperature': self.config.get('llm_temperature', 0.7),
                'timeout': self.config.get('llm_timeout', 30)
            }
            
            self.agents['llm'] = LLMGenerationAgent(
                api_key=llm_config['api_key'],
                base_url=llm_config['base_url'],
                model=llm_config['model'],
                max_tokens=llm_config['max_tokens'],
                temperature=llm_config['temperature'],
                timeout=llm_config['timeout'],
                logger=self.logger
            )
            
            self.agents['template'] = TemplateEngineAgent(
                templates_dir=self.config.get('templates_folder', 'templates'),
                logger=self.logger
            )
            self.agents['pdf'] = PDFGenerationAgent(logger=self.logger)
            self.agents['rag'] = RAGKnowledgeAgent(logger=self.logger)
            
            # New document analysis agent
            self.agents['document_analysis'] = DocumentAnalysisAgent(
                sample_dir=self.config.get("sample_folder", "sample"),
                templates_dir=self.config.get("templates_folder", "templates"),
                logger=self.logger
            )
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise

    def get_capabilities(self) -> List[str]:
        return [
            "generate_liquidation_documents",
            "analyze_pdf_documents", 
            "generate_templates_from_pdfs",
            "batch_process_documents",
            "update_rag_knowledge",
            "monitor_sample_folder",
            "generate_multipage_documents",
            "handle_logo_integration",
            "process_multi_user_documents"
        ]

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process high-level tasks and coordinate agent activities"""
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            if task_type == "generate_liquidation_documents":
                return await self._generate_liquidation_documents(input_data)
            elif task_type == "analyze_pdf_documents":
                return await self._analyze_pdf_documents(input_data)
            elif task_type == "generate_templates_from_pdfs":
                return await self._generate_templates_from_pdfs(input_data)
            elif task_type == "batch_process_documents":
                return await self._batch_process_documents(input_data)
            elif task_type == "update_rag_knowledge":
                return await self._update_rag_knowledge(input_data)
            elif task_type == "monitor_sample_folder":
                return await self._monitor_sample_folder(input_data)
            elif task_type == "generate_multipage_documents":
                return await self._generate_multipage_documents(input_data)
            elif task_type == "handle_logo_integration":
                return await self._handle_logo_integration(input_data)
            elif task_type == "process_multi_user_documents":
                return await self._process_multi_user_documents(input_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Supervisor task failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "Manual processing required"
            }

    async def _generate_liquidation_documents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced document generation with PDF analysis integration"""
        self.logger.info("Starting enhanced liquidation document generation")
        
        start_time = datetime.now()
        
        # Step 1: Data collection and enrichment
        data_result = await self._collect_and_enrich_data(input_data)
        if not data_result["success"]:
            return data_result
        
        enriched_data = data_result["data"]
        
        # Step 2: Check for custom templates from analyzed PDFs
        template_result = await self._select_optimal_template(enriched_data)
        
        # Step 3: RAG knowledge enhancement (existing functionality)
        rag_task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="get_document_knowledge",
            input_data={
                "document_type": enriched_data.get("document_type", "liquidation_resolution"),
                "context": enriched_data
            },
            status=AgentStatus.IDLE
        )
        rag_result = await self.agents['rag'].process_task(rag_task)
        
        # Step 4: LLM content generation with RAG enhancement
        llm_task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="generate_document_content",
            input_data={
                "document_type": enriched_data.get("document_type", "liquidation_resolution"),
                "company_data": enriched_data,
                "prompt": enriched_data.get("prompt", ""),
                "rag_knowledge": rag_result.get("knowledge", {}),
                "document_requirements": template_result.get("requirements", {})
            },
            status=AgentStatus.IDLE
        )
        llm_result = await self.agents['llm'].process_task(llm_task)
        
        # Step 5: Template rendering with enhanced capabilities
        template_name = template_result.get("template_name", "liquidation_resolution")
        if not template_name.endswith('.j2'):
            template_name += '.j2'
            
        template_task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="render_template",
            input_data={
                "template_name": template_name,
                "data": {**enriched_data, **llm_result.get("generated_content", {})},
                "rag_insights": rag_result.get("insights", []),
                "multipage_support": template_result.get("multipage_support", False),
                "logo_support": template_result.get("logo_support", False)
            },
            status=AgentStatus.IDLE
        )
        template_result_final = await self.agents['template'].process_task(template_task)
        
        # Step 6: PDF generation with enhanced features
        pdf_task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="generate_pdf",
            input_data={
                "content": template_result_final.get("rendered_content", ""),
                "html_content": template_result_final.get("rendered_content", ""),
                "css_styles": template_result.get("css_styles", ""),
                "output_path": enriched_data.get("output_path", "output_pdfs/liquidation_documents.pdf"),
                "multipage": template_result.get("multipage_support", False),
                "logo_handling": template_result.get("logo_support", False)
            },
            status=AgentStatus.IDLE
        )
        pdf_result = await self.agents['pdf'].process_task(pdf_task)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Create documents list in expected format
        documents = [{
            "success": pdf_result.get("success", False),
            "document_type": "liquidation_resolution",
            "pdf_result": {
                "filename": pdf_result.get("file_path", ""),
                "size": pdf_result.get("file_size", 0)
            }
        }]
        
        return {
            "success": True,
            "processing_time": processing_time,
            "company_data": enriched_data,
            "documents": documents,
            "documents_generated": pdf_result.get("files_generated", []),
            "template_used": template_result.get("template_name"),
            "multipage_support": template_result.get("multipage_support", False),
            "logo_integration": template_result.get("logo_support", False),
            "rag_insights": rag_result.get("insights", []),
            "compliance_warnings": rag_result.get("compliance_warnings", []),
            "data_sources": data_result.get("sources", []),
            "llm_confidence": llm_result.get("confidence_score", 0.85)
        }

    async def _analyze_pdf_documents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PDF documents in the sample folder"""
        file_paths = input_data.get("file_paths", [])
        if not file_paths:
            # Analyze all PDFs in sample folder
            batch_task = AgentTask(
                task_id=str(uuid.uuid4()),
                task_type="batch_analyze_folder",
                input_data={"folder_path": str(self.sample_folder)},
                status=AgentStatus.IDLE
            )
            return await self.agents['document_analysis'].process_task(batch_task)
        
        # Analyze specific files
        results = {}
        for file_path in file_paths:
            analysis_task = AgentTask(
                task_id=str(uuid.uuid4()),
                task_type="analyze_pdf_document",
                input_data={"file_path": file_path},
                status=AgentStatus.IDLE
            )
            result = await self.agents['document_analysis'].process_task(analysis_task)
            results[Path(file_path).name] = result
        
        return {
            "success": True,
            "analyses": results,
            "total_files": len(file_paths)
        }

    async def _generate_templates_from_pdfs(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Jinja2 templates from analyzed PDF documents"""
        file_paths = input_data.get("file_paths", [])
        if not file_paths:
            # Find all PDFs in sample folder
            file_paths = list(self.sample_folder.glob("*.pdf"))
        
        generated_templates = []
        failed_generations = []
        
        for file_path in file_paths:
            try:
                # Generate template from PDF
                template_task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    task_type="generate_template_from_pdf",
                    input_data={
                        "file_path": str(file_path),
                        "template_name": input_data.get("template_name")
                    },
                    status=AgentStatus.IDLE
                )
                result = await self.agents['document_analysis'].process_task(template_task)
                
                if result["success"]:
                    generated_templates.append({
                        "source_pdf": str(file_path),
                        "template_name": result["template_name"],
                        "template_file": result["template_file"],
                        "css_file": result["css_file"],
                        "features": {
                            "multipage": result["supports_multipage"],
                            "logo": result["has_logo"],
                            "tables": result["has_tables"]
                        }
                    })
                    
                    # Update RAG knowledge with new template
                    await self._update_rag_with_template_analysis(result)
                else:
                    failed_generations.append({
                        "file": str(file_path),
                        "error": result.get("error")
                    })
                    
            except Exception as e:
                failed_generations.append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        return {
            "success": True,
            "generated_templates": generated_templates,
            "failed_generations": failed_generations,
            "total_successful": len(generated_templates),
            "total_failed": len(failed_generations)
        }

    async def _select_optimal_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best template based on document requirements and available analyzed templates"""
        document_type = data.get("document_type", "liquidation_resolution")
        
        # Check if we have analyzed templates that match the requirements
        analyzed_docs = self.agents['document_analysis'].get_analyzed_documents()
        
        best_template = None
        template_score = 0
        
        for doc_id, analysis in analyzed_docs.items():
            # Score template based on features and compatibility
            score = 0
            
            # Document type matching
            if document_type in analysis.sections:
                score += 30
            
            # Feature availability
            if "has_logo" in analysis.content_types and data.get("company_logo"):
                score += 20
            
            if "has_tables" in analysis.content_types and (data.get("asset_schedule") or data.get("liability_schedule")):
                score += 15
            
            if "multipage" in analysis.content_types and len(data.get("additional_pages", [])) > 0:
                score += 10
            
            # Template complexity matching
            if analysis.total_pages > 1:
                score += 5
            
            if score > template_score:
                template_score = score
                best_template = analysis
        
        if best_template:
            # Use analyzed template
            template_name = f"{Path(best_template.document_name).stem}_template"
            return {
                "template_name": template_name,
                "template_source": "analyzed_pdf",
                "multipage_support": best_template.total_pages > 1,
                "logo_support": "has_logo" in best_template.content_types,
                "table_support": "has_tables" in best_template.content_types,
                "requirements": {
                    "sections": best_template.sections,
                    "design_elements": best_template.design_elements
                }
            }
        else:
            # Fall back to default template
            return {
                "template_name": document_type,
                "template_source": "default",
                "multipage_support": False,
                "logo_support": False,
                "table_support": True,
                "requirements": {}
            }

    async def _update_rag_with_template_analysis(self, template_result: Dict[str, Any]) -> None:
        """Update RAG knowledge base with new template analysis"""
        analysis = template_result.get("document_analysis", {})
        
        # Create RAG knowledge update
        rag_update_task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="add_document_knowledge", 
            input_data={
                "document_type": template_result["template_name"],
                "structure": {
                    "sections": analysis.get("sections", []),
                    "page_count": analysis.get("total_pages", 1),
                    "design_elements": analysis.get("design_elements", {}),
                    "content_types": analysis.get("content_types", [])
                },
                "legal_clauses": [],  # Extract from document if needed
                "compliance_rules": [],  # Extract from document if needed
                "professional_terms": {}  # Extract from document if needed
            },
            status=AgentStatus.IDLE
        )
        
        await self.agents['rag'].process_task(rag_update_task)

    async def _monitor_sample_folder(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor sample folder for new PDF documents and auto-process them"""
        if not self.auto_analyze_new_pdfs:
            return {
                "success": True,
                "message": "Auto-analysis disabled"
            }
        
        # Get current PDF files
        current_pdfs = set(self.sample_folder.glob("*.pdf"))
        known_pdfs = set(self.analyzed_documents.keys())
        
        new_pdfs = current_pdfs - known_pdfs
        
        if new_pdfs:
            self.logger.info(f"Found {len(new_pdfs)} new PDF documents")
            
            # Analyze new PDFs
            analysis_result = await self._analyze_pdf_documents({
                "file_paths": [str(pdf) for pdf in new_pdfs]
            })
            
            # Generate templates if enabled
            if self.auto_generate_templates:
                template_result = await self._generate_templates_from_pdfs({
                    "file_paths": [str(pdf) for pdf in new_pdfs]
                })
                
                return {
                    "success": True,
                    "new_pdfs_found": len(new_pdfs),
                    "analysis_result": analysis_result,
                    "template_result": template_result
                }
            
            return {
                "success": True,
                "new_pdfs_found": len(new_pdfs),
                "analysis_result": analysis_result
            }
        
        return {
            "success": True,
            "new_pdfs_found": 0,
            "message": "No new PDFs to process"
        }

    async def _generate_multipage_documents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multi-page liquidation documents with complex layouts"""
        # Ensure we use a multipage-capable template
        input_data["document_requirements"] = {
            "multipage": True,
            "complex_layout": True
        }
        
        return await self._generate_liquidation_documents(input_data)

    async def _handle_logo_integration(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle logo integration in document generation"""
        logo_path = input_data.get("logo_path")
        if logo_path and Path(logo_path).exists():
            input_data["company_logo"] = logo_path
            input_data["logo_integration"] = True
        
        return await self._generate_liquidation_documents(input_data)

    async def _process_multi_user_documents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process documents for multiple users/entities"""
        entities = input_data.get("entities", [])
        if not entities:
            return {
                "success": False,
                "error": "No entities provided for multi-user processing"
            }
        
        results = []
        
        for entity in entities:
            # Merge entity data with base input
            entity_data = {**input_data, **entity}
            entity_data["output_path"] = f"output/{entity.get('company_name', 'entity')}_liquidation.pdf"
            
            # Generate documents for this entity
            result = await self._generate_liquidation_documents(entity_data)
            results.append({
                "entity": entity.get("company_name", "Unknown"),
                "result": result
            })
        
        successful = sum(1 for r in results if r["result"]["success"])
        
        return {
            "success": True,
            "total_entities": len(entities),
            "successful": successful,
            "failed": len(entities) - successful,
            "results": results
        }

    async def _collect_and_enrich_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Existing data collection and enrichment method"""
        enriched_data = input_data.copy()
        sources = []
        
        # ABN lookup if ABN provided
        if 'abn' in input_data and input_data['abn']:
            try:
                data_task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    task_type="fetch_abn_data",
                    input_data={"abn": input_data['abn']},
                    status=AgentStatus.IDLE
                )
                abn_result = await self.agents['data_fetch'].process_task(data_task)
                
                if abn_result['success']:
                    enriched_data.update(abn_result['data'])
                    sources.append("ABN Registry")
                    self.logger.info(f"Enriched data with ABN lookup for {input_data['abn']}")
                    
            except Exception as e:
                self.logger.warning(f"ABN lookup failed: {e}")
        
        # CSV data integration if CSV file provided
        if 'csv_file' in input_data and input_data['csv_file']:
            try:
                csv_task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    task_type="process_csv",
                    input_data={"file_path": input_data['csv_file']},
                    status=AgentStatus.IDLE
                )
                csv_result = await self.agents['csv'].process_task(csv_task)
                
                if csv_result['success']:
                    enriched_data.update(csv_result['data'])
                    sources.append("CSV File")
                    self.logger.info(f"Enriched data with CSV file: {input_data['csv_file']}")
                    
            except Exception as e:
                self.logger.warning(f"CSV processing failed: {e}")
        
        # Add metadata
        enriched_data['generation_timestamp'] = datetime.now().isoformat()
        enriched_data['data_sources'] = sources
        
        return {
            "success": True,
            "data": enriched_data,
            "sources": sources
        }

    async def _batch_process_documents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch process multiple document generation requests"""
        requests = input_data.get("requests", [])
        if not requests:
            return {
                "success": False,
                "error": "No requests provided for batch processing"
            }
        
        results = []
        
        for i, request in enumerate(requests):
            try:
                self.logger.info(f"Processing batch request {i+1}/{len(requests)}")
                result = await self._generate_liquidation_documents(request)
                results.append({
                    "request_id": i,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "request_id": i,
                    "result": {
                        "success": False,
                        "error": str(e)
                    }
                })
        
        successful = sum(1 for r in results if r["result"]["success"])
        
        return {
            "success": True,
            "total_requests": len(requests),
            "successful": successful,
            "failed": len(requests) - successful,
            "results": results
        }

    async def _update_rag_knowledge(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update RAG knowledge base with new information"""
        update_task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="update_knowledge_base",
            input_data=input_data,
            status=AgentStatus.IDLE
        )
        
        return await self.agents['rag'].process_task(update_task)

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        health_status = {
            "supervisor": {
                "status": "healthy" if self.status.value != "error" else "unhealthy",
                "agents_count": len(self.agents),
                "analyzed_documents": len(self.analyzed_documents),
                "generated_templates": len(self.generated_templates)
            },
            "agents": {}
        }
        
        for agent_name, agent in self.agents.items():
            agent_status = agent.get_status()
            is_healthy = agent_status["status"] != "error"
            
            health_status["agents"][agent_name] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "queued_tasks": agent_status["queued_tasks"],
                "completed_tasks": agent_status["completed_tasks"],
                "issues": [] if is_healthy else ["Agent in error state"]
            }
        
        return health_status

    async def generate_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate liquidation documents from a prompt"""
        pipeline_id = str(uuid.uuid4())
        
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="generate_liquidation_documents",
            input_data={"prompt": prompt, "pipeline_id": pipeline_id},
            status=AgentStatus.IDLE
        )
        
        result = await self.process_task(task)
        result["pipeline_id"] = pipeline_id
        return result

    async def generate_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """Generate liquidation documents from CSV data"""
        pipeline_id = str(uuid.uuid4())
        
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="batch_process_documents",
            input_data={"csv_file": csv_path, "pipeline_id": pipeline_id},
            status=AgentStatus.IDLE
        )
        
        result = await self.process_task(task)
        result["pipeline_id"] = pipeline_id
        return result

    async def generate_from_abn(self, abn: str) -> Dict[str, Any]:
        """Generate liquidation documents from ABN lookup"""
        pipeline_id = str(uuid.uuid4())
        
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type="generate_liquidation_documents",
            input_data={"abn": abn, "pipeline_id": pipeline_id},
            status=AgentStatus.IDLE
        )
        
        result = await self.process_task(task)
        result["pipeline_id"] = pipeline_id
        return result

    async def cleanup_resources(self) -> None:
        """Cleanup resources and perform any necessary shutdown tasks"""
        self.logger.info("Cleaning up supervisor resources")
        
        # Clear memory for all agents
        for agent in self.agents.values():
            if hasattr(agent, 'clear_memory'):
                agent.clear_memory()
        
        # Clear supervisor memory
        self.clear_memory()
        self.analyzed_documents.clear()
        self.generated_templates.clear()

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "name": agent.name,
                "capabilities": agent.get_capabilities()
            }
        
        # Add document analysis status
        if 'document_analysis' in self.agents:
            doc_agent = self.agents['document_analysis']
            status['document_analysis']['analyzed_documents'] = len(doc_agent.get_analyzed_documents())
            status['document_analysis']['template_patterns'] = len(doc_agent.get_template_patterns())
        
        return status

    def get_analyzed_documents_summary(self) -> Dict[str, Any]:
        """Get summary of analyzed documents and generated templates"""
        if 'document_analysis' not in self.agents:
            return {"error": "Document analysis agent not available"}
        
        doc_agent = self.agents['document_analysis']
        analyzed_docs = doc_agent.get_analyzed_documents()
        
        summary = {
            "total_analyzed": len(analyzed_docs),
            "documents": {}
        }
        
        for doc_id, analysis in analyzed_docs.items():
            summary["documents"][analysis.document_name] = {
                "pages": analysis.total_pages,
                "sections": analysis.sections,
                "content_types": analysis.content_types,
                "has_logo": "has_logo" in analysis.content_types,
                "has_tables": "has_tables" in analysis.content_types,
                "multipage": analysis.total_pages > 1
            }
        
        return summary 