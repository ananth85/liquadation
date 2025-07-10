#!/usr/bin/env python3
"""
Enhanced Template Agent for Liquidation Document Generation
Now supports PDF-analyzed templates, logo integration, multi-page layouts, and complex structures
"""

import asyncio
import logging
import os
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from .base_agent import BaseAgent, AgentTask


class TemplateAgent(BaseAgent):
    """
    Enhanced Template Agent with PDF Analysis Integration
    
    New capabilities:
    - PDF-analyzed template support
    - Logo and image integration
    - Multi-page document layouts
    - Complex table structures
    - Dynamic template selection
    - CSS styling integration
    """
    
    def __init__(self, templates_dir: str = "templates", logger: Optional[logging.Logger] = None):
        super().__init__("Template Agent", logger)
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment with enhanced features
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters for enhanced functionality
        self._add_custom_filters()
        
        # Template registry for PDF-analyzed templates
        self.template_registry = {}
        self.css_registry = {}
        
        # Load existing templates
        self._load_template_registry()
        
        self.logger.info("Enhanced Template Agent initialized")

    def _add_custom_filters(self):
        """Add custom Jinja2 filters for enhanced template functionality"""
        
        def format_currency(value, currency_symbol="$"):
            """Format currency values"""
            try:
                if isinstance(value, str):
                    value = float(value.replace(',', '').replace('$', ''))
                return f"{currency_symbol}{value:,.2f}"
            except (ValueError, TypeError):
                return f"{currency_symbol}0.00"
        
        def format_date(value, format_str="%d %B %Y"):
            """Format date values"""
            if isinstance(value, str):
                try:
                    # Try to parse common date formats
                    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
                        try:
                            date_obj = datetime.strptime(value, fmt)
                            return date_obj.strftime(format_str)
                        except ValueError:
                            continue
                    return value
                except:
                    return value
            elif hasattr(value, 'strftime'):
                return value.strftime(format_str)
            return str(value)
        
        def format_abn(value):
            """Format ABN with spaces"""
            if not value:
                return ""
            value_str = str(value).replace(" ", "")
            if len(value_str) == 11:
                return f"{value_str[:2]} {value_str[2:5]} {value_str[5:8]} {value_str[8:]}"
            return value_str
        
        def format_acn(value):
            """Format ACN with spaces"""
            if not value:
                return ""
            value_str = str(value).replace(" ", "")
            if len(value_str) == 9:
                return f"{value_str[:3]} {value_str[3:6]} {value_str[6:]}"
            return value_str
        
        def encode_image(image_path):
            """Encode image to base64 for embedding"""
            try:
                if not image_path or not Path(image_path).exists():
                    return ""
                
                with open(image_path, 'rb') as img_file:
                    encoded = base64.b64encode(img_file.read()).decode('utf-8')
                    # Determine MIME type
                    ext = Path(image_path).suffix.lower()
                    mime_type = {
                        '.png': 'image/png',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.gif': 'image/gif',
                        '.svg': 'image/svg+xml'
                    }.get(ext, 'image/png')
                    
                    return f"data:{mime_type};base64,{encoded}"
            except Exception as e:
                self.logger.warning(f"Failed to encode image {image_path}: {e}")
                return ""
        
        def safe_default(value, default_value="N/A"):
            """Provide safe default for missing values"""
            return value if value is not None and value != "" else default_value
        
        def truncate_text(value, length=100, suffix="..."):
            """Truncate text to specified length"""
            if not value:
                return ""
            value_str = str(value)
            if len(value_str) <= length:
                return value_str
            return value_str[:length].rstrip() + suffix
        
        def capitalize_words(value):
            """Capitalize each word in a string"""
            if not value:
                return ""
            return str(value).title()
        
        # Register filters
        self.env.filters['currency'] = format_currency
        self.env.filters['date'] = format_date
        self.env.filters['abn'] = format_abn
        self.env.filters['acn'] = format_acn
        self.env.filters['encode_image'] = encode_image
        self.env.filters['safe_default'] = safe_default
        self.env.filters['truncate'] = truncate_text
        self.env.filters['capitalize_words'] = capitalize_words

    def _load_template_registry(self):
        """Load template registry from existing files"""
        # Scan for .j2 templates
        for template_file in self.templates_dir.glob("*.j2"):
            template_name = template_file.stem
            self.template_registry[template_name] = str(template_file)
            
            # Check for corresponding CSS file
            css_file = template_file.with_suffix('.css')
            if css_file.exists():
                self.css_registry[template_name] = str(css_file)
        
        self.logger.info(f"Loaded {len(self.template_registry)} templates from registry")

    def get_capabilities(self) -> List[str]:
        return [
            "render_template",
            "render_pdf_analyzed_template",
            "create_multipage_document",
            "integrate_logo",
            "render_complex_tables",
            "apply_custom_styles",
            "validate_template",
            "list_available_templates",
            "get_template_info"
        ]

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process template rendering tasks with enhanced capabilities"""
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            if task_type == "render_template":
                return await self._render_template(input_data)
            elif task_type == "render_pdf_analyzed_template":
                return await self._render_pdf_analyzed_template(input_data)
            elif task_type == "create_multipage_document":
                return await self._create_multipage_document(input_data)
            elif task_type == "integrate_logo":
                return await self._integrate_logo(input_data)
            elif task_type == "render_complex_tables":
                return await self._render_complex_tables(input_data)
            elif task_type == "apply_custom_styles":
                return await self._apply_custom_styles(input_data)
            elif task_type == "validate_template":
                return await self._validate_template(input_data)
            elif task_type == "list_available_templates":
                return await self._list_available_templates(input_data)
            elif task_type == "get_template_info":
                return await self._get_template_info(input_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Template rendering failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "Default template rendering"
            }

    async def _render_template(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced template rendering with support for PDF-analyzed templates"""
        template_name = input_data.get("template_name", "liquidation_resolution")
        data = input_data.get("data", {})
        rag_insights = input_data.get("rag_insights", [])
        
        # Add current timestamp and formatting helpers
        data.update({
            "current_date": datetime.now().strftime("%d %B %Y"),
            "current_datetime": datetime.now().isoformat(),
            "generation_timestamp": datetime.now()
        })
        
        # Handle logo integration
        if input_data.get("logo_support") and data.get("company_logo"):
            data["logo_encoded"] = self.env.filters['encode_image'](data["company_logo"])
        
        # Handle multi-page support
        if input_data.get("multipage_support"):
            data["multipage_enabled"] = True
            data["page_breaks"] = input_data.get("page_breaks", [])
        
        try:
            # Check if we have a PDF-analyzed template
            template_file = self.template_registry.get(template_name)
            if template_file and Path(template_file).exists():
                template = self.env.get_template(f"{template_name}.j2")
            else:
                # Fall back to default template
                template = self._get_default_template(template_name)
            
            # Render the template
            rendered_html = template.render(**data)
            
            # Get associated CSS if available
            css_content = ""
            css_file = self.css_registry.get(template_name)
            if css_file and Path(css_file).exists():
                with open(css_file, 'r', encoding='utf-8') as f:
                    css_content = f.read()
            
            # Add RAG insights as comments in HTML
            if rag_insights:
                insights_html = "\n<!-- RAG Insights:\n"
                for insight in rag_insights:
                    insights_html += f"- {insight}\n"
                insights_html += "-->\n"
                rendered_html = insights_html + rendered_html
            
            return {
                "success": True,
                "rendered_html": rendered_html,
                "css_content": css_content,
                "template_used": template_name,
                "template_source": "pdf_analyzed" if template_file else "default",
                "features_used": {
                    "logo_integration": bool(data.get("logo_encoded")),
                    "multipage": bool(data.get("multipage_enabled")),
                    "custom_styles": bool(css_content),
                    "rag_insights": len(rag_insights)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Template rendering failed for {template_name}: {e}")
            # Fall back to basic template
            return await self._render_fallback_template(data, template_name)

    def _get_default_template(self, template_name: str) -> Template:
        """Get default template based on document type"""
        templates = {
            "liquidation_resolution": self._create_liquidation_resolution_template(),
            "creditor_notice": self._create_creditor_notice_template(),
            "liquidator_appointment": self._create_liquidator_appointment_template(),
            "director_statement": self._create_director_statement_template()
        }
        
        return templates.get(template_name, templates["liquidation_resolution"])

    def _create_liquidation_resolution_template(self) -> Template:
        """Create default liquidation resolution template"""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liquidation Resolution - {{ company_name | safe_default }}</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.4; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000; padding-bottom: 10px; }
        .section { margin-bottom: 25px; }
        .section-title { font-weight: bold; font-size: 14pt; margin-bottom: 10px; }
        .signature-block { margin-top: 40px; }
    </style>
</head>
<body>
    {% if logo_encoded %}
    <div class="header">
        <img src="{{ logo_encoded }}" alt="Company Logo" style="max-height: 80px; margin-bottom: 10px;">
        <h1>{{ company_name | upper | safe_default }}</h1>
        {% if abn %}<p>ABN: {{ abn | abn }}</p>{% endif %}
        {% if acn %}<p>ACN: {{ acn | acn }}</p>{% endif %}
    </div>
    {% else %}
    <div class="header">
        <h1>{{ company_name | upper | safe_default }}</h1>
        {% if abn %}<p>ABN: {{ abn | abn }}</p>{% endif %}
        {% if acn %}<p>ACN: {{ acn | acn }}</p>{% endif %}
    </div>
    {% endif %}
    
    <div class="section">
        <h2 class="section-title">RESOLUTION FOR LIQUIDATION</h2>
        <p><strong>Date:</strong> {{ resolution_date | date | safe_default }}</p>
        <p><strong>Meeting Type:</strong> {{ meeting_type | safe_default("Special Meeting") }}</p>
        
        <p>IT IS RESOLVED that:</p>
        <ol>
            <li>The company {{ company_name | safe_default }} be wound up voluntarily.</li>
            <li>{{ liquidator_name | safe_default("A qualified liquidator") }} be appointed as liquidator.</li>
            {% if liquidation_reason %}
            <li>The reason for liquidation: {{ liquidation_reason }}</li>
            {% endif %}
        </ol>
    </div>
    
    <div class="signature-block">
        <p><strong>Director:</strong> _________________________</p>
        <p>Name: {{ director_name | safe_default }}</p>
        <p>Date: {{ current_date }}</p>
    </div>
</body>
</html>'''
        
        return Template(template_content)

    def _create_creditor_notice_template(self) -> Template:
        """Create default creditor notice template"""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Notice to Creditors - {{ company_name | safe_default }}</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.4; }
        .header { text-align: center; margin-bottom: 30px; }
        .notice-box { border: 2px solid #000; padding: 15px; margin: 20px 0; }
        .important { font-weight: bold; color: #cc0000; }
    </style>
</head>
<body>
    <div class="header">
        {% if logo_encoded %}
        <img src="{{ logo_encoded }}" alt="Company Logo" style="max-height: 60px;">
        {% endif %}
        <h1>NOTICE TO CREDITORS</h1>
        <h2>{{ company_name | upper | safe_default }}</h2>
        {% if abn %}<p>ABN: {{ abn | abn }}</p>{% endif %}
    </div>
    
    <div class="notice-box">
        <p class="important">NOTICE OF LIQUIDATION</p>
        <p>Notice is hereby given that {{ company_name | safe_default }} is being wound up voluntarily.</p>
        <p><strong>Liquidator:</strong> {{ liquidator_name | safe_default }}</p>
        <p><strong>Appointment Date:</strong> {{ appointment_date | date | safe_default }}</p>
    </div>
    
    <div class="section">
        <h3>CREDITOR MEETING</h3>
        <p><strong>Date:</strong> {{ meeting_date | date | safe_default("To be advised") }}</p>
        <p><strong>Time:</strong> {{ meeting_time | safe_default("To be advised") }}</p>
        <p><strong>Location:</strong> {{ meeting_location | safe_default("To be advised") }}</p>
    </div>
    
    <div class="section">
        <p class="important">Creditors must submit proofs of debt by {{ proof_deadline | date | safe_default("To be advised") }}</p>
    </div>
</body>
</html>'''
        
        return Template(template_content)

    def _create_liquidator_appointment_template(self) -> Template:
        """Create default liquidator appointment template"""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Liquidator Appointment - {{ company_name | safe_default }}</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.4; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 1px solid #000; padding-bottom: 15px; }
        .appointment-details { background-color: #f5f5f5; padding: 15px; margin: 20px 0; }
        .powers-list { margin: 15px 0; }
        .powers-list li { margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="header">
        {% if logo_encoded %}
        <img src="{{ logo_encoded }}" alt="Company Logo" style="max-height: 60px;">
        {% endif %}
        <h1>APPOINTMENT OF LIQUIDATOR</h1>
        <h2>{{ company_name | upper | safe_default }}</h2>
        {% if abn %}<p>ABN: {{ abn | abn }}</p>{% endif %}
        {% if acn %}<p>ACN: {{ acn | acn }}</p>{% endif %}
    </div>
    
    <div class="appointment-details">
        <h3>LIQUIDATOR DETAILS</h3>
        <p><strong>Name:</strong> {{ liquidator_name | safe_default }}</p>
        <p><strong>Registration Number:</strong> {{ liquidator_registration | safe_default("To be confirmed") }}</p>
        <p><strong>Address:</strong> {{ liquidator_address | safe_default("To be confirmed") }}</p>
        <p><strong>Contact:</strong> {{ liquidator_contact | safe_default("To be confirmed") }}</p>
        <p><strong>Appointment Date:</strong> {{ appointment_date | date | safe_default }}</p>
    </div>
    
    <div class="section">
        <h3>POWERS GRANTED</h3>
        <p>The liquidator is hereby granted all powers under the Corporations Act 2001, including:</p>
        <ul class="powers-list">
            <li>To carry on the business of the company</li>
            <li>To sell or otherwise dispose of property</li>
            <li>To raise money on the security of assets</li>
            <li>To take out letters of administration</li>
            <li>To bring or defend legal proceedings</li>
            <li>To refer matters to arbitration</li>
            <li>To effect and maintain insurance</li>
            <li>To appoint agents and professional advisors</li>
        </ul>
    </div>
    
    <div class="signature-block">
        <p><strong>Signed:</strong> _________________________</p>
        <p>Director: {{ director_name | safe_default }}</p>
        <p>Date: {{ current_date }}</p>
    </div>
</body>
</html>'''
        
        return Template(template_content)

    def _create_director_statement_template(self) -> Template:
        """Create default director statement template"""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Statement of Director - {{ company_name | safe_default }}</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.4; }
        .header { text-align: center; margin-bottom: 30px; }
        .statement-section { margin: 20px 0; }
        .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .table th, .table td { border: 1px solid #000; padding: 8px; text-align: left; }
        .table th { background-color: #f0f0f0; font-weight: bold; }
        .amount { text-align: right; }
    </style>
</head>
<body>
    <div class="header">
        {% if logo_encoded %}
        <img src="{{ logo_encoded }}" alt="Company Logo" style="max-height: 60px;">
        {% endif %}
        <h1>STATEMENT AS TO AFFAIRS</h1>
        <h2>{{ company_name | upper | safe_default }}</h2>
        {% if abn %}<p>ABN: {{ abn | abn }}</p>{% endif %}
        {% if acn %}<p>ACN: {{ acn | acn }}</p>{% endif %}
    </div>
    
    <div class="statement-section">
        <h3>ASSETS</h3>
        {% if asset_schedule %}
        <table class="table">
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Book Value</th>
                    <th>Estimated Realizable Value</th>
                </tr>
            </thead>
            <tbody>
                {% for asset in asset_schedule %}
                <tr>
                    <td>{{ asset.description | safe_default }}</td>
                    <td class="amount">{{ asset.book_value | currency }}</td>
                    <td class="amount">{{ asset.estimated_value | currency }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No significant assets to report.</p>
        {% endif %}
    </div>
    
    <div class="statement-section">
        <h3>LIABILITIES</h3>
        {% if liability_schedule %}
        <table class="table">
            <thead>
                <tr>
                    <th>Creditor</th>
                    <th>Nature of Debt</th>
                    <th>Amount</th>
                    <th>Security</th>
                </tr>
            </thead>
            <tbody>
                {% for liability in liability_schedule %}
                <tr>
                    <td>{{ liability.creditor | safe_default }}</td>
                    <td>{{ liability.nature | safe_default }}</td>
                    <td class="amount">{{ liability.amount | currency }}</td>
                    <td>{{ liability.security | safe_default("Unsecured") }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No significant liabilities to report.</p>
        {% endif %}
    </div>
    
    <div class="statement-section">
        <h3>DIRECTOR'S DECLARATION</h3>
        <p>I, {{ director_name | safe_default }}, being a director of the above-named company, do solemnly and sincerely declare that the particulars given in this statement are true and complete to the best of my knowledge and belief.</p>
        
        <div style="margin-top: 40px;">
            <p><strong>Signature:</strong> _________________________</p>
            <p><strong>Name:</strong> {{ director_name | safe_default }}</p>
            <p><strong>Date:</strong> {{ current_date }}</p>
        </div>
    </div>
</body>
</html>'''
        
        return Template(template_content)

    async def _render_fallback_template(self, data: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """Render fallback template when main template fails"""
        try:
            fallback_template = Template('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ document_title | default("Liquidation Document") }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .content { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name | default("Company Name") }}</h1>
        <p>{{ document_type | default("Liquidation Document") }}</p>
    </div>
    
    <div class="content">
        <p><strong>Date:</strong> {{ current_date }}</p>
        <p><strong>Generated:</strong> {{ current_datetime }}</p>
        {% if liquidation_reason %}
        <p><strong>Reason:</strong> {{ liquidation_reason }}</p>
        {% endif %}
    </div>
    
    <div class="footer">
        <p><em>This is a fallback template generated due to template rendering issues.</em></p>
    </div>
</body>
</html>
            ''')
            
            rendered_html = fallback_template.render(**data)
            
            return {
                "success": True,
                "rendered_html": rendered_html,
                "css_content": "",
                "template_used": f"{template_name}_fallback",
                "template_source": "fallback",
                "warning": "Used fallback template due to rendering issues"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Even fallback template failed: {str(e)}",
                "rendered_html": f"<html><body><h1>Template Error</h1><p>Error: {str(e)}</p></body></html>"
            }

    async def _render_pdf_analyzed_template(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render template specifically generated from PDF analysis"""
        return await self._render_template(input_data)

    async def _create_multipage_document(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create multi-page document with page breaks and complex layouts"""
        input_data["multipage_support"] = True
        return await self._render_template(input_data)

    async def _integrate_logo(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate logo into document template"""
        input_data["logo_support"] = True
        return await self._render_template(input_data)

    async def _render_complex_tables(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render templates with complex table structures"""
        # Ensure table data is properly formatted
        data = input_data.get("data", {})
        
        # Format asset schedule if present
        if "asset_schedule" in data and isinstance(data["asset_schedule"], list):
            for asset in data["asset_schedule"]:
                if isinstance(asset, dict):
                    # Ensure currency formatting
                    for key in ["book_value", "estimated_value"]:
                        if key in asset:
                            asset[key] = self.env.filters['currency'](asset[key])
        
        # Format liability schedule if present
        if "liability_schedule" in data and isinstance(data["liability_schedule"], list):
            for liability in data["liability_schedule"]:
                if isinstance(liability, dict):
                    # Ensure currency formatting
                    if "amount" in liability:
                        liability["amount"] = self.env.filters['currency'](liability["amount"])
        
        input_data["data"] = data
        return await self._render_template(input_data)

    async def _apply_custom_styles(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom CSS styles to template"""
        custom_styles = input_data.get("custom_styles", "")
        result = await self._render_template(input_data)
        
        if result["success"] and custom_styles:
            # Append custom styles to CSS
            result["css_content"] += f"\n\n/* Custom Styles */\n{custom_styles}"
        
        return result

    async def _validate_template(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template syntax and structure"""
        template_name = input_data.get("template_name", "")
        
        try:
            # Check if template exists
            template_file = self.template_registry.get(template_name)
            if not template_file or not Path(template_file).exists():
                return {
                    "success": False,
                    "valid": False,
                    "error": f"Template {template_name} not found"
                }
            
            # Try to load and parse template
            template = self.env.get_template(f"{template_name}.j2")
            
            # Basic validation with minimal data
            test_data = {"company_name": "Test Company", "current_date": "Test Date"}
            rendered = template.render(**test_data)
            
            return {
                "success": True,
                "valid": True,
                "template_name": template_name,
                "template_file": template_file,
                "validation_message": "Template is valid and can be rendered"
            }
            
        except Exception as e:
            return {
                "success": True,
                "valid": False,
                "error": str(e),
                "template_name": template_name
            }

    async def _list_available_templates(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """List all available templates"""
        templates = []
        
        for template_name, template_file in self.template_registry.items():
            template_info = {
                "name": template_name,
                "file": template_file,
                "has_css": template_name in self.css_registry,
                "exists": Path(template_file).exists()
            }
            
            # Try to extract template metadata
            try:
                if template_info["exists"]:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        template_info["size"] = len(content)
                        template_info["has_logo_support"] = "logo" in content.lower()
                        template_info["has_multipage"] = "page-break" in content.lower()
                        template_info["has_tables"] = "table" in content.lower()
            except:
                pass
            
            templates.append(template_info)
        
        return {
            "success": True,
            "templates": templates,
            "total_templates": len(templates),
            "template_directory": str(self.templates_dir)
        }

    async def _get_template_info(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a specific template"""
        template_name = input_data.get("template_name", "")
        
        if template_name not in self.template_registry:
            return {
                "success": False,
                "error": f"Template {template_name} not found"
            }
        
        template_file = self.template_registry[template_name]
        info = {
            "name": template_name,
            "file": template_file,
            "exists": Path(template_file).exists(),
            "has_css": template_name in self.css_registry
        }
        
        if info["exists"]:
            try:
                # Read template content
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                info.update({
                    "size": len(content),
                    "lines": content.count('\n'),
                    "variables": self._extract_template_variables(content),
                    "features": self._analyze_template_features(content)
                })
                
                # CSS info if available
                if info["has_css"]:
                    css_file = self.css_registry[template_name]
                    with open(css_file, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    info["css_size"] = len(css_content)
                    info["css_file"] = css_file
                    
            except Exception as e:
                info["error"] = str(e)
        
        return {
            "success": True,
            "template_info": info
        }

    def _extract_template_variables(self, content: str) -> List[str]:
        """Extract Jinja2 variables from template content"""
        import re
        
        # Find all {{ variable }} patterns
        variables = set()
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        matches = re.findall(pattern, content)
        
        for match in matches:
            # Clean up the variable (remove filters, functions, etc.)
            var = match.split('|')[0].split('.')[0].strip()
            if var and not var.startswith('loop.') and var not in ['current_date', 'current_datetime']:
                variables.add(var)
        
        return sorted(list(variables))

    def _analyze_template_features(self, content: str) -> Dict[str, bool]:
        """Analyze template features"""
        features = {
            "logo_support": "logo" in content.lower(),
            "multipage": "page-break" in content.lower(),
            "tables": "<table" in content.lower() or "table" in content.lower(),
            "forms": "<form" in content.lower() or "input" in content.lower(),
            "images": "<img" in content.lower(),
            "custom_css": "style" in content.lower(),
            "conditional_logic": "{%" in content,
            "loops": "for " in content and "in " in content,
            "filters": "|" in content
        }
        
        return features

    def register_template(self, template_name: str, template_file: str, css_file: Optional[str] = None):
        """Register a new template in the registry"""
        self.template_registry[template_name] = template_file
        if css_file:
            self.css_registry[template_name] = css_file
        
        self.logger.info(f"Registered template: {template_name}")

    def get_template_registry(self) -> Dict[str, str]:
        """Get the current template registry"""
        return self.template_registry.copy()

    def get_css_registry(self) -> Dict[str, str]:
        """Get the current CSS registry"""
        return self.css_registry.copy() 