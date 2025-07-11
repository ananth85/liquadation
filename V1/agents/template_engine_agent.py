import jinja2
import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentTask
import logging
from pathlib import Path
import os

class TemplateEngineAgent(BaseAgent):
    """Agent responsible for template processing and document content rendering"""
    
    def __init__(self, templates_dir: str = "templates", logger: Optional[logging.Logger] = None):
        super().__init__("TemplateEngineAgent", logger)
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.jinja_env.filters['format_currency'] = self._format_currency_filter
        
        # Create default templates if they don't exist
        self._ensure_default_templates()
    
    def get_capabilities(self) -> List[str]:
        return [
            "render_template",
            "render_document", 
            "list_templates",
            "validate_template",
            "create_template"
        ]
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process template rendering tasks"""
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "render_template":
            return await self.render_template(
                input_data.get("template_name"), 
                input_data.get("data")
            )
        elif task_type == "render_document":
            return await self.render_document(
                input_data.get("document_type"),
                input_data.get("company_data")
            )
        elif task_type == "list_templates":
            return await self.list_templates()
        elif task_type == "validate_template":
            return await self.validate_template(input_data.get("template_name"))
        elif task_type == "create_template":
            return await self.create_template(
                input_data.get("template_name"),
                input_data.get("content")
            )
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def render_template(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render a specific template with provided data"""
        if not template_name:
            raise ValueError("Template name is required")
        
        if not data:
            raise ValueError("Data is required for template rendering")
        
        try:
            template = self.jinja_env.get_template(template_name)
            
            # Add helper functions to template context
            template_data = data.copy()
            template_data.update(self._get_template_helpers())
            
            # Render template
            rendered_content = template.render(**template_data)
            
            self.logger.info(f"Successfully rendered template: {template_name}")
            
            return {
                "success": True,
                "template_name": template_name,
                "rendered_content": rendered_content,
                "content_length": len(rendered_content)
            }
            
        except jinja2.TemplateNotFound:
            raise FileNotFoundError(f"Template not found: {template_name}")
        except jinja2.TemplateSyntaxError as e:
            raise ValueError(f"Template syntax error in {template_name}: {e}")
        except Exception as e:
            raise RuntimeError(f"Template rendering failed: {e}")
    
    async def render_document(self, document_type: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render a complete document by type"""
        if not document_type:
            raise ValueError("Document type is required")
        
        # Map document types to templates
        template_mapping = {
            "resolution": "liquidation_resolution.j2",
            "director_resolution": "liquidation_resolution.j2",
            "creditor_notice": "creditor_notice.j2",
            "notice_to_creditors": "creditor_notice.j2",
            "liquidator_appointment": "liquidator_appointment.j2",
            "director_statement": "director_statement.j2",
            "asic_form": "asic_form_505.j2",
            "winding_up_notice": "winding_up_notice.j2"
        }
        
        template_name = template_mapping.get(document_type.lower())
        if not template_name:
            raise ValueError(f"Unknown document type: {document_type}")
        
        # Enrich company data with document-specific fields
        enriched_data = await self._enrich_data_for_document(document_type, company_data)
        
        return await self.render_template(template_name, enriched_data)
    
    async def _enrich_data_for_document(self, document_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data with document-specific fields and formatting"""
        from datetime import datetime
        from faker import Faker
        fake = Faker('en_AU')
        
        enriched = data.copy()
        
        # Add common fields
        if 'current_date' not in enriched:
            enriched['current_date'] = datetime.now().strftime('%d %B %Y')
        
        if 'formatted_date' not in enriched:
            date_str = enriched.get('date', datetime.now().strftime('%Y-%m-%d'))
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                enriched['formatted_date'] = date_obj.strftime('%d %B %Y')
            except:
                enriched['formatted_date'] = datetime.now().strftime('%d %B %Y')
        
        # Format ABN/ACN with spaces
        if 'abn' in enriched and len(str(enriched['abn'])) == 11:
            abn = str(enriched['abn'])
            enriched['formatted_abn'] = f"{abn[:2]} {abn[2:5]} {abn[5:8]} {abn[8:11]}"
        
        if 'acn' in enriched and ' ' not in str(enriched['acn']):
            acn = str(enriched['acn']).replace(' ', '')
            if len(acn) == 9:
                enriched['formatted_acn'] = f"{acn[:3]} {acn[3:6]} {acn[6:9]}"
        
        # Document-specific enrichments
        if document_type.lower() in ['resolution', 'director_resolution']:
            enriched.update({
                'meeting_type': 'Board Meeting',
                'resolution_number': f"BR{fake.random_int(100, 999)}",
                'quorum_present': True,
                'unanimous_decision': True
            })
        
        elif document_type.lower() in ['creditor_notice', 'notice_to_creditors']:
            meeting_date = fake.date_between(start_date='+7d', end_date='+21d')
            enriched.update({
                'meeting_date': meeting_date.strftime('%d %B %Y'),
                'meeting_time': '10:00 AM',
                'meeting_venue': f"{fake.building_number()} {fake.street_name()}, {fake.city()} {enriched.get('address', {}).get('state', 'NSW')}",
                'rsvp_date': fake.date_between(start_date='+2d', end_date='+5d').strftime('%d %B %Y')
            })
        
        elif document_type.lower() == 'liquidator_appointment':
            enriched.update({
                'appointment_effective_date': enriched.get('formatted_date'),
                'liquidator_registration': f"LIQ{fake.random_int(1000, 9999)}",
                'liquidator_phone': fake.phone_number(),
                'liquidator_email': f"{enriched.get('liquidator_name', 'liquidator').lower().replace(' ', '.')}@liquidation.com.au"
            })
        
        # Ensure required fields have defaults
        required_defaults = {
            'company_name': 'Unknown Company Pty Ltd',
            'abn': '12 345 678 901',
            'acn': '123 456 789',
            'liquidator_name': 'John Smith',
            'liquidation_type': 'Creditors\' Voluntary Liquidation'
        }
        
        for field, default in required_defaults.items():
            if field not in enriched or not enriched[field]:
                enriched[field] = default
        
        return enriched
    
    def _get_template_helpers(self) -> Dict[str, Any]:
        """Get helper functions for templates"""
        from datetime import datetime
        
        def format_currency(amount):
            """Format currency values"""
            if isinstance(amount, str):
                # Extract numbers from string
                import re
                numbers = re.findall(r'[\d,]+', amount)
                if numbers:
                    amount = int(numbers[0].replace(',', ''))
            
            if isinstance(amount, (int, float)):
                return f"${amount:,.2f}"
            return str(amount)
        
        def format_date(date_str, format_str='%d %B %Y'):
            """Format date strings"""
            if isinstance(date_str, str):
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    return date_obj.strftime(format_str)
                except:
                    pass
            return str(date_str)
        
        def join_with_and(items):
            """Join list items with 'and' for the last item"""
            if not items:
                return ""
            if len(items) == 1:
                return str(items[0])
            if len(items) == 2:
                return f"{items[0]} and {items[1]}"
            return f"{', '.join(str(item) for item in items[:-1])}, and {items[-1]}"
        
        return {
            'format_currency': format_currency,
            'format_date': format_date,
            'join_with_and': join_with_and,
            'current_year': datetime.now().year,
            'current_date': datetime.now().strftime('%d %B %Y')
        }
    
    def _format_currency_filter(self, amount):
        """Format currency values as a Jinja2 filter"""
        if isinstance(amount, str):
            # Extract numbers from string
            import re
            numbers = re.findall(r'[\d,]+', amount)
            if numbers:
                try:
                    amount = int(numbers[0].replace(',', ''))
                except:
                    return str(amount)
        
        if isinstance(amount, (int, float)):
            return f"{amount:,.0f}"
        return str(amount)
    
    async def list_templates(self) -> Dict[str, Any]:
        """List all available templates"""
        templates = []
        
        for template_file in self.templates_dir.glob("*.j2"):
            try:
                # Try to load template to check if it's valid
                template = self.jinja_env.get_template(template_file.name)
                
                templates.append({
                    "name": template_file.name,
                    "path": str(template_file),
                    "size": template_file.stat().st_size,
                    "valid": True
                })
            except Exception as e:
                templates.append({
                    "name": template_file.name,
                    "path": str(template_file),
                    "size": template_file.stat().st_size,
                    "valid": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
    
    async def validate_template(self, template_name: str) -> Dict[str, Any]:
        """Validate a template syntax"""
        if not template_name:
            raise ValueError("Template name is required")
        
        try:
            template = self.jinja_env.get_template(template_name)
            
            # Try to render with dummy data to check for required variables
            dummy_data = {
                'company_name': 'Test Company',
                'abn': '12345678901',
                'acn': '123456789',
                'date': '2025-01-01',
                'liquidator_name': 'Test Liquidator',
                'directors': ['Test Director'],
                'liquidation_type': 'Test Liquidation'
            }
            
            # Add template helpers
            dummy_data.update(self._get_template_helpers())
            
            # Attempt render
            rendered = template.render(**dummy_data)
            
            return {
                "success": True,
                "template_name": template_name,
                "valid": True,
                "rendered_length": len(rendered)
            }
            
        except jinja2.TemplateNotFound:
            return {
                "success": False,
                "template_name": template_name,
                "valid": False,
                "error": "Template not found"
            }
        except jinja2.TemplateSyntaxError as e:
            return {
                "success": False,
                "template_name": template_name,
                "valid": False,
                "error": f"Syntax error: {e}"
            }
        except jinja2.UndefinedError as e:
            return {
                "success": False,
                "template_name": template_name,
                "valid": False,
                "error": f"Undefined variable: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "template_name": template_name,
                "valid": False,
                "error": str(e)
            }
    
    async def create_template(self, template_name: str, content: str) -> Dict[str, Any]:
        """Create a new template file"""
        if not template_name:
            raise ValueError("Template name is required")
        
        if not content:
            raise ValueError("Template content is required")
        
        # Ensure .j2 extension
        if not template_name.endswith('.j2'):
            template_name = f"{template_name}.j2"
        
        template_path = self.templates_dir / template_name
        
        try:
            # Validate template syntax first
            test_env = jinja2.Environment()
            test_env.from_string(content)
            
            # Write template file
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Created template: {template_name}")
            
            return {
                "success": True,
                "template_name": template_name,
                "template_path": str(template_path),
                "content_length": len(content)
            }
            
        except jinja2.TemplateSyntaxError as e:
            raise ValueError(f"Template syntax error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create template: {e}")
    
    def _ensure_default_templates(self):
        """Create default templates if they don't exist"""
        default_templates = {
            "liquidation_resolution.j2": """
{{ company_name }}
ABN: {{ formatted_abn or abn }}
ACN: {{ formatted_acn or acn }}

RESOLUTION OF DIRECTORS

Date: {{ formatted_date or current_date }}

We, the undersigned directors of {{ company_name }}, hereby resolve:

1. That the company is insolvent and unable to pay its debts as they fall due.

2. That the company be wound up by way of {{ liquidation_type }}.

3. That {{ liquidator_name }} be appointed as liquidator of the company effective {{ formatted_date or current_date }}.

4. That this resolution was passed {{ 'unanimously' if unanimous_decision else 'by majority' }}.

Reason for Liquidation:
{{ liquidation_reason_detailed or reason_for_liquidation }}

Directors:
{% for director in directors %}
_________________
{{ director }}
{% endfor %}

Resolution Number: {{ resolution_number or 'N/A' }}
            """.strip(),
            
            "creditor_notice.j2": """
NOTICE TO CREDITORS

{{ company_name }}
ABN: {{ formatted_abn or abn }}
ACN: {{ formatted_acn or acn }}

NOTICE OF MEETING OF CREDITORS

NOTICE is hereby given that a meeting of creditors of {{ company_name }} will be held pursuant to Section 436E of the Corporations Act 2001.

Meeting Details:
Date: {{ meeting_date }}
Time: {{ meeting_time or '10:00 AM' }}
Venue: {{ meeting_venue or 'To be advised' }}

Purpose:
The company has resolved to wind up by {{ liquidation_type }} due to {{ reason_for_liquidation }}.

Creditors are invited to attend and vote at the meeting.

Appointed Liquidator: {{ liquidator_name }}
Contact: {{ liquidator_phone or 'Contact details to follow' }}

RSVP by: {{ rsvp_date }}

Dated: {{ formatted_date or current_date }}

{{ liquidator_name }}
Liquidator
            """.strip(),
            
            "liquidator_appointment.j2": """
APPOINTMENT OF LIQUIDATOR

{{ company_name }}
ABN: {{ formatted_abn or abn }}
ACN: {{ formatted_acn or acn }}

NOTICE OF APPOINTMENT

Notice is hereby given that {{ liquidator_name }} has been appointed as liquidator of {{ company_name }} effective {{ appointment_effective_date or formatted_date }}.

Type of Liquidation: {{ liquidation_type }}

Liquidator Details:
Name: {{ liquidator_name }}
Registration: {{ liquidator_registration or 'Registered Liquidator' }}
{% if liquidator_phone %}Phone: {{ liquidator_phone }}{% endif %}
{% if liquidator_email %}Email: {{ liquidator_email }}{% endif %}

All creditors and debtors of the company should direct their inquiries to the appointed liquidator.

Dated: {{ formatted_date or current_date }}
            """.strip(),
            
            "director_statement.j2": """
STATEMENT BY DIRECTORS

{{ company_name }}
ABN: {{ formatted_abn or abn }}
ACN: {{ formatted_acn or acn }}

STATEMENT OF AFFAIRS

We, the undersigned directors of {{ company_name }}, make the following statement regarding the company's affairs:

1. The company has ceased to carry on business as of {{ formatted_date }}.

2. The company is insolvent and unable to pay its debts as they fall due.

3. Estimated assets: {{ assets_estimate or 'To be determined' }}

4. Estimated liabilities: {{ debts_estimate or 'To be determined' }}

5. Major creditors:
{% if creditors %}
{% for creditor in creditors %}
   - {{ creditor.name }}: {{ creditor.amount }} ({{ creditor.type }})
{% endfor %}
{% else %}
   To be detailed in full statement of affairs.
{% endif %}

6. Reason for insolvency:
{{ liquidation_reason_detailed or reason_for_liquidation }}

We believe this statement to be true and correct.

Directors:
{% for director in directors %}
_________________
{{ director }}
Date: {{ formatted_date or current_date }}
{% endfor %}
            """.strip()
        }
        
        for template_name, content in default_templates.items():
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                try:
                    with open(template_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.logger.info(f"Created default template: {template_name}")
                except Exception as e:
                    self.logger.error(f"Failed to create default template {template_name}: {e}")
    
    def reload_templates(self):
        """Reload template environment (useful for development)"""
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        ) 