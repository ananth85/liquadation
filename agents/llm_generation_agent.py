#!/usr/bin/env python3
"""
Enhanced LLM Generation Agent for Liquidation Document Generation
Now includes 150 realistic liquidation reasons and dynamic clause generation
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentTask
import random

try:
    import openai
except ImportError:
    openai = None

class LLMGenerationAgent(BaseAgent):
    """Agent responsible for generating content using LLM or fallback methods"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", logger: Optional[logging.Logger] = None):
        super().__init__("LLMGenerationAgent", logger)
        self.client = None
        self.model = model
        
        if api_key and openai:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.logger.warning("No OpenAI API key provided - will use fallback synthetic generation")

    def get_capabilities(self) -> List[str]:
        return [
            "generate_from_prompt",
            "generate_company_details",
            "generate_liquidation_reason",
            "generate_document_content",
            "enhance_existing_data",
            "generate_dynamic_clauses",
            "generate_varied_structure"
        ]

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process LLM generation tasks"""
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "generate_from_prompt":
            return await self.generate_from_prompt(input_data.get("prompt"))
        elif task_type == "generate_company_details":
            return await self.generate_company_details(input_data.get("industry"), input_data.get("location"))
        elif task_type == "generate_liquidation_reason":
            return await self.generate_liquidation_reason(input_data.get("company_data"))
        elif task_type == "generate_document_content":
            return await self.generate_document_content(input_data.get("document_type"), input_data.get("company_data"))
        elif task_type == "enhance_existing_data":
            return await self.enhance_existing_data(input_data.get("data"))
        elif task_type == "generate_dynamic_clauses":
            return await self.generate_dynamic_clauses(input_data)
        elif task_type == "generate_varied_structure":
            return await self.generate_varied_structure(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    # 150 Realistic Liquidation Reasons
    LIQUIDATION_REASONS = {
        "financial": [
            "Ongoing trading losses", "Unsustainable debt levels", "Inability to repay loans",
            "Cash flow problems", "Poor financial planning", "Over-leveraging of assets",
            "Declining profit margins", "Failure to secure additional funding", "Non-payment from key clients",
            "High fixed operational costs", "Bad debt accumulation", "Poor accounts receivable turnover",
            "Unrecoverable investments", "Insolvency due to tax liabilities", "Cost overruns on major projects",
            "Late supplier payments", "Excessive interest burden", "Failed product launches",
            "Overdependence on a single client", "Lack of working capital"
        ],
        "market": [
            "Market saturation", "Increased competition", "Loss of market share",
            "Collapse of customer demand", "Regulatory changes affecting pricing", "Economic downturn",
            "COVID-19 pandemic impact", "Brexit-related market barriers", "Import/export restrictions",
            "Global supply chain disruptions", "Industry-specific downturn", "Decline in raw material availability",
            "Trade war impacts", "Unfavourable currency exchange rates", "Commodity price volatility",
            "Entry of large foreign competitors", "Seasonal business failure", "Trend shifts away from products",
            "Obsolescence of offerings", "Poor marketing ROI"
        ],
        "operational": [
            "Poor management decisions", "Director disputes", "Misappropriation of funds",
            "Lack of internal controls", "Fraud or embezzlement", "HR mismanagement",
            "Disorganised accounting", "Employee strikes", "Inability to attract skilled staff",
            "Conflict of interest at board level", "Misuse of company resources", "Overstaffing",
            "Inefficient procurement process", "Failed ERP implementation", "Poor inventory management",
            "Overexpansion", "Lack of risk mitigation strategy", "Disorganised project execution",
            "Lack of succession planning", "Poor vendor management"
        ],
        "legal": [
            "Breach of statutory obligations", "Lawsuits from customers", "Tax evasion penalties",
            "ASIC investigations", "Product liability claims", "Non-compliance with workplace laws",
            "Regulatory bans", "Occupational health & safety violations", "Anti-competitive practices",
            "Intellectual property disputes", "Trademark infringement fines", "Privacy law breaches (e.g., GDPR)",
            "False advertising claims", "Breach of director duties", "Environmental violations",
            "Pending litigation exposure", "License revocation", "Unlawful trading allegations",
            "Government sanctions", "Failure to lodge annual returns"
        ],
        "strategic": [
            "Business model no longer viable", "Strategic pivot to new entity", "Exit from Australian market",
            "Post-merger wind-down", "Rebranding as new corporate identity", "Shareholder resolution to dissolve",
            "Simplifying business structure", "Voluntary deregistration of dormant arm", "Parent company shut-down",
            "Transfer of business to new trust", "Consolidation of multiple entities", "Termination of franchise agreement",
            "Finalisation of a joint venture", "Migration to online-only operations", "Outsourcing core services",
            "Discontinuation of a product line", "Spin-off failure", "Divestment of non-core asset",
            "Lease expiration with no renewal", "Strategic bankruptcy to reduce liabilities"
        ],
        "technology": [
            "Inability to digitise operations", "Cyberattack leading to operational halt", "Obsolete IT systems",
            "Failed cloud migration", "High cost of innovation", "Poor app or software deployment",
            "Failed automation initiative", "Lack of e-commerce strategy", "AI integration failures",
            "Competitors' superior tech edge", "Poor cybersecurity posture", "Data loss incident",
            "Loss of intellectual property", "Negative tech reviews affecting brand", "Infrastructure collapse due to bugs"
        ],
        "reputation": [
            "Loss of major customer contracts", "Damaging media scandal", "Public relations crisis",
            "Product recalls", "Fake reviews and market backlash", "Poor customer support reputation",
            "Failure to adapt to customer feedback", "Allegations of unethical business", "Negative ESG ratings",
            "Mass customer migration to competitor", "Poor product quality", "Breach of customer data",
            "Lack of innovation", "Inconsistent brand messaging", "Outdated service delivery model"
        ],
        "external": [
            "Disruption from third-party failure", "Poor legal counsel", "Mistakes by financial auditor",
            "Delay in government approvals", "Unfavourable zoning changes", "Failure to secure tenancy renewals",
            "Poor outsourcing partner performance", "Negative ASX delisting", "Supplier insolvency",
            "Failure to meet ISO certification", "External political instability", "Import licensing failure",
            "Customs clearance delays", "Loss of distributor network", "Failure in product compliance testing",
            "Delay in contract award decisions", "Retirement of key directors", "Inherited legacy liabilities",
            "Board decision to exit Australia", "Collapse of overseas parent company"
        ]
    }

    # Dynamic Legal Clause Templates
    LEGAL_CLAUSE_TEMPLATES = {
        "insolvency_declarations": [
            "That the company is insolvent within the meaning of section 95A of the Corporations Act 2001 (Cth), being unable to pay its debts as and when they fall due from its own money.",
            "That the directors have formed the opinion that the company cannot by reason of its liabilities continue its business and there is no reasonable prospect of the company being able to pay its debts.",
            "That after careful consideration of the company's financial position, the directors are satisfied that the company is insolvent and cannot meet its obligations as they fall due.",
            "That the company has failed the cash flow test under section 95A of the Corporations Act, being unable to pay all debts as and when they become due and payable.",
            "That the company is balance sheet insolvent, with liabilities exceeding assets on both book and market value bases."
        ],
        "liquidation_resolutions": [
            "That the company be wound up by way of {liquidation_type} pursuant to sections 491-494 of the Corporations Act 2001 (Cth).",
            "That it is resolved to wind up the company voluntarily under Chapter 5 of the Corporations Act 2001 (Cth).",
            "That the company cease trading immediately and commence the process of voluntary liquidation in accordance with the Corporations Act.",
            "That the winding up of the company be commenced forthwith by way of {liquidation_type} under the provisions of the Corporations Act 2001.",
            "That this company be dissolved by way of voluntary liquidation pursuant to the applicable provisions of Australian corporate law."
        ],
        "liquidator_appointments": [
            "That {liquidator_name} (Registration No. {liquidator_registration}) be appointed as liquidator of the company effective from {date}.",
            "That {liquidator_name}, being a registered liquidator within the meaning of the Corporations Act, be and is hereby appointed liquidator of the company.",
            "That the appointment of {liquidator_name} as liquidator be confirmed, and that they be authorized to exercise all powers conferred by law.",
            "That {liquidator_name} (ASIC Registration {liquidator_registration}) be appointed to conduct the winding up of this company in accordance with statutory requirements.",
            "That {liquidator_name} be appointed as the official liquidator and be vested with full authority to realize assets and distribute proceeds to creditors."
        ],
        "director_powers": [
            "That the powers of the directors cease upon the appointment of the liquidator, except as may be required to assist the liquidator in the performance of their duties.",
            "That all director authorities and decision-making powers be transferred to the appointed liquidator with immediate effect.",
            "That the directors' management powers terminate upon liquidator appointment, save for cooperation obligations under the Corporations Act.",
            "That the board of directors be dissolved and all corporate governance transferred to the control of the liquidator.",
            "That directorial powers cease except where specifically retained by law or requested by the liquidator for administrative purposes."
        ],
        "asset_preservation": [
            "That all assets of the company be preserved and protected for the benefit of creditors until such time as they are realized by the liquidator.",
            "That no further disposal of company assets occur without the express written consent of the appointed liquidator.",
            "That all company property, including intellectual property rights, be secured and maintained pending liquidation proceedings.",
            "That the liquidator be granted immediate access to and control over all assets, bank accounts, and business records of the company.",
            "That asset preservation orders be implemented to prevent dissipation of company property during the liquidation process."
        ],
        "creditor_notifications": [
            "That notice of this resolution be given to all known creditors within the timeframes prescribed by the Corporations Act 2001 (Cth).",
            "That creditors be notified immediately of the liquidation and invited to submit proofs of debt in the prescribed form.",
            "That publication of the liquidation notice be made in the Government Gazette and local newspaper as required by law.",
            "That all creditor communications be handled through the liquidator in accordance with insolvency procedures.",
            "That creditor meetings be convened as required under sections 436E and 439A of the Corporations Act."
        ],
        "regulatory_compliance": [
            "That the required forms be lodged with the Australian Securities and Investments Commission (ASIC) within the prescribed timeframes.",
            "That all regulatory notifications be completed including Form 520 (Notification of Resolution) to ASIC within 14 days.",
            "That compliance with all Australian Taxation Office obligations be maintained throughout the liquidation process.",
            "That workplace entitlements and superannuation obligations be addressed in accordance with Fair Work legislation.",
            "That environmental compliance and safety obligations continue to be met during the wind-up period."
        ],
        "statutory_authorizations": [
            "That the liquidator be authorized to take all steps necessary to comply with the requirements of the Corporations Act 2001 (Cth) and all other applicable legislation.",
            "That full authority be granted to the liquidator to execute all documents and take all actions required for the proper conduct of the liquidation.",
            "That the liquidator be empowered to engage legal counsel, accountants, and other professionals as deemed necessary for the liquidation.",
            "That authorization be given for the liquidator to investigate the company's affairs and report to creditors and ASIC as required by law.",
            "That the liquidator be granted power to compromise debts, settle legal proceedings, and make distributions to creditors in accordance with statutory priorities."
        ],
        "cooperation_obligations": [
            "That the directors undertake to provide full cooperation and assistance to the liquidator in the performance of their statutory duties.",
            "That all current and former officers deliver up books, records, and company property to the liquidator immediately upon request.",
            "That directors make themselves available for examination under section 596A of the Corporations Act if required.",
            "That complete disclosure of all company affairs, transactions, and financial dealings be provided to the liquidator.",
            "That ongoing cooperation be maintained with any investigations conducted by the liquidator, ASIC, or other regulatory bodies."
        ]
    }

    async def generate_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate complete liquidation scenario from a free-form prompt"""
        if not prompt:
            raise ValueError("Prompt is required")

        if self.client:
            return await self._generate_with_openai(prompt)
        else:
            return await self._generate_fallback(prompt)

    async def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate content using OpenAI API"""
        try:
            system_prompt = """You are an expert Australian corporate law assistant specializing in company liquidations. 
            Generate realistic but synthetic liquidation scenarios for testing and training purposes.
            
            Always respond with valid JSON containing these fields:
            - company_name: realistic Australian company name
            - abn: valid 11-digit ABN
            - acn: valid 9-digit ACN (formatted as XXX XXX XXX)
            - entity_type: type of entity
            - directors: array of director names
            - registered_office: complete Australian address
            - liquidation_type: type of liquidation
            - reason_for_liquidation: brief reason
            - liquidation_reason_detailed: detailed explanation
            - liquidator_name: qualified liquidator name
            - creditors: array of creditor objects with name, amount, type
            - assets_estimate: estimated assets value
            - debts_estimate: estimated debts value
            - industry: business industry
            - date: liquidation date (YYYY-MM-DD format)
            
            Make all data realistic but clearly synthetic. Use Australian business conventions."""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                data = json.loads(content)
                return {
                    "success": True,
                    "source": "openai",
                    "model": self.model,
                    "data": data
                }
            except json.JSONDecodeError:
                # If not JSON, extract data manually
                return await self._extract_data_from_text(content, prompt)
                
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            return await self._generate_fallback(prompt)
    
    async def _extract_data_from_text(self, text: str, original_prompt: str) -> Dict[str, Any]:
        """Extract structured data from text response"""
        # Fallback data extraction if LLM doesn't return JSON
        from faker import Faker
        fake = Faker('en_AU')
        
        # Parse key information from text
        lines = text.split('\n')
        extracted = {}
        
        for line in lines:
            if 'company' in line.lower() and 'name' in line.lower():
                # Extract company name
                parts = line.split(':')
                if len(parts) > 1:
                    extracted['company_name'] = parts[1].strip()
                    
        # Generate structured data with extracted info
        return {
            "success": True,
            "source": "openai_extracted",
            "data": await self._generate_complete_scenario(
                extracted.get('company_name'),
                original_prompt
            )
        }
    
    async def _generate_fallback(self, prompt: str) -> Dict[str, Any]:
        """Generate content using comprehensive fallback with 150 reasons"""
        self.logger.info("Using enhanced fallback generation with 150 liquidation reasons")
        
        # Analyze prompt for keywords
        prompt_lower = prompt.lower()
        
        # Determine industry from prompt
        industry_keywords = {
            'tech': 'Technology Services',
            'fintech': 'Financial Technology', 
            'retail': 'Retail Trade',
            'construction': 'Construction',
            'restaurant': 'Food Service',
            'consulting': 'Professional Services',
            'manufacturing': 'Manufacturing',
            'healthcare': 'Healthcare Services',
            'mining': 'Mining and Resources',
            'agriculture': 'Agriculture and Farming',
            'transport': 'Transport and Logistics',
            'education': 'Education Services',
            'tourism': 'Tourism and Hospitality'
        }
        
        industry = 'Professional Services'  # default
        for keyword, industry_name in industry_keywords.items():
            if keyword in prompt_lower:
                industry = industry_name
                break
        
        # Determine location
        location_keywords = {
            'sydney': 'NSW', 'melbourne': 'VIC', 'brisbane': 'QLD',
            'perth': 'WA', 'adelaide': 'SA', 'hobart': 'TAS',
            'darwin': 'NT', 'canberra': 'ACT'
        }
        
        state = 'NSW'  # default
        for keyword, state_code in location_keywords.items():
            if keyword in prompt_lower:
                state = state_code
                break
        
        scenario = await self._generate_comprehensive_scenario(None, prompt, industry, state)
        
        return {
            "success": True,
            "source": "enhanced_fallback_with_150_reasons",
            "data": scenario
        }
    
    async def _generate_comprehensive_scenario(self, company_name: Optional[str] = None, 
                                            prompt: str = "", industry: str = "Professional Services", 
                                            state: str = "NSW") -> Dict[str, Any]:
        """Generate a comprehensive liquidation scenario with dynamic content"""
        from faker import Faker
        fake = Faker('en_AU')
        
        # Extract company name from prompt if provided
        if not company_name and prompt:
            words = prompt.split()
            for i, word in enumerate(words):
                if 'Ltd' in word or 'Limited' in word or 'Pty' in word:
                    start_idx = max(0, i - 3)
                    company_name = ' '.join(words[start_idx:i+1])
                    break
        
        if not company_name:
            base_name = fake.company().replace(',', '').replace('.', '')
            suffixes = ["Pty Ltd", "Limited", "Holdings Pty Ltd", "Group Pty Ltd", "Services Pty Ltd"]
            company_name = f"{base_name} {random.choice(suffixes)}"
        
        # Generate comprehensive financial data with more variation
        base_debt = random.randint(150000, 3500000)
        base_assets = int(base_debt * random.uniform(0.10, 0.60))  # More variation in asset ratios
        
        # Dynamic asset and liability generation based on industry
        assets_schedule, total_book_value, total_estimated_value = self._generate_dynamic_assets(industry, base_assets)
        liability_schedule = self._generate_dynamic_liabilities(industry, base_debt)
        
        # Select random liquidation reasons from the 150
        primary_category = self._select_reason_category(prompt, industry)
        primary_reasons = random.sample(self.LIQUIDATION_REASONS[primary_category], random.randint(2, 4))
        
        # Add secondary reasons from other categories
        secondary_categories = [cat for cat in self.LIQUIDATION_REASONS.keys() if cat != primary_category]
        secondary_category = random.choice(secondary_categories)
        secondary_reasons = random.sample(self.LIQUIDATION_REASONS[secondary_category], random.randint(1, 2))
        
        all_reasons = primary_reasons + secondary_reasons
        
        # Generate dynamic legal clauses (5-12 clauses)
        dynamic_clauses = self._generate_dynamic_legal_clauses()
        
        # Generate varied document structure
        document_structure = self._generate_document_structure()
        
        # Generate comprehensive detailed reason
        detailed_reason = self._generate_detailed_liquidation_reason(all_reasons, industry, company_name, base_debt, total_estimated_value)
        
        # Generate varied insolvency indicators
        insolvency_indicators = self._generate_insolvency_indicators(industry, all_reasons)
        
        # Generate dynamic liquidator details
        liquidator_details = self._generate_liquidator_details()
        
        # Generate address
        address = self._generate_address(state)
        
        return {
            "company_name": company_name,
            "abn": self._generate_valid_abn(),
            "acn": self._generate_acn(),
            "entity_type": random.choice(["Australian Private Company", "Public Company Limited by Shares", "Proprietary Limited Company"]),
            "directors": [fake.name() for _ in range(random.randint(2, 5))],
            "address": address,
            "registered_office": f"{address['street']}, {address['city']} {address['state']} {address['postcode']}",
            "liquidation_type": "Creditors' Voluntary Liquidation",
            "reason_for_liquidation": "; ".join(all_reasons[:3]),  # Primary reasons
            "liquidation_reason_detailed": detailed_reason,
            "liquidator_name": liquidator_details["name"],
            "liquidator_registration": liquidator_details["registration"],
            "liquidator_phone": liquidator_details["phone"],
            "liquidator_email": liquidator_details["email"],
            "creditors": self._generate_major_creditors(base_debt),
            "assets_estimate": f"{total_book_value:,}",
            "debts_estimate": f"{base_debt:,}",
            "estimated_realization": f"{total_estimated_value:,}",
            "assets_schedule": assets_schedule,
            "liability_schedule": liability_schedule,
            "cash_flow_issues": self._generate_cash_flow_issues(industry, all_reasons),
            "insolvency_indicators": insolvency_indicators,
            "dynamic_clauses": dynamic_clauses,
            "document_structure": document_structure,
            "liquidation_reasons_full": all_reasons,
            "primary_reason_category": primary_category,
            "industry": industry,
            "date": fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
            "email": f"info@{company_name.lower().replace(' ', '').replace('pty', '').replace('ltd', '')[:15]}.com.au",
            "phone": fake.phone_number(),
            "meeting_type": random.choice(["Board Meeting", "Directors' Meeting", "Special Resolution Meeting"]),
            "unanimous_decision": random.choice([True, False]),
            "resolution_number": f"RES-{random.randint(100, 999)}-{fake.date_this_year().strftime('%Y')}"
        }

    def _select_reason_category(self, prompt: str, industry: str) -> str:
        """Select primary reason category based on prompt and industry"""
        prompt_lower = prompt.lower()
        
        # Check for specific indicators in prompt
        if any(word in prompt_lower for word in ['debt', 'cash', 'funding', 'payment', 'financial']):
            return "financial"
        elif any(word in prompt_lower for word in ['competition', 'market', 'demand', 'covid', 'economic']):
            return "market"
        elif any(word in prompt_lower for word in ['management', 'fraud', 'dispute', 'mismanagement']):
            return "operational"
        elif any(word in prompt_lower for word in ['lawsuit', 'compliance', 'legal', 'regulatory']):
            return "legal"
        elif any(word in prompt_lower for word in ['technology', 'cyber', 'digital', 'innovation']):
            return "technology"
        elif any(word in prompt_lower for word in ['reputation', 'scandal', 'customer', 'brand']):
            return "reputation"
        
        # Industry-based defaults
        industry_defaults = {
            "Technology Services": "technology",
            "Financial Technology": "financial", 
            "Construction": "operational",
            "Professional Services": "market",
            "Manufacturing": "operational",
            "Retail Trade": "market"
        }
        
        return industry_defaults.get(industry, "financial")

    def _generate_dynamic_legal_clauses(self) -> List[Dict[str, str]]:
        """Generate 5-12 dynamic legal clauses"""
        clauses = []
        clause_count = random.randint(5, 12)
        
        # Always include core clauses
        core_categories = ["insolvency_declarations", "liquidation_resolutions", "liquidator_appointments"]
        
        for i, category in enumerate(core_categories):
            template = random.choice(self.LEGAL_CLAUSE_TEMPLATES[category])
            clauses.append({
                "number": i + 1,
                "title": category.replace('_', ' ').title(),
                "content": template,
                "category": category
            })
        
        # Add additional varied clauses
        optional_categories = [cat for cat in self.LEGAL_CLAUSE_TEMPLATES.keys() if cat not in core_categories]
        additional_count = clause_count - len(core_categories)
        selected_additional = random.sample(optional_categories, min(additional_count, len(optional_categories)))
        
        for i, category in enumerate(selected_additional):
            template = random.choice(self.LEGAL_CLAUSE_TEMPLATES[category])
            clauses.append({
                "number": len(clauses) + 1,
                "title": category.replace('_', ' ').title(),
                "content": template,
                "category": category
            })
        
        return clauses

    def _generate_document_structure(self) -> Dict[str, Any]:
        """Generate varied document structure"""
        structures = [
            {
                "type": "formal_resolution",
                "sections": ["header", "company_details", "financial_summary", "clauses", "reasons", "schedules", "signatures"],
                "style": "formal"
            },
            {
                "type": "comprehensive_analysis", 
                "sections": ["header", "executive_summary", "financial_analysis", "legal_framework", "asset_schedule", "liability_analysis", "risk_assessment", "signatures"],
                "style": "analytical"
            },
            {
                "type": "statutory_compliance",
                "sections": ["header", "statutory_declarations", "compliance_checklist", "financial_position", "creditor_information", "director_statements", "signatures"],
                "style": "compliance"
            }
        ]
        
        return random.choice(structures)

    def _generate_detailed_liquidation_reason(self, reasons: List[str], industry: str, company_name: str, debt: int, assets: int) -> str:
        """Generate comprehensive detailed liquidation reason"""
        primary_reason = reasons[0]
        
        templates = [
            f"{company_name} has experienced severe financial distress primarily due to {primary_reason.lower()}. The company's financial position has deteriorated significantly with total liabilities of ${debt:,} against assets valued at only ${assets:,} on a forced sale basis, representing a deficiency of ${debt - assets:,}. Contributing factors include {', '.join(reasons[1:3]).lower()}. The directors have determined that voluntary liquidation is the most appropriate course of action to ensure orderly wind-up and equitable distribution to creditors in accordance with statutory priorities.",
            
            f"The decision to wind up {company_name} follows an extensive review of the company's financial position and future viability. The primary driver has been {primary_reason.lower()}, which has created unsustainable operating conditions. Additional challenges including {' and '.join(reasons[1:3]).lower()} have compounded the situation. With debts totaling ${debt:,} and limited asset recovery potential of ${assets:,}, the company is unable to meet its obligations as they fall due. The directors believe liquidation represents the best outcome for all stakeholders.",
            
            f"After careful consideration of all available options, the directors of {company_name} have resolved to commence voluntary liquidation. The company has been unable to overcome significant challenges in the {industry.lower()} sector, particularly {primary_reason.lower()}. The situation has been exacerbated by {reasons[1].lower()} and {reasons[2].lower()}. Despite efforts to restructure operations and secure additional funding, the company remains insolvent with a substantial deficiency of ${debt - assets:,}. Liquidation will enable an orderly realization of assets and distribution to creditors."
        ]
        
        return random.choice(templates)

    def _generate_insolvency_indicators(self, industry: str, reasons: List[str]) -> List[str]:
        """Generate varied insolvency indicators based on reasons"""
        base_indicators = [
            "Inability to pay debts as they fall due",
            "Cash flow deficiencies over extended period", 
            "Mounting creditor demands and legal threats",
            "Inability to secure additional funding",
            "Declining business performance and revenue"
        ]
        
        reason_specific_indicators = {
            "financial": [
                "Overdraft limits consistently exceeded",
                "Multiple bounced cheques and failed direct debits",
                "Supplier accounts placed on COD terms",
                "Unable to meet loan repayment schedules"
            ],
            "market": [
                f"Loss of key {industry.lower()} customers and contracts",
                "Market share decline affecting revenue projections",
                "Pricing pressure from competitors",
                "Reduced demand for core products/services"
            ],
            "operational": [
                "Key staff departures disrupting operations",
                "Operational inefficiencies increasing costs",
                "Poor vendor relationships affecting supply",
                "Management systems failures"
            ],
            "legal": [
                "Regulatory compliance costs escalating",
                "Legal proceedings threatening asset base",
                "License revocations affecting operations",
                "Penalties and fines accumulating"
            ]
        }
        
        # Select indicators based on reasons
        selected_indicators = base_indicators.copy()
        for reason in reasons:
            for category, indicators in reason_specific_indicators.items():
                if any(keyword in reason.lower() for keyword in category.split()):
                    selected_indicators.extend(random.sample(indicators, min(2, len(indicators))))
        
        return random.sample(selected_indicators, min(8, len(selected_indicators)))

    def _generate_dynamic_assets(self, industry: str, base_assets: int) -> tuple:
        """Generate industry-specific asset schedules"""
        industry_asset_profiles = {
            "Technology Services": [
                ("Computer Equipment", 0.35, 0.40),
                ("Software Licenses", 0.20, 0.60),
                ("Office Furniture", 0.10, 0.25),
                ("Trade Debtors", 0.25, 0.80),
                ("Cash at Bank", 0.10, 1.00)
            ],
            "Construction": [
                ("Plant and Equipment", 0.40, 0.35),
                ("Motor Vehicles", 0.20, 0.45),
                ("Tools and Machinery", 0.15, 0.30),
                ("Trade Debtors", 0.15, 0.70),
                ("Materials Inventory", 0.10, 0.40)
            ],
            "Retail Trade": [
                ("Inventory", 0.45, 0.35),
                ("Shop Fittings", 0.20, 0.20),
                ("Point of Sale Systems", 0.10, 0.30),
                ("Trade Debtors", 0.15, 0.85),
                ("Cash at Bank", 0.10, 1.00)
            ]
        }
        
        default_profile = [
            ("Plant and Equipment", 0.25, 0.30),
            ("Office Furniture & Fittings", 0.15, 0.25),
            ("Computer Equipment", 0.20, 0.35),
            ("Trade Debtors", 0.25, 0.75),
            ("Inventory", 0.10, 0.50),
            ("Cash at Bank", 0.05, 1.00)
        ]
        
        asset_profile = industry_asset_profiles.get(industry, default_profile)
        
        assets_schedule = []
        total_book_value = 0
        total_estimated_value = 0
        
        for asset_type, proportion, recovery_rate in asset_profile:
            book_value = int(base_assets * proportion)
            estimated_value = int(book_value * recovery_rate)
            
            total_book_value += book_value
            total_estimated_value += estimated_value
            
            assets_schedule.append({
                "description": asset_type,
                "book_value": f"{book_value:,}",
                "estimated_value": f"{estimated_value:,}",
                "notes": self._get_dynamic_asset_notes(asset_type, industry)
            })
        
        return assets_schedule, total_book_value, total_estimated_value

    def _generate_dynamic_liabilities(self, industry: str, base_debt: int) -> List[Dict[str, str]]:
        """Generate industry-specific liability schedules"""
        industry_liability_profiles = {
            "Technology Services": [
                ("Venture Debt Facility", 0.35, "Secured - IP and Assets", "Secured"),
                ("Trade Creditors - Software/Cloud", 0.20, "Unsecured", "Unsecured"),
                ("Australian Taxation Office", 0.15, "Statutory Priority", "Priority"),
                ("Employee Stock Option Liabilities", 0.10, "Statutory Priority", "Priority"),
                ("Office Lease Liabilities", 0.12, "Unsecured", "Unsecured"),
                ("Professional Services", 0.08, "Unsecured", "Unsecured")
            ],
            "Construction": [
                ("Equipment Finance", 0.30, "Secured - Equipment", "Secured"),
                ("Trade Creditors - Suppliers", 0.25, "Unsecured", "Unsecured"),
                ("Australian Taxation Office", 0.15, "Statutory Priority", "Priority"),
                ("Employee Entitlements", 0.12, "Statutory Priority", "Priority"),
                ("Performance Bond Liabilities", 0.10, "Unsecured", "Unsecured"),
                ("Subcontractor Debts", 0.08, "Unsecured", "Unsecured")
            ]
        }
        
        default_profile = [
            ("Secured Bank Loan", 0.40, "Secured - General Security Agreement", "Secured"),
            ("Trade Creditors - Various", 0.25, "Unsecured", "Unsecured"),
            ("Australian Taxation Office", 0.15, "Statutory Priority", "Priority"),
            ("Employee Entitlements", 0.08, "Statutory Priority", "Priority"),
            ("Lease Liabilities", 0.07, "Unsecured", "Unsecured"),
            ("Other Creditors", 0.05, "Unsecured", "Unsecured")
        ]
        
        liability_profile = industry_liability_profiles.get(industry, default_profile)
        
        liability_schedule = []
        for liability_type, proportion, security, priority in liability_profile:
            amount = int(base_debt * proportion)
            liability_schedule.append({
                "creditor": liability_type,
                "amount": f"{amount:,}",
                "security": security,
                "priority": priority
            })
        
        return liability_schedule
    
    def _get_asset_notes(self, asset_type: str) -> str:
        """Generate realistic notes for different asset types"""
        notes_map = {
            "Plant and Equipment": random.choice([
                "Aged equipment, limited market value",
                "Specialized equipment, narrow market",
                "Good condition but industry-specific",
                "Depreciated, requires maintenance"
            ]),
            "Office Furniture & Fittings": random.choice([
                "Standard office furniture, readily marketable",
                "Good condition, suitable for resale",
                "Basic office setup, limited value",
                "Modern furniture in good condition"
            ]),
            "Computer Equipment": random.choice([
                "2-3 years old, moderate depreciation",
                "Current technology, good resale value",
                "Older systems, limited market appeal",
                "Mixed ages, some obsolete items"
            ]),
            "Motor Vehicles": random.choice([
                "Company vehicles, subject to finance",
                "Utility vehicles in fair condition",
                "High mileage, average condition",
                "Well-maintained fleet vehicles"
            ]),
            "Trade Debtors": random.choice([
                "Some doubtful debts requiring collection",
                "Mostly current, good collection prospects",
                "Includes overdue accounts, collection uncertain",
                "Mix of current and overdue accounts"
            ]),
            "Inventory": random.choice([
                "Slow-moving stock, market dependent",
                "Current inventory, good turnover",
                "Obsolete stock, limited marketability",
                "Seasonal inventory, timing dependent"
            ]),
            "Cash at Bank": random.choice([
                "Available cash, immediately accessible",
                "Restricted funds, some encumbrances",
                "Operating accounts, minimal balance",
                "Subject to bank guarantees"
            ])
        }
        return notes_map.get(asset_type, "Asset value dependent on market conditions")
    
    def _get_dynamic_asset_notes(self, asset_type: str, industry: str) -> str:
        """Generate dynamic notes for different asset types"""
        notes_library = {
            "Computer Equipment": [
                "Depreciation adjusted for age and technological obsolescence",
                "Market value affected by rapid technology advancement",
                "Includes laptops, desktops, servers - condition varies",
                "Recovery dependent on current market demand for used IT equipment"
            ],
            "Plant and Equipment": [
                "Valued based on forced sale conditions in current market",
                "Age and maintenance history affects realization value",
                "Industry-specific equipment may have limited buyer pool",
                "Transport and storage costs reduce net recovery"
            ],
            "Trade Debtors": [
                "Recovery rate based on age analysis and customer viability",
                "Provision for doubtful debts already applied",
                "Collection efforts ongoing through liquidator",
                "Some debtors may require legal action for recovery"
            ],
            "Inventory": [
                "Valued at lower of cost and net realizable value",
                "Slow-moving and obsolete stock heavily discounted",
                "Industry demand affects recovery rates",
                "Storage and selling costs reduce net proceeds"
            ],
            "Office Furniture": [
                "Second-hand office furniture market remains weak",
                "Bulk sale expected to achieve minimal recovery",
                "Condition varies - some items may be obsolete",
                "Transport costs significant relative to recovery value"
            ]
        }
        
        return random.choice(notes_library.get(asset_type, ["Asset recovery subject to market conditions and buyer interest"]))

    def _generate_cash_flow_issues(self, industry: str, reasons: List[str]) -> List[str]:
        """Generate industry and reason-specific cash flow issues"""
        base_issues = [
            "Consistent operating losses over past 12-18 months",
            "Declining gross margins due to competitive pressure",
            "Extended debtor payment terms affecting working capital"
        ]
        
        industry_specific = {
            "Technology Services": [
                "High customer acquisition costs with extended payback periods",
                "Subscription revenue churn affecting recurring income",
                "Heavy R&D investment requirements with uncertain returns"
            ],
            "Construction": [
                "Progress payment delays on major contracts", 
                "Seasonal cash flow variations affecting liquidity",
                "Equipment finance commitments exceeding project returns"
            ],
            "Retail Trade": [
                "Inventory management issues tying up working capital",
                "Declining foot traffic affecting daily cash generation",
                "Fixed lease commitments regardless of sales performance"
            ]
        }
        
        issues = base_issues + industry_specific.get(industry, [])
        
        # Add reason-specific cash flow impacts
        for reason in reasons:
            if "covid" in reason.lower():
                issues.append("COVID-19 lockdowns severely impacting revenue generation")
            elif "competition" in reason.lower():
                issues.append("Price competition forcing margin reduction to maintain market share")
            elif "debt" in reason.lower():
                issues.append("High interest and loan repayment obligations consuming available cash")
        
        return random.sample(issues, min(6, len(issues)))

    def _generate_liquidator_details(self) -> Dict[str, str]:
        """Generate realistic liquidator details"""
        from faker import Faker
        fake = Faker('en_AU')
        
        firms = [
            "Restructuring Partners Australia",
            "Corporate Recovery Solutions", 
            "Insolvency Specialists Group",
            "Business Restructuring Associates",
            "Advisory & Recovery Partners",
            "Turnaround Management Group",
            "Financial Recovery Advisors",
            "Corporate Insolvency Partners"
        ]
        
        firm = random.choice(firms)
        name = fake.name()
        
        return {
            "name": name,
            "firm": firm,
            "registration": f"LIQ{random.randint(1000, 9999)}",
            "phone": f"(0{random.randint(2,8)}) {random.randint(1000,9999)} {random.randint(1000,9999)}",
            "email": f"{name.lower().replace(' ', '.')}@{firm.lower().replace(' ', '').replace('&', 'and')[:20]}.com.au"
        }

    def _generate_major_creditors(self, total_debt: int) -> List[Dict[str, Any]]:
        """Generate major creditor list"""
        from faker import Faker
        fake = Faker('en_AU')
        
        creditor_types = [
            ("Big Four Bank", 0.35, "Secured"),
            ("Australian Taxation Office", 0.15, "Priority"),
            ("Trade Supplier", 0.12, "Unsecured"),
            ("Equipment Financier", 0.10, "Secured"),
            ("Landlord", 0.08, "Unsecured"),
            ("Professional Services", 0.05, "Unsecured"),
            ("Trade Supplier", 0.08, "Unsecured"),
            ("Employee Entitlements", 0.07, "Priority")
        ]
        
        creditors = []
        used_debt = 0
        
        for creditor_type, proportion, status in creditor_types:
            amount = int(total_debt * proportion)
            used_debt += amount
            
            if creditor_type == "Big Four Bank":
                name = random.choice(["Commonwealth Bank", "ANZ Bank", "Westpac Bank", "NAB"])
            elif creditor_type == "Australian Taxation Office":
                name = "Australian Taxation Office"
            elif creditor_type == "Equipment Financier":
                name = random.choice(["FlexiCommercial", "Liberty Financial", "Westpac Equipment Finance"])
            elif creditor_type == "Landlord":
                name = f"{fake.last_name()} Property Group"
            elif creditor_type == "Professional Services":
                name = random.choice([f"{fake.last_name()} & Associates", f"{fake.company()} Legal", f"{fake.last_name()} Accountants"])
            else:
                name = fake.company()
            
            creditors.append({
                "name": name,
                "amount": f"{amount:,}",
                "status": status,
                "type": creditor_type
            })
        
        return creditors

    def _generate_address(self, state: str) -> Dict[str, str]:
        """Generate realistic Australian address"""
        from faker import Faker
        fake = Faker('en_AU')
        
        state_cities = {
            'NSW': ['Sydney', 'Newcastle', 'Wollongong', 'Parramatta'],
            'VIC': ['Melbourne', 'Geelong', 'Ballarat', 'Bendigo'],
            'QLD': ['Brisbane', 'Gold Coast', 'Townsville', 'Cairns'],
            'WA': ['Perth', 'Fremantle', 'Mandurah', 'Bunbury'],
            'SA': ['Adelaide', 'Mount Gambier', 'Whyalla', 'Murray Bridge'],
            'TAS': ['Hobart', 'Launceston', 'Devonport', 'Burnie'],
            'NT': ['Darwin', 'Alice Springs', 'Katherine', 'Nhulunbuy'],
            'ACT': ['Canberra', 'Belconnen', 'Tuggeranong', 'Gungahlin']
        }
        
        postcode_ranges = {
            'NSW': (2000, 2999),
            'VIC': (3000, 3999), 
            'QLD': (4000, 4999),
            'WA': (6000, 6999),
            'SA': (5000, 5999),
            'TAS': (7000, 7999),
            'NT': (800, 999),
            'ACT': (2600, 2699)
        }
        
        city = random.choice(state_cities.get(state, ['Sydney']))
        postcode_range = postcode_ranges.get(state, (2000, 2999))
        postcode = random.randint(*postcode_range)
        
        return {
            "street": fake.street_address(),
            "city": city,
            "state": state,
            "postcode": str(postcode)
        }

    def _generate_valid_abn(self) -> str:
        """Generate a valid Australian Business Number with correct check digit"""
        # Generate 9 random digits for the core ABN
        core_digits = [random.randint(0, 9) for _ in range(9)]
        
        # ABN check digit calculation
        weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        
        # Subtract 1 from first digit
        first_digit = core_digits[0] - 1 if core_digits[0] > 0 else 9
        
        # Calculate weighted sum
        weighted_sum = first_digit * weights[0]
        for i in range(1, 9):
            weighted_sum += core_digits[i] * weights[i + 1]
        
        # Calculate check digits
        remainder = weighted_sum % 89
        check_digits = 89 - remainder if remainder != 0 else 0
        
        # Format as string with check digits at start
        abn_digits = [check_digits // 10, check_digits % 10] + core_digits
        return ''.join(f'{digit:01d}' for digit in abn_digits)

    def _generate_acn(self) -> str:
        """Generate a valid Australian Company Number"""
        # Generate 8 random digits
        digits = [random.randint(0, 9) for _ in range(8)]
        
        # ACN check digit calculation
        weights = [8, 7, 6, 5, 4, 3, 2, 1]
        weighted_sum = sum(digit * weight for digit, weight in zip(digits, weights))
        check_digit = (10 - (weighted_sum % 10)) % 10
        
        # Format with check digit
        acn_digits = digits + [check_digit]
        return ''.join(f'{digit:01d}' for digit in acn_digits)

    async def generate_document_content(self, document_type: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate document content with dynamic clauses and reasons"""
        if not company_data:
            return {"error": "Company data required"}
        
        # Ensure dynamic content is generated if missing
        if "dynamic_clauses" not in company_data:
            company_data["dynamic_clauses"] = self._generate_dynamic_legal_clauses()
        
        if "liquidation_reasons_full" not in company_data:
            # Generate new set of reasons
            category = random.choice(list(self.LIQUIDATION_REASONS.keys()))
            company_data["liquidation_reasons_full"] = random.sample(
                self.LIQUIDATION_REASONS[category], 
                random.randint(3, 6)
            )
        
        if "document_structure" not in company_data:
            company_data["document_structure"] = self._generate_document_structure()
        
        return {
            "success": True,
            "content": company_data,
            "document_type": document_type,
            "generated_clauses": len(company_data.get("dynamic_clauses", [])),
            "reason_category": company_data.get("primary_reason_category", "financial"),
            "structure_type": company_data.get("document_structure", {}).get("type", "formal_resolution")
        }

    async def generate_company_details(self, industry: str = None, location: str = None) -> Dict[str, Any]:
        """Generate company details with dynamic content"""
        scenario = await self._generate_comprehensive_scenario(
            industry=industry or "Professional Services",
            state=location or "NSW"
        )
        return {"success": True, "data": scenario}

    async def generate_liquidation_reason(self, company_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate liquidation reason using the 150 reasons database"""
        # Select random category and reasons
        category = random.choice(list(self.LIQUIDATION_REASONS.keys()))
        reasons = random.sample(self.LIQUIDATION_REASONS[category], random.randint(2, 5))
        
        # Generate additional context
        industry = company_data.get("industry", "Professional Services") if company_data else "Professional Services"
        company_name = company_data.get("company_name", "Sample Company Pty Ltd") if company_data else "Sample Company Pty Ltd"
        
        detailed_reason = self._generate_detailed_liquidation_reason(
            reasons, industry, company_name, 
            random.randint(500000, 2000000), 
            random.randint(100000, 800000)
        )
        
        return {
            "success": True,
            "primary_reason": reasons[0],
            "contributing_factors": reasons[1:],
            "category": category,
            "detailed_explanation": detailed_reason,
            "all_reasons": reasons
        }

    async def enhance_existing_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance existing data with dynamic clauses and varied content"""
        if not data:
            return {"error": "No data provided"}
        
        # Add dynamic elements
        data["dynamic_clauses"] = self._generate_dynamic_legal_clauses()
        data["document_structure"] = self._generate_document_structure()
        
        # Update liquidation reason if basic
        if data.get("reason_for_liquidation") and len(data["reason_for_liquidation"]) < 50:
            category = random.choice(list(self.LIQUIDATION_REASONS.keys()))
            new_reasons = random.sample(self.LIQUIDATION_REASONS[category], random.randint(3, 5))
            data["liquidation_reasons_full"] = new_reasons
            data["reason_for_liquidation"] = "; ".join(new_reasons[:2])
        
        # Add missing financial details
        if "cash_flow_issues" not in data:
            data["cash_flow_issues"] = self._generate_cash_flow_issues(
                data.get("industry", "Professional Services"),
                data.get("liquidation_reasons_full", ["Financial difficulties"])
            )
        
        return {"success": True, "enhanced_data": data}

    async def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate content using OpenAI API with dynamic prompting"""
        enhanced_prompt = f"""
        Generate a comprehensive liquidation document scenario based on this prompt: "{prompt}"
        
        Requirements:
        1. Use varied and realistic liquidation reasons from categories: financial, market, operational, legal, strategic, technology, reputation, external
        2. Generate 5-12 unique legal clauses (not hardcoded templates)
        3. Create realistic Australian company details with valid ABN/ACN structure
        4. Include comprehensive financial analysis with industry-appropriate assets/liabilities
        5. Provide detailed insolvency indicators and cash flow issues
        6. Generate varied document structure and presentation style
        
        Ensure each generation is unique with different reasons, clauses, and financial scenarios.
        Focus on Australian corporate law compliance and realistic business scenarios.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in Australian corporate law and liquidation procedures. Generate realistic, varied liquidation documents with unique content each time."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.8  # Higher temperature for more variety
            )
            
            content = response.choices[0].message.content
            
            # Parse the LLM response and enhance with our structured data
            scenario = await self._generate_comprehensive_scenario(prompt=prompt)
            
            return {
                "success": True,
                "source": "openai_enhanced",
                "llm_content": content,
                "structured_data": scenario
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            return await self._generate_fallback(prompt) 