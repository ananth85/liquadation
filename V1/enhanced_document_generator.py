#!/usr/bin/env python3
"""
Enhanced Document Generator with Intelligent Template Selection and LLM-Driven Content Generation

This script demonstrates how to use the intelligent template system to:
1. Understand user prompts using LLM
2. Dynamically select appropriate templates from 155 unique options
3. Fill templates with contextual, LLM-generated data
4. Produce unique, relevant liquidation documents
"""

import asyncio
import logging
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Import our enhanced agents
from agents.llm_generation_agent import LLMGenerationAgent
from agents.intelligent_template_agent import IntelligentTemplateAgent
from agents.pdf_generation_agent import PDFGenerationAgent

class EnhancedDocumentGenerator:
    """
    Enhanced Document Generator that uses LLM to understand prompts and generate unique documents
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Initialize agents
        self.llm_agent = self._initialize_llm_agent()
        self.template_agent = IntelligentTemplateAgent(
            templates_dir=self.config.get('templates_folder', 'templates'),
            llm_agent=self.llm_agent,
            logger=self.logger
        )
        self.pdf_agent = PDFGenerationAgent(logger=self.logger)
        
        # Output directory
        self.output_dir = Path(self.config.get('output_dir', 'output_pdfs'))
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger.info("Enhanced Document Generator initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('document_generation.log')
            ]
        )
        return logging.getLogger(__name__)

    def _initialize_llm_agent(self) -> LLMGenerationAgent:
        """Initialize LLM agent with configuration"""
        llm_config = {
            'api_key': os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY'),
            'base_url': os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1'),
            'model': os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
            'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '4000')),
            'temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
            'timeout': int(os.getenv('LLM_TIMEOUT', '30'))
        }
        
        return LLMGenerationAgent(
            api_key=llm_config['api_key'],
            base_url=llm_config['base_url'],
            model=llm_config['model'],
            max_tokens=llm_config['max_tokens'],
            temperature=llm_config['temperature'],
            timeout=llm_config['timeout'],
            logger=self.logger
        )

    async def generate_document_from_prompt(self, prompt: str, output_filename: str = None) -> Dict[str, Any]:
        """
        Generate a unique liquidation document from a user prompt
        
        Args:
            prompt: Natural language description of the liquidation scenario
            output_filename: Optional custom filename for output
            
        Returns:
            Dictionary with generation results and file paths
        """
        self.logger.info(f"Starting enhanced document generation for prompt: {prompt[:100]}...")
        
        try:
            # Step 1: Use intelligent template agent for full pipeline
            from agents.base_agent import AgentTask, AgentStatus
            import uuid
            
            task = AgentTask(
                task_id=str(uuid.uuid4()),
                task_type="intelligent_document_generation",
                input_data={"prompt": prompt},
                status=AgentStatus.IDLE
            )
            generation_result = await self.template_agent.process_task(task)
            
            if not generation_result.get("success"):
                self.logger.error(f"Document generation failed: {generation_result.get('error')}")
                return generation_result
            
            # Step 2: Generate PDF from HTML
            html_content = generation_result["document_html"]
            
            # Create output filename
            if not output_filename:
                company_name = generation_result["generated_data"].get("company_name", "Unknown_Company")
                safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"liquidation_{safe_name.replace(' ', '_')}_{timestamp}"
            
            # Generate PDF
            pdf_result = await self._generate_pdf(html_content, output_filename)
            
            # Step 3: Save metadata and results
            metadata = {
                "generation_timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "template_used": generation_result["template_used"],
                "generated_data": generation_result["generated_data"],
                "prompt_analysis": generation_result["prompt_analysis"],
                "generation_stats": generation_result["generation_stats"],
                "files": {
                    "pdf": pdf_result.get("pdf_file"),
                    "html": pdf_result.get("html_file"),
                    "metadata": f"{output_filename}_metadata.json"
                }
            }
            
            # Save metadata
            metadata_file = self.output_dir / f"{output_filename}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            self.logger.info(f"Successfully generated document: {pdf_result.get('pdf_file')}")
            
            return {
                "success": True,
                "files": metadata["files"],
                "metadata": metadata,
                "summary": {
                    "company_name": generation_result["generated_data"].get("company_name"),
                    "industry": generation_result["generated_data"].get("industry"),
                    "template": generation_result["template_used"]["template_id"],
                    "uniqueness_score": generation_result["generation_stats"]["uniqueness_indicators"]["uniqueness_score"],
                    "data_source": generation_result["generation_stats"]["data_source"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced document generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_pdf(self, html_content: str, filename: str) -> Dict[str, Any]:
        """Generate PDF from HTML content"""
        try:
            from agents.base_agent import AgentTask, AgentStatus
            import uuid
            
            # Save HTML file
            html_file = self.output_dir / f"{filename}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate PDF using PDF agent
            pdf_task = AgentTask(
                task_id=str(uuid.uuid4()),
                task_type="generate_pdf",
                input_data={
                    "content": html_content,
                    "output_path": str(self.output_dir / f"{filename}.pdf"),
                    "options": {
                        "page_size": "A4",
                        "orientation": "portrait",
                        "margins": {"top": 20, "bottom": 20, "left": 20, "right": 20}
                    }
                },
                status=AgentStatus.IDLE
            )
            
            pdf_result = await self.pdf_agent.process_task(pdf_task)
            
            if pdf_result.get("success"):
                return {
                    "success": True,
                    "pdf_file": f"{filename}.pdf",
                    "html_file": f"{filename}.html",
                    "file_size": pdf_result.get("file_size", 0)
                }
            else:
                self.logger.error(f"PDF generation failed: {pdf_result.get('error')}")
                return {"success": False, "error": pdf_result.get("error")}
                
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def generate_multiple_documents(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """Generate multiple documents from a list of prompts"""
        results = []
        
        for i, prompt in enumerate(prompts, 1):
            self.logger.info(f"Generating document {i}/{len(prompts)}")
            
            try:
                result = await self.generate_document_from_prompt(
                    prompt, 
                    output_filename=f"batch_document_{i:03d}"
                )
                results.append(result)
                
                # Add delay between generations to avoid rate limiting
                if i < len(prompts):
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Failed to generate document {i}: {e}")
                results.append({"success": False, "error": str(e), "prompt": prompt})
        
        return results

    async def analyze_template_coverage(self) -> Dict[str, Any]:
        """Analyze coverage of the 155 unique templates"""
        template_metadata = self.template_agent.template_metadata
        
        if not template_metadata:
            return {"error": "No template metadata available"}
        
        # Analyze coverage by industry, location, style
        industries = {}
        locations = {}
        styles = {}
        
        for template_id, metadata in template_metadata.items():
            industry = metadata.get("industry", "Unknown")
            location = metadata.get("state", "Unknown")
            style = metadata.get("style", "Unknown")
            
            industries[industry] = industries.get(industry, 0) + 1
            locations[location] = locations.get(location, 0) + 1
            styles[style] = styles.get(style, 0) + 1
        
        return {
            "total_templates": len(template_metadata),
            "coverage": {
                "industries": dict(sorted(industries.items())),
                "locations": dict(sorted(locations.items())),
                "styles": dict(sorted(styles.items()))
            },
            "unique_combinations": len(template_metadata),
            "recommendations": self._get_coverage_recommendations(industries, locations, styles)
        }

    def _get_coverage_recommendations(self, industries: Dict, locations: Dict, styles: Dict) -> List[str]:
        """Get recommendations for improving template coverage"""
        recommendations = []
        
        # Check for underrepresented categories
        min_industry_count = min(industries.values()) if industries else 0
        min_location_count = min(locations.values()) if locations else 0
        min_style_count = min(styles.values()) if styles else 0
        
        if min_industry_count < 3:
            underrep_industries = [k for k, v in industries.items() if v == min_industry_count]
            recommendations.append(f"Consider adding more templates for: {', '.join(underrep_industries)}")
        
        if min_location_count < 10:
            underrep_locations = [k for k, v in locations.items() if v == min_location_count]
            recommendations.append(f"Consider adding more templates for: {', '.join(underrep_locations)}")
        
        if len(styles) < 8:
            recommendations.append("Consider adding more visual style variations")
        
        return recommendations

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "llm_agent": {
                "available": self.llm_agent.client is not None,
                "model": self.llm_agent.model,
                "base_url": self.llm_agent.base_url
            },
            "template_agent": {
                "templates_loaded": len(self.template_agent.template_registry),
                "metadata_loaded": len(self.template_agent.template_metadata),
                "unique_templates_dir": str(self.template_agent.unique_templates_dir)
            },
            "pdf_agent": {
                "available": True,
                "capabilities": self.pdf_agent.get_capabilities()
            },
            "output_directory": str(self.output_dir),
            "configuration": {
                "llm_model": os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
                "use_unique_templates": os.getenv('USE_UNIQUE_TEMPLATES', 'true'),
                "dynamic_content": os.getenv('DYNAMIC_CONTENT_GENERATION', 'true')
            }
        }


async def main():
    """
    Demo script showing how to use the enhanced document generator
    """
    print("=== Enhanced Document Generator Demo ===\n")
    
    # Initialize generator
    generator = EnhancedDocumentGenerator()
    
    # Check system status
    status = generator.get_system_status()
    print(f"System Status:")
    print(f"- LLM Available: {status['llm_agent']['available']}")
    print(f"- Templates Loaded: {status['template_agent']['templates_loaded']}")
    print(f"- Model: {status['llm_agent']['model']}")
    print()
    
    # Demo prompts that should generate unique documents
    demo_prompts = [
        "Generate liquidation documents for TechFlow Solutions Pty Ltd, a fintech startup in Sydney that failed to secure Series B funding and is facing insolvency due to high burn rate",
        
        "Create liquidation paperwork for Melbourne Metro Construction, a medium-sized construction company in Victoria that's been hit by cost overruns on major projects and supply chain disruptions",
        
        "I need liquidation documents for Green Valley Organic Farms, a small agricultural business in Queensland that's struggling with drought conditions and rising operational costs",
        
        "Generate liquidation papers for Perth Digital Marketing Services, a professional services company in WA that lost its major clients and can't cover monthly expenses",
        
        "Create docs for Adelaide Auto Parts Manufacturing, a family-owned business in SA that's facing bankruptcy due to import competition and declining local demand"
    ]
    
    # Analyze template coverage
    print("Analyzing template coverage...")
    coverage = await generator.analyze_template_coverage()
    if "total_templates" in coverage:
        print(f"- Total templates available: {coverage['total_templates']}")
        print(f"- Industries covered: {len(coverage['coverage']['industries'])}")
        print(f"- Locations covered: {len(coverage['coverage']['locations'])}")
        print(f"- Visual styles: {len(coverage['coverage']['styles'])}")
    print()
    
    # Generate documents from prompts
    print("Generating unique documents from prompts...\n")
    
    for i, prompt in enumerate(demo_prompts, 1):
        print(f"Document {i}: {prompt[:80]}...")
        
        result = await generator.generate_document_from_prompt(prompt)
        
        if result["success"]:
            summary = result["summary"]
            print(f"✅ Generated: {summary['company_name']}")
            print(f"   Industry: {summary['industry']}")
            print(f"   Template: {summary['template']}")
            print(f"   Uniqueness: {summary['uniqueness_score']:.2f}")
            print(f"   Data Source: {summary['data_source']}")
            print(f"   Files: {result['files']['pdf']}")
        else:
            print(f"❌ Failed: {result.get('error')}")
        
        print()
        
        # Small delay between generations
        await asyncio.sleep(0.5)
    
    print("=== Demo Complete ===")
    print(f"Check the {generator.output_dir} folder for generated documents")


if __name__ == "__main__":
    # Instructions for setup
    print("Enhanced Document Generator")
    print("=" * 50)
    print()
    print("SETUP INSTRUCTIONS:")
    print("1. Copy config_example.env to .env")
    print("2. Add your OpenAI API key to .env:")
    print("   LLM_API_KEY=your_openai_api_key_here")
    print("3. Ensure you have the 155 unique templates in templates/unique_templates/")
    print("4. Run this script to generate unique, contextual documents")
    print()
    print("WITHOUT API KEY: The system will use enhanced fallback generation")
    print("WITH API KEY: The system will use LLM for maximum uniqueness and context")
    print()
    
    # Check if API key is configured
    api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY')
    if api_key and api_key != "your_openai_api_key_here":
        print("✅ API key detected - LLM-enhanced generation will be used")
    else:
        print("⚠️  No API key detected - enhanced fallback generation will be used")
        print("   (Still generates unique documents, but less contextual)")
    
    print()
    input("Press Enter to start the demo...")
    
    asyncio.run(main()) 