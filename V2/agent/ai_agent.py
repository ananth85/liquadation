"""
Main AI Agent Class
Orchestrates LLM interaction, web search, and PDF generation
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import Config
from .llm_client import LLMService
from .web_search import WebSearchService
from .pdf_generator import PDFGenerator, DocumentMetadata

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of a completed task"""
    task_type: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class AgentResponse:
    """Complete response from AI agent"""
    prompt: str
    analysis: Dict[str, Any]
    search_results: Optional[Dict[str, Any]] = None
    generated_documents: Optional[List[Any]] = None
    task_results: Optional[List[TaskResult]] = None
    total_execution_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


class AIAgent:
    """
    Main AI Agent that processes prompts and orchestrates all services
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.llm_service = LLMService(config)
        self.search_service = WebSearchService(config)
        self.pdf_generator = PDFGenerator(config)
        
        # Task execution tracking
        self._active_tasks = {}
        self._task_counter = 0
        
        logger.info(f"AI Agent initialized: {config.agent_name} v{config.agent_version}")
    
    async def process_prompt(self, prompt: str) -> AgentResponse:
        """
        Main entry point: process user prompt and execute required tasks
        
        Args:
            prompt: User's request/prompt
            
        Returns:
            AgentResponse with results of all executed tasks
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Processing prompt: {prompt[:100]}...")
            
            # Step 1: Analyze the prompt
            analysis = await self.llm_service.analyze_prompt(prompt)
            logger.info(f"Prompt analysis: {analysis.get('task_type', 'unknown')}")
            
            # Step 2: Execute tasks based on analysis
            task_results = []
            search_results = None
            generated_documents = None
            
            # Web search if needed
            if analysis.get('search_queries'):
                search_task = await self._execute_search_task(analysis['search_queries'])
                task_results.append(search_task)
                if search_task.success:
                    search_results = search_task.data
            
            # Document generation if needed
            if analysis.get('document_types'):
                doc_task = await self._execute_document_generation_task(
                    prompt, analysis, search_results
                )
                task_results.append(doc_task)
                if doc_task.success:
                    generated_documents = doc_task.data
            
            # API queries if needed (placeholder for custom APIs)
            if analysis.get('api_endpoints'):
                api_task = await self._execute_api_task(analysis['api_endpoints'])
                task_results.append(api_task)
            
            total_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResponse(
                prompt=prompt,
                analysis=analysis,
                search_results=search_results,
                generated_documents=generated_documents,
                task_results=task_results,
                total_execution_time=total_time,
                success=True
            )
            
        except Exception as e:
            total_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Agent processing failed: {e}")
            
            return AgentResponse(
                prompt=prompt,
                analysis={},
                total_execution_time=total_time,
                success=False,
                error=str(e)
            )
    
    async def _execute_search_task(self, search_queries: List[str]) -> TaskResult:
        """Execute web search tasks"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Executing search for {len(search_queries)} queries")
            
            async with self.search_service as search:
                search_results = await search.search_multiple_queries(
                    search_queries, 
                    max_results_per_query=5
                )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Consolidate results
            consolidated_results = {
                'queries': search_queries,
                'results': search_results,
                'total_results': sum(r.total_results for r in search_results.values() if r.success),
                'successful_searches': sum(1 for r in search_results.values() if r.success)
            }
            
            return TaskResult(
                task_type="web_search",
                success=True,
                data=consolidated_results,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Search task failed: {e}")
            
            return TaskResult(
                task_type="web_search",
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def _execute_document_generation_task(
        self, 
        original_prompt: str, 
        analysis: Dict[str, Any],
        search_results: Optional[Dict[str, Any]] = None
    ) -> TaskResult:
        """Execute document generation tasks"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            document_types = analysis.get('document_types', ['general'])
            organizations = analysis.get('organizations', ['Default Organization'])
            
            logger.info(f"Generating {len(document_types)} document types for {len(organizations)} organizations")
            
            # Prepare context for document generation
            context = {
                'original_prompt': original_prompt,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'search_data': self._extract_search_context(search_results) if search_results else None
            }
            
            # Generate documents
            documents_to_generate = []
            
            # Create document combinations
            for doc_type in document_types:
                for org in organizations:
                    documents_to_generate.append({
                        'document_type': doc_type,
                        'organization': org,
                        'context': context
                    })
            
            # Special case for liquidation documents (based on user example)
            if any('liquid' in dt.lower() for dt in document_types) or 'liquid' in original_prompt.lower():
                documents_to_generate = await self._prepare_liquidation_documents(
                    original_prompt, context, organizations
                )
            
            # Generate document content using LLM
            document_contents = []
            for doc_spec in documents_to_generate:
                content = await self.llm_service.generate_document_content(
                    doc_spec['document_type'],
                    doc_spec['context'],
                    doc_spec['organization']
                )
                
                # Validate document if enabled
                if self.config.enable_validation:
                    validation = await self.llm_service.validate_document(
                        content, doc_spec['document_type']
                    )
                    doc_spec['validation'] = validation
                
                doc_spec['content'] = content
                document_contents.append(doc_spec)
            
            # Generate PDFs
            template_type = 'liquidation' if any('liquid' in dt.lower() for dt in document_types) else 'legal'
            pdf_results = await self.pdf_generator.generate_multiple_pdfs(
                document_contents, template_type
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Combine content and PDF results
            final_documents = []
            for i, (doc_spec, pdf_result) in enumerate(zip(document_contents, pdf_results)):
                final_documents.append({
                    'document_type': doc_spec['document_type'],
                    'organization': doc_spec['organization'],
                    'content': doc_spec['content'],
                    'validation': doc_spec.get('validation'),
                    'pdf_result': pdf_result,
                    'file_path': str(pdf_result.file_path) if pdf_result.file_path else None
                })
            
            return TaskResult(
                task_type="document_generation",
                success=True,
                data={
                    'documents': final_documents,
                    'total_generated': len(final_documents),
                    'successful_pdfs': sum(1 for pdf in pdf_results if pdf.success)
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Document generation task failed: {e}")
            
            return TaskResult(
                task_type="document_generation",
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def _prepare_liquidation_documents(
        self, 
        prompt: str, 
        context: Dict[str, Any],
        organizations: List[str]
    ) -> List[Dict[str, Any]]:
        """Prepare specific liquidation document types"""
        
        # Based on the user's example and Australian liquidation requirements
        liquidation_doc_types = [
            'Liquidation Resolution',
            'Creditor Notification',
            'Liquidator Appointment Notice',
            'Director Statement',
            'Asset Realization Notice'
        ]
        
        # If user asked for 5 documents specifically
        if '5' in prompt:
            liquidation_doc_types = liquidation_doc_types[:5]
        
        documents = []
        for org in organizations:
            for doc_type in liquidation_doc_types:
                documents.append({
                    'document_type': doc_type,
                    'organization': org,
                    'context': {
                        **context,
                        'liquidation_type': 'voluntary',  # Default
                        'urgency': 'high',
                        'compliance_required': True
                    }
                })
        
        return documents
    
    async def _execute_api_task(self, api_endpoints: List[str]) -> TaskResult:
        """Execute custom API queries (placeholder)"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"API task with {len(api_endpoints)} endpoints")
            
            # Placeholder for custom API integration
            # This would be implemented based on specific API requirements
            
            results = {
                'endpoints': api_endpoints,
                'status': 'placeholder_implementation',
                'message': 'Custom API integration would be implemented here'
            }
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return TaskResult(
                task_type="api_query",
                success=True,
                data=results,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"API task failed: {e}")
            
            return TaskResult(
                task_type="api_query",
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def _extract_search_context(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant context from search results for document generation"""
        if not search_results or not search_results.get('results'):
            return {}
        
        # Consolidate search snippets and sources
        all_snippets = []
        sources = []
        
        for query, response in search_results['results'].items():
            if response.success:
                for result in response.results[:3]:  # Top 3 results per query
                    all_snippets.append(f"{result.title}: {result.snippet}")
                    sources.append(result.url)
        
        return {
            'search_snippets': all_snippets[:10],  # Limit context size
            'sources': sources[:10],
            'search_summary': f"Found information from {len(sources)} sources across {len(search_results['results'])} searches"
        }
    
    async def generate_summary_report(self, response: AgentResponse) -> str:
        """Generate a summary report of agent execution"""
        
        summary_parts = [
            f"AI Agent Execution Report",
            f"========================",
            f"",
            f"Prompt: {response.prompt[:200]}{'...' if len(response.prompt) > 200 else ''}",
            f"",
            f"Analysis:",
            f"- Task Type: {response.analysis.get('task_type', 'unknown')}",
            f"- Complexity: {response.analysis.get('complexity', 'unknown')}",
            f"- Urgency: {response.analysis.get('urgency', 'unknown')}",
            f"",
            f"Execution Results:",
        ]
        
        if response.task_results:
            for i, task in enumerate(response.task_results, 1):
                status = "✓ Success" if task.success else "✗ Failed"
                time_str = f"{task.execution_time:.2f}s" if task.execution_time else "N/A"
                summary_parts.append(f"{i}. {task.task_type}: {status} ({time_str})")
                
                if task.error:
                    summary_parts.append(f"   Error: {task.error}")
        
        if response.generated_documents:
            doc_count = response.generated_documents.get('total_generated', 0)
            pdf_count = response.generated_documents.get('successful_pdfs', 0)
            summary_parts.extend([
                f"",
                f"Documents Generated: {doc_count}",
                f"PDFs Created: {pdf_count}",
            ])
        
        if response.search_results:
            search_count = response.search_results.get('successful_searches', 0)
            result_count = response.search_results.get('total_results', 0)
            summary_parts.extend([
                f"",
                f"Web Searches: {search_count}",
                f"Search Results: {result_count}",
            ])
        
        total_time = response.total_execution_time or 0
        summary_parts.extend([
            f"",
            f"Total Execution Time: {total_time:.2f} seconds",
            f"Overall Status: {'Success' if response.success else 'Failed'}",
        ])
        
        if response.error:
            summary_parts.extend([
                f"",
                f"Error: {response.error}"
            ])
        
        return "\n".join(summary_parts)
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up AI Agent resources")
        
        # Cancel any active tasks
        for task in self._active_tasks.values():
            if not task.done():
                task.cancel()
        
        # Wait for cleanup with timeout
        if self._active_tasks:
            await asyncio.wait(self._active_tasks.values(), timeout=5.0)
        
        self._active_tasks.clear()
        logger.info("AI Agent cleanup completed") 