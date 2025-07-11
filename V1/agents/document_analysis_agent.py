#!/usr/bin/env python3
"""
Document Analysis Agent for Automatic Template Generation
Analyzes PDF documents to extract structure, design patterns, and content
for automatic template creation and RAG knowledge enhancement.
"""

import asyncio
import json
import logging
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from .base_agent import BaseAgent, AgentTask


@dataclass
class DocumentStructure:
    """Document structure analysis result"""
    document_name: str
    total_pages: int
    page_layouts: List[Dict[str, Any]]
    sections: List[str]
    headers_footers: Dict[str, List[str]]
    logos_images: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    form_fields: List[Dict[str, Any]]
    text_patterns: List[Dict[str, Any]]
    design_elements: Dict[str, Any]
    content_types: List[str]
    metadata: Dict[str, Any]


@dataclass
class TemplatePattern:
    """Template pattern for generation"""
    pattern_id: str
    document_type: str
    layout_type: str
    page_structure: Dict[str, Any]
    content_sections: List[Dict[str, Any]]
    design_rules: Dict[str, Any]
    variables: List[str]
    dependencies: List[str]


class DocumentAnalysisAgent(BaseAgent):
    """
    Document Analysis Agent for PDF Template Generation
    
    Analyzes PDF documents to extract:
    - Document structure and layout patterns
    - Logo and image placements
    - Multi-page designs and flows
    - Form fields and data entry points
    - Text patterns and styling
    - Table structures and formatting
    """
    
    def __init__(self, sample_dir: str = "sample", templates_dir: str = "templates", logger: Optional[logging.Logger] = None):
        super().__init__("Document Analysis Agent", logger)
        self.sample_dir = Path(sample_dir)
        self.templates_dir = Path(templates_dir)
        
        # Analysis results storage
        self.analyzed_documents: Dict[str, DocumentStructure] = {}
        self.template_patterns: Dict[str, TemplatePattern] = {}
        self.design_library: Dict[str, Any] = {}
        
        # Ensure directories exist
        self.sample_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        
        self._initialize_analysis_tools()
        
    def _initialize_analysis_tools(self):
        """Initialize document analysis capabilities"""
        self.pdf_engines = []
        
        if PYMUPDF_AVAILABLE:
            self.pdf_engines.append("pymupdf")
            self.logger.info("PyMuPDF available for advanced PDF analysis")
        
        if PDF_AVAILABLE:
            self.pdf_engines.append("pypdf2")
            self.logger.info("PyPDF2 available for basic PDF analysis")
        
        if not self.pdf_engines:
            self.logger.warning("No PDF analysis engines available - install PyMuPDF or PyPDF2")

    def get_capabilities(self) -> List[str]:
        return [
            "analyze_pdf_document",
            "extract_document_structure", 
            "generate_template_from_pdf",
            "update_rag_knowledge",
            "batch_analyze_folder",
            "extract_logo_patterns",
            "analyze_multipage_flow",
            "detect_form_fields"
        ]

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process document analysis tasks"""
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            if task_type == "analyze_pdf_document":
                return await self._analyze_pdf_document(input_data.get("file_path"))
            elif task_type == "extract_document_structure":
                return await self._extract_document_structure(input_data.get("file_path"))
            elif task_type == "generate_template_from_pdf":
                return await self._generate_template_from_pdf(input_data.get("file_path"), input_data.get("template_name"))
            elif task_type == "update_rag_knowledge":
                return await self._update_rag_knowledge(input_data.get("analysis_results"))
            elif task_type == "batch_analyze_folder":
                return await self._batch_analyze_folder(input_data.get("folder_path", self.sample_dir))
            elif task_type == "extract_logo_patterns":
                return await self._extract_logo_patterns(input_data.get("file_path"))
            elif task_type == "analyze_multipage_flow":
                return await self._analyze_multipage_flow(input_data.get("file_path"))
            elif task_type == "detect_form_fields":
                return await self._detect_form_fields(input_data.get("file_path"))
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            self.logger.error(f"Document analysis task failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "Manual template creation required"
            }

    async def _analyze_pdf_document(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive PDF document analysis"""
        if not self.pdf_engines:
            return {
                "success": False,
                "error": "No PDF analysis engines available",
                "recommendation": "Install PyMuPDF: pip install PyMuPDF"
            }
        
        file_path = Path(file_path)
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        self.logger.info(f"Analyzing PDF document: {file_path.name}")
        
        # Use best available engine
        if "pymupdf" in self.pdf_engines:
            analysis_result = await self._analyze_with_pymupdf(file_path)
        elif "pypdf2" in self.pdf_engines:
            analysis_result = await self._analyze_with_pypdf2(file_path)
        else:
            return {
                "success": False,
                "error": "No suitable PDF engine available"
            }
        
        # Store analysis results
        doc_id = hashlib.md5(str(file_path).encode()).hexdigest()
        self.analyzed_documents[doc_id] = analysis_result
        
        return {
            "success": True,
            "document_id": doc_id,
            "file_name": file_path.name,
            "analysis": asdict(analysis_result),
            "engine_used": self.pdf_engines[0] if self.pdf_engines else "none"
        }

    async def _analyze_with_pymupdf(self, file_path: Path) -> DocumentStructure:
        """Advanced PDF analysis using PyMuPDF"""
        import fitz
        
        doc = fitz.open(str(file_path))
        
        # Basic document info
        total_pages = len(doc)
        metadata = doc.metadata
        
        page_layouts = []
        sections = []
        headers_footers = {"headers": [], "footers": []}
        logos_images = []
        tables = []
        form_fields = []
        text_patterns = []
        design_elements = {}
        content_types = set()
        
        # Analyze each page
        for page_num in range(total_pages):
            page = doc[page_num]
            
            # Page layout analysis
            page_layout = {
                "page_number": page_num + 1,
                "dimensions": {
                    "width": page.rect.width,
                    "height": page.rect.height
                },
                "orientation": "portrait" if page.rect.height > page.rect.width else "landscape"
            }
            
            # Extract text blocks with positioning
            blocks = page.get_text("dict")
            text_blocks = []
            
            for block in blocks["blocks"]:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_blocks.append({
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "font": span["font"],
                                "size": span["size"],
                                "flags": span["flags"]
                            })
            
            page_layout["text_blocks"] = text_blocks
            
            # Identify headers and footers (top 15% and bottom 15% of page)
            page_height = page.rect.height
            header_zone = page_height * 0.15
            footer_zone = page_height * 0.85
            
            page_headers = []
            page_footers = []
            
            for block in text_blocks:
                bbox = block["bbox"]
                if bbox[1] < header_zone:  # Top of page
                    page_headers.append(block["text"].strip())
                elif bbox[1] > footer_zone:  # Bottom of page
                    page_footers.append(block["text"].strip())
            
            headers_footers["headers"].extend(page_headers)
            headers_footers["footers"].extend(page_footers)
            
            # Extract images and potential logos
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                image_info = {
                    "page": page_num + 1,
                    "index": img_index,
                    "xref": img[0],
                    "bbox": page.get_image_bbox(img),
                    "size_estimate": "logo" if max(page.get_image_bbox(img)[2:]) < 200 else "content"
                }
                logos_images.append(image_info)
            
            # Detect tables (simplified - look for grid patterns)
            tables_on_page = self._detect_tables_in_text_blocks(text_blocks)
            for table in tables_on_page:
                table["page"] = page_num + 1
                tables.append(table)
            
            # Extract form fields
            if hasattr(page, 'widgets'):
                for widget in page.widgets():
                    form_fields.append({
                        "page": page_num + 1,
                        "field_name": widget.field_name,
                        "field_type": widget.field_type_string,
                        "bbox": widget.rect,
                        "value": widget.field_value
                    })
            
            page_layouts.append(page_layout)
        
        # Analyze document structure
        sections = self._identify_document_sections(page_layouts)
        text_patterns = self._analyze_text_patterns(page_layouts)
        design_elements = self._analyze_design_elements(page_layouts)
        content_types = self._classify_content_types(page_layouts, logos_images, tables, form_fields)
        
        doc.close()
        
        return DocumentStructure(
            document_name=file_path.name,
            total_pages=total_pages,
            page_layouts=page_layouts,
            sections=sections,
            headers_footers=headers_footers,
            logos_images=logos_images,
            tables=tables,
            form_fields=form_fields,
            text_patterns=text_patterns,
            design_elements=design_elements,
            content_types=list(content_types),
            metadata=metadata
        )

    async def _analyze_with_pypdf2(self, file_path: Path) -> DocumentStructure:
        """Basic PDF analysis using PyPDF2"""
        import PyPDF2
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            total_pages = len(reader.pages)
            metadata = reader.metadata or {}
            
            page_layouts = []
            sections = []
            text_content = []
            
            # Extract text from each page
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    text_content.append(text)
                    
                    # Basic page layout info
                    page_layout = {
                        "page_number": page_num + 1,
                        "text_content": text,
                        "text_length": len(text),
                        "estimated_sections": self._estimate_sections_from_text(text)
                    }
                    page_layouts.append(page_layout)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    page_layouts.append({
                        "page_number": page_num + 1,
                        "text_content": "",
                        "error": str(e)
                    })
            
            # Analyze overall document structure
            sections = self._analyze_document_sections_from_text(text_content)
            
        return DocumentStructure(
            document_name=file_path.name,
            total_pages=total_pages,
            page_layouts=page_layouts,
            sections=sections,
            headers_footers={"headers": [], "footers": []},
            logos_images=[],
            tables=[],
            form_fields=[],
            text_patterns=[],
            design_elements={},
            content_types=["text_document"],
            metadata=dict(metadata) if metadata else {}
        )

    def _detect_tables_in_text_blocks(self, text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect table structures in text blocks"""
        tables = []
        
        # Group text blocks by vertical position (rows)
        rows = {}
        for block in text_blocks:
            y_pos = int(block["bbox"][1] / 5) * 5  # Group by 5-pixel intervals
            if y_pos not in rows:
                rows[y_pos] = []
            rows[y_pos].append(block)
        
        # Look for rows with multiple aligned columns
        for y_pos, row_blocks in rows.items():
            if len(row_blocks) >= 3:  # Potential table row
                # Sort by x position
                row_blocks.sort(key=lambda b: b["bbox"][0])
                
                # Check for regular column spacing
                x_positions = [block["bbox"][0] for block in row_blocks]
                if self._has_regular_spacing(x_positions):
                    tables.append({
                        "type": "table_row",
                        "y_position": y_pos,
                        "columns": len(row_blocks),
                        "cells": [block["text"] for block in row_blocks],
                        "bbox": [
                            min(b["bbox"][0] for b in row_blocks),
                            min(b["bbox"][1] for b in row_blocks),
                            max(b["bbox"][2] for b in row_blocks),
                            max(b["bbox"][3] for b in row_blocks)
                        ]
                    })
        
        return tables

    def _has_regular_spacing(self, positions: List[float], tolerance: float = 20) -> bool:
        """Check if positions have regular spacing"""
        if len(positions) < 3:
            return False
        
        spacings = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
        avg_spacing = sum(spacings) / len(spacings)
        
        # Check if all spacings are within tolerance of average
        return all(abs(spacing - avg_spacing) <= tolerance for spacing in spacings)

    def _identify_document_sections(self, page_layouts: List[Dict[str, Any]]) -> List[str]:
        """Identify document sections from page layouts"""
        sections = []
        
        # Common liquidation document sections
        common_sections = [
            "header", "company_information", "resolution_details", 
            "director_details", "liquidator_appointment", "creditor_notice",
            "asset_schedule", "liability_schedule", "signature_block", "footer"
        ]
        
        # Analyze text patterns to identify sections
        for page in page_layouts:
            if "text_blocks" in page:
                for block in page["text_blocks"]:
                    text = block["text"].lower()
                    for section in common_sections:
                        if any(keyword in text for keyword in self._get_section_keywords(section)):
                            if section not in sections:
                                sections.append(section)
        
        return sections

    def _get_section_keywords(self, section: str) -> List[str]:
        """Get keywords for identifying document sections"""
        keywords_map = {
            "header": ["letterhead", "company name", "abn", "acn"],
            "company_information": ["company", "entity", "registered office"],
            "resolution_details": ["resolution", "resolved", "motion"],
            "director_details": ["director", "board", "signature"],
            "liquidator_appointment": ["liquidator", "appointment", "wind up"],
            "creditor_notice": ["creditor", "notice", "meeting"],
            "asset_schedule": ["assets", "property", "inventory"],
            "liability_schedule": ["liabilities", "debts", "creditors"],
            "signature_block": ["signature", "date", "witness"],
            "footer": ["page", "document", "confidential"]
        }
        return keywords_map.get(section, [])

    def _analyze_text_patterns(self, page_layouts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze text patterns for template generation"""
        patterns = []
        
        # Font size patterns (headers, body text, etc.)
        font_sizes = {}
        for page in page_layouts:
            if "text_blocks" in page:
                for block in page["text_blocks"]:
                    size = block.get("size", 12)
                    if size not in font_sizes:
                        font_sizes[size] = []
                    font_sizes[size].append(block["text"])
        
        # Classify text by size
        for size, texts in font_sizes.items():
            if size >= 16:
                pattern_type = "heading"
            elif size >= 12:
                pattern_type = "body_text"
            else:
                pattern_type = "small_text"
            
            patterns.append({
                "type": pattern_type,
                "font_size": size,
                "sample_count": len(texts),
                "examples": texts[:3]  # First 3 examples
            })
        
        return patterns

    def _analyze_design_elements(self, page_layouts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze design elements for styling"""
        design = {
            "page_margins": {},
            "text_alignment": {},
            "font_usage": {},
            "layout_patterns": []
        }
        
        # Calculate page margins
        if page_layouts:
            first_page = page_layouts[0]
            if "text_blocks" in first_page:
                text_blocks = first_page["text_blocks"]
                if text_blocks:
                    min_x = min(block["bbox"][0] for block in text_blocks)
                    max_x = max(block["bbox"][2] for block in text_blocks)
                    min_y = min(block["bbox"][1] for block in text_blocks)
                    max_y = max(block["bbox"][3] for block in text_blocks)
                    
                    page_width = first_page["dimensions"]["width"]
                    page_height = first_page["dimensions"]["height"]
                    
                    design["page_margins"] = {
                        "left": min_x,
                        "right": page_width - max_x,
                        "top": min_y,
                        "bottom": page_height - max_y
                    }
        
        return design

    def _classify_content_types(self, page_layouts: List[Dict[str, Any]], 
                              logos_images: List[Dict[str, Any]], 
                              tables: List[Dict[str, Any]], 
                              form_fields: List[Dict[str, Any]]) -> set:
        """Classify the types of content in the document"""
        content_types = {"text_document"}
        
        if logos_images:
            content_types.add("has_images")
            if any(img.get("size_estimate") == "logo" for img in logos_images):
                content_types.add("has_logo")
        
        if tables:
            content_types.add("has_tables")
        
        if form_fields:
            content_types.add("has_forms")
        
        if len(page_layouts) > 1:
            content_types.add("multipage")
        
        return content_types

    def _estimate_sections_from_text(self, text: str) -> List[str]:
        """Estimate document sections from text content (PyPDF2 fallback)"""
        sections = []
        text_lower = text.lower()
        
        section_indicators = {
            "company_header": ["company", "pty ltd", "abn", "acn"],
            "resolution": ["resolution", "resolved", "motion"],
            "appointment": ["appointment", "liquidator"],
            "notice": ["notice", "creditor", "meeting"],
            "statement": ["statement", "affairs", "assets", "liabilities"],
            "signature": ["signature", "director", "date"]
        }
        
        for section, keywords in section_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                sections.append(section)
        
        return sections

    def _analyze_document_sections_from_text(self, text_content: List[str]) -> List[str]:
        """Analyze document sections from text content"""
        all_sections = set()
        
        for text in text_content:
            sections = self._estimate_sections_from_text(text)
            all_sections.update(sections)
        
        return list(all_sections)

    async def _generate_template_from_pdf(self, file_path: str, template_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate Jinja2 template from analyzed PDF structure"""
        # First analyze the document
        analysis_result = await self._analyze_pdf_document(file_path)
        
        if not analysis_result["success"]:
            return analysis_result
        
        analysis = analysis_result["analysis"]
        doc_name = Path(file_path).stem
        template_name = template_name or f"{doc_name}_template"
        
        # Generate template content
        template_content = await self._create_jinja_template(analysis, template_name)
        
        # Save template file
        template_file = self.templates_dir / f"{template_name}.j2"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        # Generate CSS for styling
        css_content = await self._create_css_styles(analysis)
        css_file = self.templates_dir / f"{template_name}.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        return {
            "success": True,
            "template_name": template_name,
            "template_file": str(template_file),
            "css_file": str(css_file),
            "document_analysis": analysis,
            "generated_sections": analysis["sections"],
            "supports_multipage": analysis["total_pages"] > 1,
            "has_logo": "has_logo" in analysis["content_types"],
            "has_tables": "has_tables" in analysis["content_types"]
        }

    async def _create_jinja_template(self, analysis: Dict[str, Any], template_name: str) -> str:
        """Create Jinja2 template from document analysis"""
        template_parts = []
        
        # HTML Document structure
        template_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ document_title | default('""" + template_name + """') }}</title>
    <style>
        @page {
            size: A4;
            margin: {{ page_margins.top | default('2cm') }} {{ page_margins.right | default('2cm') }} {{ page_margins.bottom | default('2cm') }} {{ page_margins.left | default('2cm') }};
        }
        body {
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.4;
            color: #000;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
        }
        .logo {
            max-height: 80px;
            margin-bottom: 10px;
        }
        .company-details {
            font-weight: bold;
            margin-bottom: 20px;
        }
        .section {
            margin-bottom: 25px;
        }
        .section-title {
            font-weight: bold;
            font-size: 14pt;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .table th, .table td {
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
        }
        .table th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        .signature-block {
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
        }
        .signature-line {
            width: 200px;
            border-bottom: 1px solid #000;
            margin-bottom: 5px;
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 10pt;
            border-top: 1px solid #ccc;
            padding-top: 5px;
        }
        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body>""")
        
        # Header section with logo support
        if "has_logo" in analysis.get("content_types", []):
            template_parts.append("""
    <div class="header">
        {% if company_logo %}
        <img src="{{ company_logo }}" alt="Company Logo" class="logo">
        {% endif %}
        <div class="company-details">
            <h1>{{ company_name | upper }}</h1>
            {% if abn %}<p>ABN: {{ abn }}</p>{% endif %}
            {% if acn %}<p>ACN: {{ acn }}</p>{% endif %}
            {% if registered_office %}<p>{{ registered_office }}</p>{% endif %}
        </div>
    </div>""")
        else:
            template_parts.append("""
    <div class="header">
        <div class="company-details">
            <h1>{{ company_name | upper }}</h1>
            {% if abn %}<p>ABN: {{ abn }}</p>{% endif %}
            {% if acn %}<p>ACN: {{ acn }}</p>{% endif %}
            {% if registered_office %}<p>{{ registered_office }}</p>{% endif %}
        </div>
    </div>""")
        
        # Generate sections based on analysis
        sections = analysis.get("sections", [])
        
        for section in sections:
            if section == "company_information":
                template_parts.append("""
    <div class="section">
        <h2 class="section-title">Company Information</h2>
        <p><strong>Entity Name:</strong> {{ entity_name | default(company_name) }}</p>
        <p><strong>Entity Type:</strong> {{ entity_type | default('Australian Private Company') }}</p>
        <p><strong>Status:</strong> {{ company_status | default('Active') }}</p>
        {% if directors %}
        <p><strong>Directors:</strong>
        {% for director in directors %}
            {{ director }}{% if not loop.last %}, {% endif %}
        {% endfor %}
        </p>
        {% endif %}
    </div>""")
            
            elif section == "resolution_details":
                template_parts.append("""
    <div class="section">
        <h2 class="section-title">Resolution Details</h2>
        <p><strong>Resolution Type:</strong> {{ resolution_type | default('Special Resolution') }}</p>
        <p><strong>Date of Resolution:</strong> {{ resolution_date | default(current_date) }}</p>
        <p><strong>Meeting Type:</strong> {{ meeting_type | default('Board Meeting') }}</p>
        
        <div style="margin: 20px 0;">
            <p><strong>IT IS RESOLVED:</strong></p>
            <ol>
                {% for resolution_item in resolution_items %}
                <li>{{ resolution_item }}</li>
                {% endfor %}
            </ol>
        </div>
        
        {% if liquidation_reason %}
        <p><strong>Reason for Liquidation:</strong> {{ liquidation_reason }}</p>
        {% endif %}
    </div>""")
            
            elif section == "liquidator_appointment":
                template_parts.append("""
    <div class="section">
        <h2 class="section-title">Liquidator Appointment</h2>
        <p><strong>Liquidator Name:</strong> {{ liquidator_name }}</p>
        <p><strong>Registration Number:</strong> {{ liquidator_registration | default('TBA') }}</p>
        <p><strong>Address:</strong> {{ liquidator_address | default('TBA') }}</p>
        <p><strong>Contact Details:</strong> {{ liquidator_contact | default('TBA') }}</p>
        
        <p style="margin-top: 15px;">
            The liquidator is hereby authorized to exercise all powers conferred by the 
            Corporations Act 2001, including but not limited to the powers specified in 
            sections 477 to 482 of the Act.
        </p>
    </div>""")
        
        # Add table support if detected
        if "has_tables" in analysis.get("content_types", []):
            template_parts.append("""
    {% if asset_schedule or liability_schedule or creditor_details %}
    <div class="section">
        {% if asset_schedule %}
        <h2 class="section-title">Schedule of Assets</h2>
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
                    <td>{{ asset.description }}</td>
                    <td>${{ asset.book_value | default('0.00') }}</td>
                    <td>${{ asset.estimated_value | default('0.00') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
        
        {% if liability_schedule %}
        <h2 class="section-title">Schedule of Liabilities</h2>
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
                    <td>{{ liability.creditor }}</td>
                    <td>{{ liability.nature }}</td>
                    <td>${{ liability.amount }}</td>
                    <td>{{ liability.security | default('Unsecured') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>
    {% endif %}""")
        
        # Multi-page support
        if analysis.get("total_pages", 1) > 1:
            template_parts.append("""
    {% if additional_pages %}
    {% for page in additional_pages %}
    <div class="page-break">
        <h2 class="section-title">{{ page.title }}</h2>
        {{ page.content | safe }}
    </div>
    {% endfor %}
    {% endif %}""")
        
        # Signature block
        template_parts.append("""
    <div class="signature-block">
        <div>
            <div class="signature-line"></div>
            <p><strong>Director Signature</strong></p>
            <p>{{ director_name | default('Director Name') }}</p>
            <p>Date: {{ signature_date | default(current_date) }}</p>
        </div>
        {% if witness_required %}
        <div>
            <div class="signature-line"></div>
            <p><strong>Witness</strong></p>
            <p>Name: ________________________</p>
            <p>Date: {{ signature_date | default(current_date) }}</p>
        </div>
        {% endif %}
    </div>
    
    <div class="footer">
        <p>{{ footer_text | default('This document was generated for liquidation purposes. Page {{ page_number | default('1') }} of {{ total_pages | default('1') }}') }}</p>
    </div>
</body>
</html>""")
        
        return "\n".join(template_parts)

    async def _create_css_styles(self, analysis: Dict[str, Any]) -> str:
        """Create CSS styles based on document analysis"""
        css_parts = []
        
        # Base styles
        css_parts.append("""/* Auto-generated CSS from document analysis */
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'Times New Roman', serif;
    font-size: 12pt;
    line-height: 1.4;
    color: #000;
    margin: 0;
    padding: 0;
}""")
        
        # Add margin styles if detected
        design_elements = analysis.get("design_elements", {})
        if "page_margins" in design_elements:
            margins = design_elements["page_margins"]
            css_parts.append(f"""
.content-area {{
    margin-left: {margins.get('left', 72)}px;
    margin-right: {margins.get('right', 72)}px;
    margin-top: {margins.get('top', 72)}px;
    margin-bottom: {margins.get('bottom', 72)}px;
}}""")
        
        # Font size patterns
        text_patterns = analysis.get("text_patterns", [])
        for pattern in text_patterns:
            if pattern["type"] == "heading":
                css_parts.append(f"""
.heading-{int(pattern['font_size'])} {{
    font-size: {pattern['font_size']}pt;
    font-weight: bold;
    margin-bottom: 10px;
}}""")
        
        # Logo and image styles
        if "has_logo" in analysis.get("content_types", []):
            css_parts.append("""
.logo-container {
    text-align: center;
    margin-bottom: 20px;
}

.company-logo {
    max-height: 80px;
    max-width: 200px;
}""")
        
        # Table styles if tables detected
        if "has_tables" in analysis.get("content_types", []):
            css_parts.append("""
.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 11pt;
}

.data-table th,
.data-table td {
    border: 1px solid #000;
    padding: 6px 8px;
    text-align: left;
}

.data-table th {
    background-color: #f5f5f5;
    font-weight: bold;
}

.data-table .amount {
    text-align: right;
}""")
        
        # Multi-page styles
        if analysis.get("total_pages", 1) > 1:
            css_parts.append("""
.page-break {
    page-break-before: always;
}

.page-header {
    margin-bottom: 30px;
}

.page-footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    font-size: 10pt;
    border-top: 1px solid #ccc;
    padding-top: 5px;
}""")
        
        return "\n".join(css_parts)

    async def _batch_analyze_folder(self, folder_path: str) -> Dict[str, Any]:
        """Analyze all PDF files in a folder"""
        folder = Path(folder_path)
        if not folder.exists():
            return {
                "success": False,
                "error": f"Folder not found: {folder}"
            }
        
        pdf_files = list(folder.glob("*.pdf"))
        results = {}
        successful = 0
        failed = 0
        
        self.logger.info(f"Analyzing {len(pdf_files)} PDF files in {folder}")
        
        for pdf_file in pdf_files:
            try:
                result = await self._analyze_pdf_document(str(pdf_file))
                results[pdf_file.name] = result
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                results[pdf_file.name] = {
                    "success": False,
                    "error": str(e)
                }
                failed += 1
        
        return {
            "success": True,
            "total_files": len(pdf_files),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    async def _update_rag_knowledge(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Update RAG knowledge base with analysis results"""
        # This will be called by the supervisor to update the RAG agent
        return {
            "success": True,
            "message": "RAG knowledge update requested",
            "analysis_data": analysis_results
        }

    def get_analyzed_documents(self) -> Dict[str, DocumentStructure]:
        """Get all analyzed documents"""
        return self.analyzed_documents

    def get_template_patterns(self) -> Dict[str, TemplatePattern]:
        """Get all extracted template patterns"""
        return self.template_patterns 