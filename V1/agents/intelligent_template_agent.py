#!/usr/bin/env python3
"""
Intelligent Template Agent - Enhanced Template Selection and Content Generation
Uses LLM to understand prompts and dynamically select and fill templates with unique data
"""

import asyncio
import json
import os
import random
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .base_agent import BaseAgent, AgentTask
from .llm_generation_agent import LLMGenerationAgent

class IntelligentTemplateAgent(BaseAgent):
    """
    Intelligent Template Agent that:
    1. Uses LLM to understand user prompts
    2. Dynamically selects appropriate templates from the 155 unique templates
    3. Fills templates with LLM-generated contextual data
    4. Ensures each document is unique and relevant
    """
    
    def __init__(self, templates_dir: str = "templates", llm_agent: Optional[LLMGenerationAgent] = None, 
                 logger: Optional[logging.Logger] = None):
        super().__init__("IntelligentTemplateAgent", logger)
        self.templates_dir = Path(templates_dir)
        self.unique_templates_dir = self.templates_dir / "unique_templates"
        self.llm_agent = llm_agent
        
        # Load template registry and metadata
        self.template_registry = {}
        self.template_metadata = {}
        self._load_template_registry()
        
        self.logger.info(f"Loaded {len(self.template_registry)} unique templates")

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "intelligent_document_generation",
            "analyze_prompt_requirements", 
            "select_optimal_template",
            "generate_contextual_data",
            "fill_template_dynamically"
        ]

    def _load_template_registry(self):
        """Load all unique templates and their metadata"""
        if not self.unique_templates_dir.exists():
            self.logger.warning("Unique templates directory not found")
            return
        
        # Load templates
        for template_file in self.unique_templates_dir.glob("liquidation_*.j2"):
            template_id = template_file.stem
            self.template_registry[template_id] = template_file
        
        # Load metadata
        for metadata_file in self.unique_templates_dir.glob("metadata_*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    template_id = f"liquidation_{metadata['template_number']:03d}_{metadata['industry'].lower().replace(' ', '_')}_{metadata['state'].lower()}_{metadata['style']}"
                    self.template_metadata[template_id] = metadata
            except Exception as e:
                self.logger.error(f"Failed to load metadata {metadata_file}: {e}")

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process intelligent template tasks"""
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "intelligent_document_generation":
            return await self._intelligent_document_generation(input_data)
        elif task_type == "analyze_prompt_requirements":
            return await self._analyze_prompt_requirements(input_data)
        elif task_type == "select_optimal_template":
            return await self._select_optimal_template(input_data)
        elif task_type == "generate_contextual_data":
            return await self._generate_contextual_data(input_data)
        elif task_type == "fill_template_dynamically":
            return await self._fill_template_dynamically(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _intelligent_document_generation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main intelligent document generation pipeline"""
        prompt = input_data.get("prompt", "")
        if not prompt:
            return {"success": False, "error": "No prompt provided"}
        
        self.logger.info(f"Starting intelligent document generation for: {prompt[:100]}...")
        
        try:
            # Step 1: Analyze prompt to understand requirements
            prompt_analysis = await self._analyze_prompt_requirements({"prompt": prompt})
            if not prompt_analysis["success"]:
                return prompt_analysis
            
            requirements = prompt_analysis["requirements"]
            self.logger.info(f"Identified requirements: {requirements['industry']} company in {requirements['location']}")
            
            # Step 2: Select optimal template based on requirements
            template_selection = await self._select_optimal_template({"requirements": requirements})
            if not template_selection["success"]:
                return template_selection
            
            selected_template = template_selection["template"]
            self.logger.info(f"Selected template: {selected_template['template_id']} ({selected_template['industry']} - {selected_template['style']})")
            
            # Step 3: Generate contextual data using LLM
            contextual_data = await self._generate_contextual_data({
                "prompt": prompt,
                "requirements": requirements,
                "template": selected_template
            })
            if not contextual_data["success"]:
                return contextual_data
            
            # Step 4: Fill template with generated data
            filled_template = await self._fill_template_dynamically({
                "template": selected_template,
                "data": contextual_data["data"],
                "requirements": requirements
            })
            
            return {
                "success": True,
                "document_html": filled_template["rendered_html"],
                "template_used": selected_template,
                "generated_data": contextual_data["data"],
                "prompt_analysis": requirements,
                "generation_stats": {
                    "template_count": len(self.template_registry),
                    "selection_score": template_selection.get("selection_score", 0),
                    "data_source": contextual_data.get("source", "fallback"),
                    "uniqueness_indicators": self._calculate_uniqueness_indicators(contextual_data["data"])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Intelligent document generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _analyze_prompt_requirements(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze prompt and extract specific requirements"""
        prompt = input_data.get("prompt", "")
        
        if self.llm_agent and self.llm_agent.client:
            # Use LLM for sophisticated prompt analysis
            analysis_prompt = f"""
Analyze this liquidation document generation request and extract specific requirements:

User Request: "{prompt}"

Extract and return a JSON response with these fields:
{{
    "company_name": "extracted or null if not specified",
    "industry": "specific industry sector",
    "location": "Australian state/city or null",
    "company_size": "small/medium/large based on context",
    "liquidation_reason": "primary reason category",
    "urgency": "immediate/standard/planning",
    "document_style": "formal/corporate/minimal preference",
    "specific_requirements": ["any specific mentions"],
    "financial_indicators": {{
        "debt_level": "estimated range",
        "asset_type": "primary assets mentioned"
    }},
    "complexity": "simple/standard/complex"
}}

Be specific and extract as much detail as possible from the user's language and context.
"""
            
            try:
                llm_result = await self.llm_agent.generate_from_prompt(analysis_prompt)
                if llm_result["success"] and "data" in llm_result:
                    # Parse LLM response for requirements
                    llm_data = llm_result["data"]
                    requirements = {
                        "company_name": llm_data.get("company_name"),
                        "industry": llm_data.get("industry", "Professional Services"),
                        "location": llm_data.get("location", "NSW"),
                        "company_size": llm_data.get("company_size", "small"),
                        "liquidation_reason": llm_data.get("liquidation_reason", "financial"),
                        "urgency": llm_data.get("urgency", "standard"),
                        "document_style": llm_data.get("document_style", "formal"),
                        "specific_requirements": llm_data.get("specific_requirements", []),
                        "financial_indicators": llm_data.get("financial_indicators", {}),
                        "complexity": llm_data.get("complexity", "standard"),
                        "analysis_source": "llm"
                    }
                    
                    return {"success": True, "requirements": requirements}
            except Exception as e:
                self.logger.warning(f"LLM prompt analysis failed, using fallback: {e}")
        
        # Fallback analysis using keyword matching
        requirements = await self._fallback_prompt_analysis(prompt)
        return {"success": True, "requirements": requirements}

    async def _fallback_prompt_analysis(self, prompt: str) -> Dict[str, Any]:
        """Fallback prompt analysis using keyword matching"""
        prompt_lower = prompt.lower()
        
        # Industry detection
        industry_keywords = {
            'tech': 'Technology Services',
            'technology': 'Technology Services',
            'software': 'Software Development',
            'fintech': 'Financial Services',
            'retail': 'Retail Trade',
            'construction': 'Construction',
            'restaurant': 'Food and Beverage',
            'consulting': 'Professional Services',
            'manufacturing': 'Manufacturing',
            'healthcare': 'Healthcare',
            'mining': 'Mining and Resources',
            'agriculture': 'Agriculture',
            'transport': 'Transport and Logistics',
            'education': 'Education Services',
            'tourism': 'Tourism and Hospitality',
            'automotive': 'Automotive',
            'fashion': 'Fashion and Textiles',
            'real estate': 'Real Estate',
            'media': 'Media and Communications'
        }
        
        industry = 'Professional Services'
        for keyword, industry_name in industry_keywords.items():
            if keyword in prompt_lower:
                industry = industry_name
                break
        
        # Location detection
        location_keywords = {
            'sydney': 'NSW', 'melbourne': 'VIC', 'brisbane': 'QLD',
            'perth': 'WA', 'adelaide': 'SA', 'hobart': 'TAS',
            'darwin': 'NT', 'canberra': 'ACT',
            'nsw': 'NSW', 'vic': 'VIC', 'qld': 'QLD',
            'wa': 'WA', 'sa': 'SA', 'tas': 'TAS', 'nt': 'NT', 'act': 'ACT'
        }
        
        location = 'NSW'
        for keyword, state_code in location_keywords.items():
            if keyword in prompt_lower:
                location = state_code
                break
        
        # Company size detection
        size_keywords = {
            'small': ['small', 'startup', 'new', 'boutique'],
            'medium': ['medium', 'growing', 'established'],
            'large': ['large', 'major', 'multinational', 'corporation']
        }
        
        company_size = 'small'
        for size, keywords in size_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                company_size = size
                break
        
        # Extract company name if mentioned
        company_name = None
        words = prompt.split()
        for i, word in enumerate(words):
            if any(suffix in word.lower() for suffix in ['ltd', 'limited', 'pty']):
                start_idx = max(0, i - 3)
                company_name = ' '.join(words[start_idx:i+1])
                break
        
        return {
            "company_name": company_name,
            "industry": industry,
            "location": location,
            "company_size": company_size,
            "liquidation_reason": "financial",
            "urgency": "standard",
            "document_style": "formal",
            "specific_requirements": [],
            "financial_indicators": {},
            "complexity": "standard",
            "analysis_source": "keyword_fallback"
        }

    async def _select_optimal_template(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select the most appropriate template based on requirements"""
        requirements = input_data.get("requirements", {})
        
        if not self.template_metadata:
            return {"success": False, "error": "No templates available"}
        
        # Score templates based on requirements match
        template_scores = {}
        
        for template_id, metadata in self.template_metadata.items():
            score = 0
            
            # Industry match (high weight)
            if metadata.get("industry", "").lower().replace(" ", "_") == requirements.get("industry", "").lower().replace(" ", "_"):
                score += 50
            elif requirements.get("industry", "").lower() in metadata.get("industry", "").lower():
                score += 25
            
            # Location match (medium weight)
            if metadata.get("state", "").lower() == requirements.get("location", "").lower():
                score += 30
            
            # Style preference match (medium weight)
            style_preferences = {
                "formal": ["formal_legal", "traditional_serif"],
                "corporate": ["modern_corporate", "professional_blue"],
                "minimal": ["minimal_clean", "contemporary_grid"]
            }
            
            preferred_styles = style_preferences.get(requirements.get("document_style", "formal"), ["formal_legal"])
            if metadata.get("style") in preferred_styles:
                score += 20
            
            # Company size consideration (low weight)
            if requirements.get("company_size") == "large" and "Holdings" in metadata.get("company_name", ""):
                score += 10
            elif requirements.get("company_size") == "small" and "Pty Ltd" in metadata.get("company_name", ""):
                score += 10
            
            # Random factor for variety (prevents always selecting same template)
            score += random.randint(0, 15)
            
            template_scores[template_id] = score
        
        # Select template with highest score
        if not template_scores:
            return {"success": False, "error": "No suitable templates found"}
        
        best_template_id = max(template_scores, key=template_scores.get)
        best_metadata = self.template_metadata[best_template_id]
        template_file = self.template_registry[best_template_id]
        
        selected_template = {
            "template_id": best_template_id,
            "template_file": str(template_file),
            "metadata": best_metadata,
            "industry": best_metadata.get("industry"),
            "state": best_metadata.get("state"),
            "style": best_metadata.get("style"),
            "selection_score": template_scores[best_template_id]
        }
        
        self.logger.info(f"Selected template {best_template_id} with score {template_scores[best_template_id]}")
        
        return {
            "success": True,
            "template": selected_template,
            "selection_score": template_scores[best_template_id],
            "alternatives": sorted(template_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        }

    async def _generate_contextual_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual data using LLM based on prompt and template"""
        prompt = input_data.get("prompt", "")
        requirements = input_data.get("requirements", {})
        template = input_data.get("template", {})
        
        if self.llm_agent and self.llm_agent.client:
            # Use LLM to generate rich, contextual data
            data_generation_prompt = f"""
Generate realistic and specific liquidation document data for an Australian company based on this scenario:

User Request: "{prompt}"

Company Requirements:
- Industry: {requirements.get('industry', 'Professional Services')}
- Location: {requirements.get('location', 'NSW')}
- Size: {requirements.get('company_size', 'small')}
- Template Style: {template.get('style', 'formal_legal')}

Generate comprehensive JSON data including:
{{
    "company_name": "Realistic Australian company name ending in Pty Ltd",
    "abn": "Valid format ABN (11 222 333 444)",
    "acn": "Valid format ACN (123 456 789)",
    "industry": "{requirements.get('industry', 'Professional Services')}",
    "entity_type": "Australian Private Company",
    "address": {{
        "street": "Realistic street address",
        "suburb": "Appropriate suburb for {requirements.get('location', 'NSW')}",
        "state": "{requirements.get('location', 'NSW')}",
        "postcode": "Correct postcode for location"
    }},
    "directors": ["2-4 realistic Australian names"],
    "liquidation_reason": "Detailed, industry-specific reason for liquidation",
    "liquidation_type": "Creditors' Voluntary Liquidation",
    "assets_value": "realistic amount for {requirements.get('company_size', 'small')} {requirements.get('industry', 'professional services')} company",
    "liabilities_value": "amount that creates insolvency",
    "major_creditors": ["3-5 realistic creditor names"],
    "liquidator": {{
        "name": "Professional liquidator name",
        "registration": "LIQ followed by numbers",
        "firm": "Liquidation firm name"
    }},
    "specific_circumstances": "Detailed explanation relevant to the user's prompt",
    "timeline": "Expected liquidation timeline",
    "employee_impact": "Number of employees affected",
    "creditor_impact": "Estimated creditor recovery percentage"
}}

Make all details realistic, specific, and directly relevant to: "{prompt}"
Ensure the liquidation scenario makes financial and legal sense for Australian corporate law.
"""
            
            try:
                llm_result = await self.llm_agent.generate_from_prompt(data_generation_prompt)
                if llm_result["success"] and "data" in llm_result:
                    # Enhance LLM data with additional calculated fields
                    enhanced_data = await self._enhance_generated_data(llm_result["data"], requirements)
                    return {
                        "success": True,
                        "data": enhanced_data,
                        "source": "llm_generated",
                        "uniqueness_score": self._calculate_uniqueness_score(enhanced_data)
                    }
            except Exception as e:
                self.logger.warning(f"LLM data generation failed, using enhanced fallback: {e}")
        
        # Enhanced fallback data generation
        fallback_data = await self._generate_enhanced_fallback_data(requirements, template)
        return {
            "success": True,
            "data": fallback_data,
            "source": "enhanced_fallback",
            "uniqueness_score": self._calculate_uniqueness_score(fallback_data)
        }

    async def _enhance_generated_data(self, base_data: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance LLM-generated data with additional calculated fields"""
        enhanced = base_data.copy()
        
        # Add current date formatting
        enhanced["current_date"] = datetime.now().strftime('%d %B %Y')
        enhanced["formatted_date"] = enhanced["current_date"]
        
        # Add financial calculations
        assets = enhanced.get("assets_value", 100000)
        liabilities = enhanced.get("liabilities_value", 200000)
        if isinstance(assets, str):
            assets = int(''.join(filter(str.isdigit, assets)) or 100000)
        if isinstance(liabilities, str):
            liabilities = int(''.join(filter(str.isdigit, liabilities)) or 200000)
        
        enhanced["assets_estimate"] = f"{assets:,}"
        enhanced["debts_estimate"] = f"{liabilities:,}"
        enhanced["deficiency_amount"] = f"{max(0, liabilities - assets):,}"
        
        # Add industry-specific enhancements
        industry = requirements.get("industry", "Professional Services")
        enhanced["industry_specific_assets"] = self._get_industry_assets(industry)
        enhanced["industry_specific_liabilities"] = self._get_industry_liabilities(industry)
        
        return enhanced

    async def _generate_enhanced_fallback_data(self, requirements: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced fallback data when LLM is not available"""
        from faker import Faker
        fake = Faker('en_AU')
        
        industry = requirements.get("industry", "Professional Services")
        location = requirements.get("location", "NSW")
        company_size = requirements.get("company_size", "small")
        
        # Generate realistic company name
        base_name = fake.company().replace(',', '').replace('.', '')
        suffixes = ["Pty Ltd", "Holdings Pty Ltd", "Services Pty Ltd", "Group Pty Ltd"]
        company_name = f"{base_name} {random.choice(suffixes)}"
        
        # Size-appropriate financial data
        size_multipliers = {
            "small": (50000, 500000),
            "medium": (200000, 2000000),
            "large": (1000000, 10000000)
        }
        
        min_debt, max_debt = size_multipliers.get(company_size, (50000, 500000))
        liabilities = random.randint(min_debt, max_debt)
        assets = int(liabilities * random.uniform(0.2, 0.6))  # Insolvent scenario
        
        return {
            "company_name": company_name,
            "abn": self._generate_abn(),
            "acn": self._generate_acn(),
            "industry": industry,
            "entity_type": "Australian Private Company",
            "address": self._generate_address(location),
            "directors": [fake.name() for _ in range(random.randint(2, 4))],
            "liquidation_reason": self._get_industry_liquidation_reason(industry),
            "liquidation_type": random.choice([
                "Creditors' Voluntary Liquidation",
                "Members' Voluntary Liquidation"
            ]),
            "assets_value": assets,
            "liabilities_value": liabilities,
            "assets_estimate": f"{assets:,}",
            "debts_estimate": f"{liabilities:,}",
            "deficiency_amount": f"{liabilities - assets:,}",
            "current_date": datetime.now().strftime('%d %B %Y'),
            "formatted_date": datetime.now().strftime('%d %B %Y'),
            "liquidator": {
                "name": fake.name(),
                "registration": f"LIQ{random.randint(10000, 99999)}",
                "firm": f"{fake.last_name()} & Associates"
            },
            "major_creditors": [
                {"name": f"{fake.company()} Pty Ltd", "amount": random.randint(10000, 50000)},
                {"name": "Australian Taxation Office", "amount": random.randint(5000, 25000)},
                {"name": f"{fake.company()} Bank", "amount": random.randint(20000, 100000)}
            ]
        }

    async def _fill_template_dynamically(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill template with generated data"""
        template = input_data.get("template", {})
        data = input_data.get("data", {})
        
        template_file = template.get("template_file")
        if not template_file or not Path(template_file).exists():
            return {"success": False, "error": "Template file not found"}
        
        try:
            # Read template content
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Simple template filling (basic string replacement for key fields)
            filled_content = template_content
            
            # Replace template variables with actual data
            replacements = {
                "{{ company_name or 'Unknown Company' }}": data.get("company_name", "Unknown Company"),
                "{{ formatted_abn or abn or '11 111 111 111' }}": data.get("abn", "11 111 111 111"),
                "{{ formatted_acn or acn or '111 111 111' }}": data.get("acn", "111 111 111"),
                "{{ industry or 'Professional Services' }}": data.get("industry", "Professional Services"),
                "{{ state or 'NSW' }}": data.get("address", {}).get("state", "NSW"),
                "{{ liquidation_type or 'Creditors' Voluntary Liquidation' }}": data.get("liquidation_type", "Creditors' Voluntary Liquidation"),
                "{{ assets_estimate or '100,000' }}": data.get("assets_estimate", "100,000"),
                "{{ debts_estimate or '200,000' }}": data.get("debts_estimate", "200,000"),
                "{{ deficiency_amount or '100,000' }}": data.get("deficiency_amount", "100,000"),
                "{{ formatted_date or current_date }}": data.get("current_date", datetime.now().strftime('%d %B %Y')),
                "{{ liquidator_name or 'John Smith' }}": data.get("liquidator", {}).get("name", "John Smith"),
            }
            
            for placeholder, value in replacements.items():
                filled_content = filled_content.replace(placeholder, str(value))
            
            return {
                "success": True,
                "rendered_html": filled_content,
                "template_id": template.get("template_id"),
                "data_points_filled": len(replacements)
            }
            
        except Exception as e:
            self.logger.error(f"Template filling failed: {e}")
            return {"success": False, "error": str(e)}

    def _generate_abn(self) -> str:
        """Generate valid format ABN"""
        digits = [random.randint(0, 9) for _ in range(11)]
        return f"{digits[0]}{digits[1]} {digits[2]}{digits[3]}{digits[4]} {digits[5]}{digits[6]}{digits[7]} {digits[8]}{digits[9]}{digits[10]}"

    def _generate_acn(self) -> str:
        """Generate valid format ACN"""
        digits = [random.randint(0, 9) for _ in range(9)]
        return f"{digits[0]}{digits[1]}{digits[2]} {digits[3]}{digits[4]}{digits[5]} {digits[6]}{digits[7]}{digits[8]}"

    def _generate_address(self, state: str) -> Dict[str, str]:
        """Generate realistic address for given state"""
        from faker import Faker
        fake = Faker('en_AU')
        
        # State-specific postcodes
        postcodes = {
            "NSW": (2000, 2999),
            "VIC": (3000, 3999),
            "QLD": (4000, 4999),
            "WA": (6000, 6999),
            "SA": (5000, 5999),
            "TAS": (7000, 7999),
            "NT": (800, 899),
            "ACT": (2600, 2699)
        }
        
        postcode_range = postcodes.get(state, (2000, 2999))
        postcode = random.randint(*postcode_range)
        
        return {
            "street": fake.street_address(),
            "suburb": fake.city(),
            "state": state,
            "postcode": str(postcode)
        }

    def _get_industry_liquidation_reason(self, industry: str) -> str:
        """Get industry-specific liquidation reason"""
        industry_reasons = {
            "Technology Services": "Failed to secure Series B funding and increasing competition from established players",
            "Construction": "Major project delays and cost overruns leading to cash flow problems",
            "Retail Trade": "Declining foot traffic and inability to compete with online retailers",
            "Manufacturing": "Rising raw material costs and equipment maintenance expenses",
            "Professional Services": "Loss of key clients and inability to maintain overhead costs",
            "Healthcare": "Regulatory changes and increased compliance costs",
            "Mining and Resources": "Commodity price volatility and environmental compliance requirements"
        }
        
        return industry_reasons.get(industry, "Financial difficulties and cash flow problems")

    def _get_industry_assets(self, industry: str) -> List[str]:
        """Get industry-specific asset types"""
        industry_assets = {
            "Technology Services": ["Software licenses", "Computer equipment", "Intellectual property"],
            "Construction": ["Plant and machinery", "Work in progress", "Vehicles"],
            "Retail Trade": ["Inventory", "Shop fittings", "Point of sale systems"],
            "Manufacturing": ["Production equipment", "Raw materials", "Finished goods"],
            "Professional Services": ["Office equipment", "Client databases", "Professional licenses"]
        }
        
        return industry_assets.get(industry, ["Office equipment", "Computer systems", "Furniture"])

    def _get_industry_liabilities(self, industry: str) -> List[str]:
        """Get industry-specific liability types"""
        return ["Trade creditors", "Bank loans", "Employee entitlements", "Tax liabilities", "Lease obligations"]

    def _calculate_uniqueness_score(self, data: Dict[str, Any]) -> float:
        """Calculate uniqueness score for generated data"""
        unique_elements = 0
        total_elements = 0
        
        # Check for unique company name
        if data.get("company_name") and len(data["company_name"]) > 10:
            unique_elements += 1
        total_elements += 1
        
        # Check for specific liquidation reason
        if data.get("liquidation_reason") and len(data["liquidation_reason"]) > 50:
            unique_elements += 1
        total_elements += 1
        
        # Check for financial data variety
        if data.get("assets_value") and data.get("liabilities_value"):
            unique_elements += 1
        total_elements += 1
        
        return unique_elements / total_elements if total_elements > 0 else 0.0

    def _calculate_uniqueness_indicators(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various uniqueness indicators"""
        return {
            "has_specific_company_name": bool(data.get("company_name")),
            "has_detailed_liquidation_reason": len(data.get("liquidation_reason", "")) > 50,
            "has_realistic_financials": bool(data.get("assets_value") and data.get("liabilities_value")),
            "has_multiple_directors": len(data.get("directors", [])) > 1,
            "has_specific_address": bool(data.get("address", {}).get("street")),
            "uniqueness_score": self._calculate_uniqueness_score(data)
        } 