"""
Professional PDF Generator for Legal Documents
Creates court-quality PDFs matching Federal Court standards
"""

import asyncio
import logging
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import tempfile
import os

# Enhanced PDF generation libraries
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        PageBreak, KeepTogether, NextPageTemplate, PageTemplate
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus.frames import Frame
    from reportlab.platypus.doctemplate import BaseDocTemplate
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class LawFirm:
    """Law firm information for document headers"""
    name: str
    address: str
    phone: str
    email: str
    website: str
    principal: str
    registration: str
    letterhead_style: str  # 'formal', 'modern', 'classic', 'corporate'
    color_scheme: tuple  # RGB color for headers


# Pre-defined law firms with different styles
LAW_FIRMS = [
    LawFirm(
        name="Harrison Legal Partners",
        address="Level 42, MLC Centre, 19-29 Martin Place, Sydney NSW 2000",
        phone="+61 2 9230 4567",
        email="partners@harrisonlegal.com.au",
        website="www.harrisonlegal.com.au",
        principal="Margaret Harrison QC",
        registration="NSW Law Society 12345",
        letterhead_style="formal",
        color_scheme=(0.1, 0.2, 0.5)  # Navy blue
    ),
    LawFirm(
        name="Corporate Solutions Legal",
        address="Suite 1500, 385 Bourke Street, Melbourne VIC 3000",
        phone="+61 3 8622 3456",
        email="info@corpsolutions.legal",
        website="www.corpsolutions.legal",
        principal="David Chen, Senior Partner",
        registration="VIC Bar Association 67890",
        letterhead_style="modern",
        color_scheme=(0.8, 0.1, 0.1)  # Deep red
    ),
    LawFirm(
        name="Queensland Commercial Chambers",
        address="Level 28, Riparian Plaza, 71 Eagle Street, Brisbane QLD 4000",
        phone="+61 7 3221 8901",
        email="chambers@qldcommercial.com.au",
        website="www.qldcommercial.com.au",
        principal="Sarah Mitchell SC",
        registration="QLD Bar Association 24681",
        letterhead_style="classic",
        color_scheme=(0.0, 0.4, 0.2)  # Forest green
    ),
    LawFirm(
        name="Enterprise Legal Group",
        address="Level 15, 140 St Georges Terrace, Perth WA 6000",
        phone="+61 8 9486 1234",
        email="legal@enterprisegroup.com.au", 
        website="www.enterprisegroup.com.au",
        principal="Robert Williams, Managing Partner",
        registration="WA Law Society 13579",
        letterhead_style="corporate",
        color_scheme=(0.4, 0.0, 0.6)  # Purple
    ),
    LawFirm(
        name="Adelaide Commercial Law",
        address="Level 12, 25 Grenfell Street, Adelaide SA 5000",
        phone="+61 8 8123 5678",
        email="contact@adelaidecommercial.law",
        website="www.adelaidecommercial.law",
        principal="Patricia Thompson, Principal",
        registration="SA Law Society 97531",
        letterhead_style="formal",
        color_scheme=(0.0, 0.3, 0.7)  # Royal blue
    )
]


@dataclass
class DocumentTemplate:
    """Document template configuration"""
    name: str
    document_type: str  # 'affidavit', 'resolution', 'creditor_notice', 'director_statement', 'asset_notice'
    layout_style: str   # 'traditional', 'modern', 'detailed', 'summary', 'formal'
    font_family: str
    font_size_body: int
    font_size_heading: int
    margin_style: str   # 'wide', 'narrow', 'standard'
    header_style: str   # 'full', 'minimal', 'detailed', 'logo'
    footer_style: str   # 'simple', 'detailed', 'legal'


# Document template variations
DOCUMENT_TEMPLATES = [
    # Professional Affidavit Templates
    DocumentTemplate("Federal Court Affidavit", "affidavit", "traditional", "Times-Roman", 11, 14, "wide", "full", "legal"),
    DocumentTemplate("Supreme Court Affidavit", "affidavit", "formal", "Helvetica", 10, 13, "standard", "detailed", "simple"),
    DocumentTemplate("Commercial Affidavit", "affidavit", "modern", "Helvetica-Bold", 10, 12, "narrow", "minimal", "detailed"),
    
    # Liquidation Resolution Templates  
    DocumentTemplate("Board Resolution", "resolution", "formal", "Times-Roman", 10, 13, "wide", "full", "legal"),
    DocumentTemplate("Members Resolution", "resolution", "traditional", "Helvetica", 11, 14, "standard", "detailed", "simple"),
    DocumentTemplate("Special Resolution", "resolution", "detailed", "Times-Bold", 10, 12, "narrow", "minimal", "detailed"),
    
    # Creditor Notification Templates
    DocumentTemplate("Formal Creditor Notice", "creditor_notice", "formal", "Helvetica", 10, 12, "standard", "full", "legal"),
    DocumentTemplate("Standard Creditor Notice", "creditor_notice", "summary", "Times-Roman", 11, 13, "wide", "detailed", "simple"),
    DocumentTemplate("Urgent Creditor Notice", "creditor_notice", "modern", "Helvetica-Bold", 10, 14, "narrow", "minimal", "detailed"),
    
    # Director Statement Templates
    DocumentTemplate("Director's Declaration", "director_statement", "formal", "Times-Roman", 10, 13, "wide", "full", "legal"),
    DocumentTemplate("Director's Report", "director_statement", "detailed", "Helvetica", 11, 12, "standard", "detailed", "simple"),
    DocumentTemplate("Director's Statement", "director_statement", "traditional", "Times-Bold", 10, 14, "narrow", "minimal", "detailed"),
    
    # Asset Realization Templates
    DocumentTemplate("Asset Disposal Notice", "asset_notice", "modern", "Helvetica", 10, 12, "standard", "full", "legal"),
    DocumentTemplate("Realization Report", "asset_notice", "detailed", "Times-Roman", 11, 13, "wide", "detailed", "simple"),
    DocumentTemplate("Asset Sale Notice", "asset_notice", "summary", "Helvetica-Bold", 10, 14, "narrow", "minimal", "detailed")
]


@dataclass
class CompanyDetails:
    """Company information for legal documents"""
    name: str
    acn: Optional[str] = None
    abn: Optional[str] = None
    registered_office: Optional[str] = None
    principal_place: Optional[str] = None
    directors: Optional[List[str]] = None
    liquidator: Optional[str] = None
    liquidator_address: Optional[str] = None
    liquidator_registration: Optional[str] = None


@dataclass
class FinancialSummary:
    """Financial information for legal documents"""
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    estimated_surplus_deficiency: Optional[float] = None
    secured_creditors: Optional[float] = None
    preferential_creditors: Optional[float] = None
    unsecured_creditors: Optional[float] = None
    employee_entitlements: Optional[float] = None
    cash_at_bank: Optional[float] = None
    debtors: Optional[float] = None
    stock_inventory: Optional[float] = None
    plant_equipment: Optional[float] = None
    real_property: Optional[float] = None


@dataclass
class LegalClause:
    """Legal clause with reference and content"""
    reference: str
    title: str
    content: str
    subsections: Optional[List[str]] = None


class ProfessionalDocumentTemplate(BaseDocTemplate):
    """Professional document template matching various law firm standards"""
    
    def __init__(self, filename, law_firm: LawFirm, doc_template: DocumentTemplate, **kwargs):
        self.allowSplitting = 1
        self.law_firm = law_firm
        self.doc_template = doc_template
        
        # Set margins based on template style
        margins = self._get_margins(doc_template.margin_style)
        
        BaseDocTemplate.__init__(self, filename, **kwargs)
        
        # Create frames for the document with variable margins
        frame = Frame(
            margins['left'], margins['bottom'], 
            self.width - margins['left'] - margins['right'], 
            self.height - margins['top'] - margins['bottom'],
            leftPadding=margins['padding'], 
            bottomPadding=margins['padding'], 
            rightPadding=margins['padding'], 
            topPadding=margins['padding']
        )
        
        # Create page template
        template = PageTemplate(id='main', frames=[frame], onPage=self._add_page_decorations)
        self.addPageTemplates([template])
    
    def _get_margins(self, margin_style: str) -> dict:
        """Get margin settings based on style"""
        if margin_style == 'wide':
            return {'left': 1.5*inch, 'right': 1.5*inch, 'top': 1.2*inch, 'bottom': 1*inch, 'padding': 10}
        elif margin_style == 'narrow':
            return {'left': 0.75*inch, 'right': 0.75*inch, 'top': 0.8*inch, 'bottom': 0.6*inch, 'padding': 5}
        else:  # standard
            return {'left': 1*inch, 'right': 1*inch, 'top': 1*inch, 'bottom': 0.8*inch, 'padding': 8}
    
    def _add_page_decorations(self, canvas, doc):
        """Add headers, footers, and page decorations based on law firm and template"""
        canvas.saveState()
        
        # Set colors based on law firm
        header_color = colors.Color(*self.law_firm.color_scheme)
        
        # Different header styles based on law firm letterhead style
        if self.law_firm.letterhead_style == 'formal':
            self._add_formal_header(canvas, header_color)
        elif self.law_firm.letterhead_style == 'modern':
            self._add_modern_header(canvas, header_color)
        elif self.law_firm.letterhead_style == 'classic':
            self._add_classic_header(canvas, header_color)
        elif self.law_firm.letterhead_style == 'corporate':
            self._add_corporate_header(canvas, header_color)
        
        # Different footer styles based on document template
        if self.doc_template.footer_style == 'legal':
            self._add_legal_footer(canvas)
        elif self.doc_template.footer_style == 'detailed':
            self._add_detailed_footer(canvas)
        else:  # simple
            self._add_simple_footer(canvas)
        
        canvas.restoreState()
    
    def _add_formal_header(self, canvas, color):
        """Add formal law firm header"""
        canvas.setFillColor(color)
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(A4[0]/2, A4[1] - 40, self.law_firm.name.upper())
        
        canvas.setFont('Times-Roman', 10)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(A4[0]/2, A4[1] - 55, self.law_firm.address)
        canvas.drawCentredString(A4[0]/2, A4[1] - 68, f"Tel: {self.law_firm.phone} | Email: {self.law_firm.email}")
        
        # Formal border
        canvas.setStrokeColor(color)
        canvas.setLineWidth(2)
        canvas.line(50, A4[1] - 80, A4[0] - 50, A4[1] - 80)
        canvas.setLineWidth(0.5)
        canvas.line(50, A4[1] - 85, A4[0] - 50, A4[1] - 85)
    
    def _add_modern_header(self, canvas, color):
        """Add modern law firm header"""
        # Color block header
        canvas.setFillColor(color)
        canvas.rect(0, A4[1] - 70, A4[0], 70, fill=1)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 18)
        canvas.drawString(60, A4[1] - 35, self.law_firm.name)
        
        canvas.setFont('Helvetica', 9)
        canvas.drawString(60, A4[1] - 50, self.law_firm.address.split(',')[0])
        canvas.drawRightString(A4[0] - 60, A4[1] - 35, self.law_firm.phone)
        canvas.drawRightString(A4[0] - 60, A4[1] - 50, self.law_firm.website)
    
    def _add_classic_header(self, canvas, color):
        """Add classic law firm header"""
        canvas.setFillColor(color)
        canvas.setFont('Times-Bold', 14)
        canvas.drawCentredString(A4[0]/2, A4[1] - 35, self.law_firm.name)
        
        canvas.setFont('Times-Italic', 10)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(A4[0]/2, A4[1] - 50, f"Principal: {self.law_firm.principal}")
        canvas.drawCentredString(A4[0]/2, A4[1] - 62, self.law_firm.registration)
        
        # Classic double line
        canvas.setStrokeColor(color)
        canvas.setLineWidth(1)
        canvas.line(100, A4[1] - 75, A4[0] - 100, A4[1] - 75)
        canvas.line(100, A4[1] - 78, A4[0] - 100, A4[1] - 78)
    
    def _add_corporate_header(self, canvas, color):
        """Add corporate law firm header"""
        canvas.setStrokeColor(color)
        canvas.setFillColor(color)
        canvas.setLineWidth(8)
        canvas.line(0, A4[1] - 20, A4[0], A4[1] - 20)
        
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica-Bold', 16)
        canvas.drawString(80, A4[1] - 45, self.law_firm.name)
        
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0] - 80, A4[1] - 35, f"{self.law_firm.phone} | {self.law_firm.email}")
        canvas.drawRightString(A4[0] - 80, A4[1] - 45, self.law_firm.address.split(',')[0])
    
    def _add_legal_footer(self, canvas):
        """Add comprehensive legal footer"""
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        page_num = canvas.getPageNumber()
        
        # Legal disclaimers and page number
        canvas.drawString(50, 40, "This document contains confidential and legally privileged information")
        canvas.drawRightString(A4[0] - 50, 40, f"Page {page_num}")
        canvas.drawCentredString(A4[0]/2, 25, f"{self.law_firm.registration} | {self.law_firm.website}")
        
        # Footer line
        canvas.setStrokeColor(colors.lightgrey)
        canvas.setLineWidth(0.5)
        canvas.line(50, 55, A4[0] - 50, 55)
    
    def _add_detailed_footer(self, canvas):
        """Add detailed footer with firm information"""
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.darkgrey)
        page_num = canvas.getPageNumber()
        
        canvas.drawString(50, 30, f"{self.law_firm.name} | {self.law_firm.principal}")
        canvas.drawRightString(A4[0] - 50, 30, f"Page {page_num}")
    
    def _add_simple_footer(self, canvas):
        """Add simple footer with just page number"""
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(A4[0] - 50, 30, f"Page {page_num}")


class ProfessionalPDFGenerator:
    """Enhanced PDF generator for professional legal documents"""
    
    def __init__(self, config):
        self.config = config
        self.styles = None
        self._setup_professional_styles()
        
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not installed. PDF generation will be limited.")
    
    def _setup_professional_styles(self):
        """Setup professional document styles matching court standards"""
        if not REPORTLAB_AVAILABLE:
            return
            
        self.styles = getSampleStyleSheet()
        
        # Court document title style
        self.styles.add(ParagraphStyle(
            name='CourtTitle',
            parent=self.styles['Title'],
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        # Legal heading style
        self.styles.add(ParagraphStyle(
            name='LegalHeading',
            parent=self.styles['Heading1'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=15,
            spaceBefore=20,
            alignment=TA_CENTER,
            textColor=colors.black,
            borderWidth=1,
            borderColor=colors.black,
            borderPadding=5
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=10,
            spaceBefore=15,
            alignment=TA_LEFT,
            textColor=colors.black
        ))
        
        # Professional body text
        self.styles.add(ParagraphStyle(
            name='ProfessionalBody',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=10,
            spaceBefore=5,
            leftIndent=20,
            rightIndent=20,
            alignment=TA_JUSTIFY,
            textColor=colors.black
        ))
        
        # Legal clause style
        self.styles.add(ParagraphStyle(
            name='LegalClause',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=8,
            spaceBefore=5,
            leftIndent=30,
            rightIndent=20,
            alignment=TA_JUSTIFY,
            bulletIndent=20
        ))
        
        # Financial table style
        self.styles.add(ParagraphStyle(
            name='FinancialText',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            alignment=TA_RIGHT
        ))
        
        # Signature style
        self.styles.add(ParagraphStyle(
            name='SignatureBlock',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=30,
            spaceBefore=20,
            alignment=TA_LEFT
        ))
        
        # Legal reference style
        self.styles.add(ParagraphStyle(
            name='LegalReference',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Oblique',
            spaceAfter=5,
            textColor=colors.grey
        ))
    
    def _select_law_firm(self) -> LawFirm:
        """Randomly select a law firm for document variety"""
        return random.choice(LAW_FIRMS)
    
    def _select_document_template(self, document_type: str) -> DocumentTemplate:
        """Select appropriate document template based on type"""
        templates = [t for t in DOCUMENT_TEMPLATES if t.document_type == document_type]
        return random.choice(templates) if templates else DOCUMENT_TEMPLATES[0]
    
    def _setup_dynamic_styles(self, doc_template: DocumentTemplate):
        """Setup styles based on selected document template"""
        if not REPORTLAB_AVAILABLE:
            return
            
        # Update styles based on template preferences
        font_family = doc_template.font_family
        body_size = doc_template.font_size_body
        heading_size = doc_template.font_size_heading
        
        # Safely handle font family names
        if font_family == 'Times-Bold':
            base_font = 'Times-Roman'
            bold_font = 'Times-Bold'
        elif font_family == 'Helvetica-Bold':
            base_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
        else:
            base_font = font_family
            bold_font = font_family + '-Bold' if 'Times' in font_family or 'Helvetica' in font_family else font_family
        
        # Override base styles with template-specific fonts and sizes
        self.styles['ProfessionalBody'].fontName = base_font
        self.styles['ProfessionalBody'].fontSize = body_size
        
        self.styles['SectionHeading'].fontName = bold_font
        self.styles['SectionHeading'].fontSize = heading_size
        
        # Add layout-specific styles with unique names
        style_prefix = doc_template.layout_style.capitalize()
        
        if doc_template.layout_style == 'modern':
            modern_title_name = f'{style_prefix}Title_{id(doc_template)}'
            if modern_title_name not in [style.name for style in self.styles.byName.values()]:
                self.styles.add(ParagraphStyle(
                    name=modern_title_name,
                    parent=self.styles['CourtTitle'],
                    fontSize=heading_size + 2,
                    fontName=bold_font,
                    textColor=colors.darkblue,
                    spaceAfter=25
                ))
        elif doc_template.layout_style == 'detailed':
            detailed_section_name = f'{style_prefix}Section_{id(doc_template)}'
            if detailed_section_name not in [style.name for style in self.styles.byName.values()]:
                self.styles.add(ParagraphStyle(
                    name=detailed_section_name,
                    parent=self.styles['SectionHeading'],
                    fontSize=body_size + 1,
                    fontName=bold_font,
                    spaceAfter=15,
                    borderWidth=1,
                    borderColor=colors.lightgrey,
                    borderPadding=8
                ))
    
    async def generate_document(
        self,
        document_type: str,
        company_details: CompanyDetails,
        financial_summary: FinancialSummary,
        legal_clauses: List[LegalClause] = None,
        case_details: Dict[str, Any] = None,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate any type of legal document with varied templates"""
        
        if not REPORTLAB_AVAILABLE:
            return await self._generate_text_fallback(company_details, financial_summary, output_filename)
        
        # Select random law firm and appropriate template
        law_firm = self._select_law_firm()
        doc_template = self._select_document_template(document_type)
        
        # Setup dynamic styles
        self._setup_dynamic_styles(doc_template)
        
        # Route to specific document generator
        if document_type == 'affidavit':
            return await self._generate_affidavit(law_firm, doc_template, company_details, financial_summary, legal_clauses or [], case_details or {}, output_filename)
        elif document_type == 'resolution':
            return await self._generate_resolution(law_firm, doc_template, company_details, financial_summary, output_filename)
        elif document_type == 'creditor_notice':
            return await self._generate_creditor_notice(law_firm, doc_template, company_details, financial_summary, output_filename)
        elif document_type == 'director_statement':
            return await self._generate_director_statement(law_firm, doc_template, company_details, financial_summary, output_filename)
        elif document_type == 'asset_notice':
            return await self._generate_asset_notice(law_firm, doc_template, company_details, financial_summary, output_filename)
        else:
            # Default to affidavit
            return await self._generate_affidavit(law_firm, doc_template, company_details, financial_summary, legal_clauses or [], case_details or {}, output_filename)
    
    async def _generate_affidavit(
        self,
        law_firm: LawFirm,
        doc_template: DocumentTemplate,
        company_details: CompanyDetails,
        financial_summary: FinancialSummary,
        legal_clauses: List[LegalClause],
        case_details: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate professional affidavit with varied law firm templates"""
        
        try:
            # Generate filename with law firm and template info
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_company = "".join(c for c in company_details.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                law_firm_short = law_firm.name.split()[0]
                output_filename = f"{doc_template.name.replace(' ', '_')}_{safe_company}_{law_firm_short}_{timestamp}.pdf"
            
            output_path = self.config.pdf_output_dir / output_filename
            
            # Create professional document with selected law firm and template
            doc = ProfessionalDocumentTemplate(
                str(output_path),
                law_firm=law_firm,
                doc_template=doc_template,
                pagesize=A4
            )
            
            # Build document content with template-specific styling
            story = []
            
            # Document header varies by template style
            if doc_template.layout_style == 'traditional':
                story.extend(self._create_traditional_header(doc_template, case_details))
            elif doc_template.layout_style == 'modern':
                story.extend(self._create_modern_header(doc_template, case_details))
            else:
                story.extend(self._create_formal_header(doc_template, case_details))
            
            story.append(Spacer(1, 20))
            
            # Case details and filing information
            story.extend(self._create_case_details(case_details, company_details))
            story.append(Spacer(1, 20))
            
            # Professional affidavit content with template variations
            story.extend(self._create_affidavit_content(company_details, financial_summary, legal_clauses))
            
            # Financial schedules with different layouts
            story.extend(self._create_financial_schedules(financial_summary))
            
            # Legal clauses and compliance
            story.extend(self._create_legal_clauses_section(legal_clauses))
            
            # Signature and certification
            story.extend(self._create_signature_block(company_details, law_firm))
            
            # Build the PDF
            doc.build(story)
            
            # Get file info
            file_size = output_path.stat().st_size
            estimated_pages = self._estimate_pages(story)
            
            logger.info(f"Professional PDF generated: {output_path}")
            
            return {
                'success': True,
                'output_file': str(output_path),
                'file_size': file_size,
                'pages': estimated_pages,
                'document_type': doc_template.name,
                'law_firm': law_firm.name,
                'company': company_details.name,
                'template_style': doc_template.layout_style
            }
            
        except Exception as e:
            logger.error(f"Professional PDF generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'document_type': 'affidavit',
                'company': company_details.name
            }
    
    # Keep the original method as a wrapper for backwards compatibility
    async def generate_professional_affidavit(
        self,
        company_details: CompanyDetails,
        financial_summary: FinancialSummary,
        legal_clauses: List[LegalClause],
        case_details: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate professional affidavit (backwards compatibility wrapper)"""
        return await self.generate_document(
            'affidavit', company_details, financial_summary, legal_clauses, case_details, output_filename
        )
    
    def _create_court_header(self, case_details: Dict[str, Any]) -> List[Any]:
        """Create Federal Court header matching the provided sample"""
        elements = []
        
        # Notice of Filing
        elements.append(Paragraph("NOTICE OF FILING", self.styles['CourtTitle']))
        elements.append(Spacer(1, 15))
        
        notice_text = f"""
        This document was lodged electronically in the FEDERAL COURT OF AUSTRALIA (FCA) on 
        {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} AEST and has been accepted for filing under the Court's Rules. 
        Details of filing follow and important additional information about these are set out below.
        """
        elements.append(Paragraph(notice_text, self.styles['ProfessionalBody']))
        elements.append(Spacer(1, 20))
        
        # Details of Filing table
        elements.append(Paragraph("Details of Filing", self.styles['SectionHeading']))
        
        filing_data = [
            ['Document Lodged:', case_details.get('document_type', 'Affidavit - Liquidation Proceedings')],
            ['File Number:', case_details.get('file_number', f"NSD{datetime.now().strftime('%j')}/2024")],
            ['File Title:', case_details.get('file_title', 'IN THE MATTER OF LIQUIDATION PROCEEDINGS')],
            ['Registry:', case_details.get('registry', 'FEDERAL COURT OF AUSTRALIA')]
        ]
        
        filing_table = Table(filing_data, colWidths=[2.5*inch, 4*inch])
        filing_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(filing_table)
        elements.append(Spacer(1, 30))
        
        # Registrar signature
        elements.append(Paragraph(f"Dated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} AEST", self.styles['ProfessionalBody']))
        elements.append(Paragraph("Registrar", self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_case_details(self, case_details: Dict[str, Any], company_details: CompanyDetails) -> List[Any]:
        """Create case details section"""
        elements = []
        
        # Form header
        elements.append(Paragraph("Form 59 Rule 29.02(1)", self.styles['LegalReference']))
        elements.append(Paragraph("Affidavit", self.styles['LegalHeading']))
        elements.append(Spacer(1, 15))
        
        # Case title
        case_title = f"IN THE MATTER OF {company_details.name.upper()}"
        if company_details.acn:
            case_title += f" ACN {company_details.acn}"
        
        elements.append(Paragraph(case_title, self.styles['SectionHeading']))
        elements.append(Spacer(1, 20))
        
        # Parties table
        parties_data = [
            ['Applicant:', f"{company_details.liquidator or '[LIQUIDATOR NAME]'} in capacity as Liquidator"],
            ['Company:', f"{company_details.name}"],
            ['ACN:', company_details.acn or '[TO BE COMPLETED]'],
            ['ABN:', company_details.abn or '[TO BE COMPLETED]']
        ]
        
        parties_table = Table(parties_data, colWidths=[1.5*inch, 4.5*inch])
        parties_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(parties_table)
        
        return elements
    
    def _create_affidavit_content(
        self, 
        company_details: CompanyDetails, 
        financial_summary: FinancialSummary,
        legal_clauses: List[LegalClause]
    ) -> List[Any]:
        """Create main affidavit content"""
        elements = []
        
        # Affidavit declaration
        liquidator_name = company_details.liquidator or "[LIQUIDATOR NAME]"
        liquidator_address = company_details.liquidator_address or "[LIQUIDATOR ADDRESS]"
        
        declaration = f"""
        I, {liquidator_name}, of {liquidator_address}, Registered Liquidator and Chartered Accountant, 
        solemnly and sincerely declare and affirm:
        """
        elements.append(Paragraph(declaration, self.styles['ProfessionalBody']))
        elements.append(Spacer(1, 15))
        
        # Numbered paragraphs
        paragraphs = [
            f"I am a Registered Liquidator and have practised as an accountant specialising in restructuring "
            f"distressed companies and other insolvency related matters in Australia.",
            
            f"I make this affidavit in support of the relief sought in these proceedings, namely orders under "
            f"the Corporations Act 2001 (Cth) relating to the liquidation of {company_details.name}.",
            
            f"Unless otherwise stated, I make this affidavit based on my own knowledge and belief obtained "
            f"through my role as liquidator of {company_details.name}.",
        ]
        
        for i, para in enumerate(paragraphs, 1):
            elements.append(Paragraph(f"{i}. {para}", self.styles['LegalClause']))
            elements.append(Spacer(1, 10))
        
        # Company information section
        elements.append(Paragraph("THE COMPANY", self.styles['LegalHeading']))
        
        company_info = f"""
        {company_details.name} is an Australian company that was incorporated and operated in Australia. 
        The company's registered office is located at {company_details.registered_office or '[REGISTERED OFFICE ADDRESS]'}.
        The company's principal place of business is {company_details.principal_place or '[PRINCIPAL PLACE OF BUSINESS]'}.
        """
        
        elements.append(Paragraph(f"4. {company_info}", self.styles['LegalClause']))
        
        return elements
    
    def _create_financial_schedules(self, financial_summary: FinancialSummary) -> List[Any]:
        """Create comprehensive financial schedules"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("FINANCIAL POSITION", self.styles['LegalHeading']))
        elements.append(Spacer(1, 15))
        
        # Assets schedule
        elements.append(Paragraph("Schedule of Assets", self.styles['SectionHeading']))
        
        assets_data = [
            ['Asset Category', 'Book Value ($)', 'Estimated Realizable Value ($)'],
            ['Cash at Bank', 
             self._format_currency(financial_summary.cash_at_bank), 
             self._format_currency(financial_summary.cash_at_bank)],
            ['Debtors', 
             self._format_currency(financial_summary.debtors), 
             self._format_currency(financial_summary.debtors * 0.8 if financial_summary.debtors else None)],
            ['Stock/Inventory', 
             self._format_currency(financial_summary.stock_inventory), 
             self._format_currency(financial_summary.stock_inventory * 0.6 if financial_summary.stock_inventory else None)],
            ['Plant & Equipment', 
             self._format_currency(financial_summary.plant_equipment), 
             self._format_currency(financial_summary.plant_equipment * 0.4 if financial_summary.plant_equipment else None)],
            ['Real Property', 
             self._format_currency(financial_summary.real_property), 
             self._format_currency(financial_summary.real_property * 0.9 if financial_summary.real_property else None)],
            ['TOTAL ASSETS', 
             self._format_currency(financial_summary.total_assets), 
             self._format_currency(financial_summary.total_assets * 0.75 if financial_summary.total_assets else None)]
        ]
        
        assets_table = Table(assets_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        assets_table.setStyle(self._get_financial_table_style())
        elements.append(assets_table)
        elements.append(Spacer(1, 20))
        
        # Liabilities schedule
        elements.append(Paragraph("Schedule of Liabilities", self.styles['SectionHeading']))
        
        liabilities_data = [
            ['Liability Category', 'Amount ($)', 'Priority'],
            ['Secured Creditors', self._format_currency(financial_summary.secured_creditors), 'First'],
            ['Employee Entitlements', self._format_currency(financial_summary.employee_entitlements), 'Second'],
            ['Preferential Creditors', self._format_currency(financial_summary.preferential_creditors), 'Third'],
            ['Unsecured Creditors', self._format_currency(financial_summary.unsecured_creditors), 'Fourth'],
            ['TOTAL LIABILITIES', self._format_currency(financial_summary.total_liabilities), '-']
        ]
        
        liabilities_table = Table(liabilities_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        liabilities_table.setStyle(self._get_financial_table_style())
        elements.append(liabilities_table)
        elements.append(Spacer(1, 20))
        
        # Summary
        surplus_deficiency = (financial_summary.total_assets or 0) - (financial_summary.total_liabilities or 0)
        summary_text = f"""
        Based on the above analysis, the company shows an estimated 
        {'surplus' if surplus_deficiency >= 0 else 'deficiency'} of 
        {self._format_currency(abs(surplus_deficiency))}.
        """
        elements.append(Paragraph(summary_text, self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_legal_clauses_section(self, legal_clauses: List[LegalClause]) -> List[Any]:
        """Create legal clauses section with comprehensive compliance information"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("LEGAL COMPLIANCE AND STATUTORY REQUIREMENTS", self.styles['LegalHeading']))
        elements.append(Spacer(1, 15))
        
        # Default legal clauses if none provided
        if not legal_clauses:
            legal_clauses = self._get_default_legal_clauses()
        
        for i, clause in enumerate(legal_clauses, 1):
            # Clause heading
            elements.append(Paragraph(f"{i}. {clause.title}", self.styles['SectionHeading']))
            
            # Clause reference
            if clause.reference:
                elements.append(Paragraph(f"Reference: {clause.reference}", self.styles['LegalReference']))
            
            # Clause content
            elements.append(Paragraph(clause.content, self.styles['LegalClause']))
            
            # Subsections if any
            if clause.subsections:
                for j, subsection in enumerate(clause.subsections, 1):
                    elements.append(Paragraph(f"    ({chr(96+j)}) {subsection}", self.styles['LegalClause']))
            
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_signature_block(self, company_details: CompanyDetails, law_firm: LawFirm) -> List[Any]:
        """Create professional signature block"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("CERTIFICATION AND SIGNATURES", self.styles['LegalHeading']))
        elements.append(Spacer(1, 20))
        
        # Liquidator certification
        liquidator_name = company_details.liquidator or "[LIQUIDATOR NAME]"
        certification_text = f"""
        I, {liquidator_name}, certify that:
        
        (a) This affidavit is true and complete to the best of my knowledge and belief;
        (b) All company books and records have been reviewed;
        (c) The financial information provided is based on available records;
        (d) All statutory obligations have been considered;
        (e) This affidavit complies with the Corporations Act 2001 (Cth).
        """
        
        elements.append(Paragraph(certification_text, self.styles['ProfessionalBody']))
        elements.append(Spacer(1, 30))
        
        # Signature table
        signature_data = [
            ['Affirmed by:', '________________________________'],
            ['', liquidator_name],
            ['', 'Registered Liquidator'],
            ['', f"Registration No: {company_details.liquidator_registration or '[REGISTRATION NUMBER]'}"],
            ['', ''],
            ['Date:', datetime.now().strftime('%d %B %Y')],
            ['', ''],
            ['Witness:', '________________________________'],
            ['', '[WITNESS NAME]'],
            ['Date:', '____________________']
        ]
        
        signature_table = Table(signature_data, colWidths=[1.5*inch, 4*inch])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(signature_table)
        
        return elements
    
    def _create_traditional_header(self, doc_template: DocumentTemplate, case_details: Dict[str, Any]) -> List[Any]:
        """Create traditional document header"""
        elements = []
        
        title_style = 'CourtTitle' if 'CourtTitle' in self.styles else 'Title'
        elements.append(Paragraph(f"<b>{doc_template.name.upper()}</b>", self.styles[title_style]))
        elements.append(Spacer(1, 15))
        
        if case_details:
            elements.append(Paragraph(f"Matter No: {case_details.get('matter_no', 'TBD')}", self.styles['ProfessionalBody']))
            elements.append(Paragraph(f"Registry: {case_details.get('registry', 'Commercial')}", self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_modern_header(self, doc_template: DocumentTemplate, case_details: Dict[str, Any]) -> List[Any]:
        """Create modern document header"""
        elements = []
        
        if 'ModernTitle' in self.styles:
            elements.append(Paragraph(f"<b>{doc_template.name}</b>", self.styles['ModernTitle']))
        else:
            elements.append(Paragraph(f"<b>{doc_template.name}</b>", self.styles['Title']))
        
        elements.append(Spacer(1, 20))
        
        if case_details:
            case_info = f"Case Reference: {case_details.get('matter_no', 'Pending')} | " \
                       f"Date Filed: {case_details.get('date_filed', datetime.now().strftime('%d/%m/%Y'))}"
            elements.append(Paragraph(case_info, self.styles['ProfessionalBody']))
        
        return elements
    
    def _create_formal_header(self, doc_template: DocumentTemplate, case_details: Dict[str, Any]) -> List[Any]:
        """Create formal document header"""
        elements = []
        
        elements.append(Paragraph(f"<b>{doc_template.name}</b>", self.styles['LegalHeading']))
        elements.append(Spacer(1, 10))
        
        if case_details:
            elements.append(Paragraph(f"<b>Matter:</b> {case_details.get('matter_no', 'To be assigned')}", self.styles['ProfessionalBody']))
            elements.append(Paragraph(f"<b>Court:</b> {case_details.get('court', 'Federal Court of Australia')}", self.styles['ProfessionalBody']))
        
        return elements
    
    async def _generate_resolution(
        self,
        law_firm: LawFirm,
        doc_template: DocumentTemplate,
        company_details: CompanyDetails,
        financial_summary: FinancialSummary,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate liquidation resolution document"""
        
        try:
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_company = "".join(c for c in company_details.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                law_firm_short = law_firm.name.split()[0]
                output_filename = f"Resolution_{safe_company}_{law_firm_short}_{timestamp}.pdf"
            
            output_path = self.config.pdf_output_dir / output_filename
            
            doc = ProfessionalDocumentTemplate(
                str(output_path),
                law_firm=law_firm,
                doc_template=doc_template,
                pagesize=A4
            )
            
            story = []
            
            # Header
            story.extend(self._create_formal_header(doc_template, {}))
            story.append(Spacer(1, 30))
            
            # Resolution content
            story.append(Paragraph(f"<b>RESOLUTION OF {company_details.name.upper()}</b>", self.styles['SectionHeading']))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph(f"<b>Company:</b> {company_details.name}", self.styles['ProfessionalBody']))
            story.append(Paragraph(f"<b>ACN:</b> {company_details.acn or 'Not provided'}", self.styles['ProfessionalBody']))
            story.append(Paragraph(f"<b>ABN:</b> {company_details.abn or 'Not provided'}", self.styles['ProfessionalBody']))
            story.append(Spacer(1, 20))
            
            # Resolution clauses
            resolution_text = f"""
            <b>SPECIAL RESOLUTION</b><br/><br/>
            
            RESOLVED THAT:<br/><br/>
            
            1. The company be wound up voluntarily pursuant to section 491 of the Corporations Act 2001.<br/><br/>
            
            2. {company_details.liquidator or 'A qualified liquidator'} be appointed as liquidator of the company.<br/><br/>
            
            3. The liquidator is authorized to exercise all powers conferred by the Corporations Act 2001 
            and to take all necessary steps for the winding up of the company's affairs.<br/><br/>
            
            4. The liquidator's remuneration be fixed on a time cost basis in accordance with the 
            schedule of hourly rates as disclosed to creditors.<br/><br/>
            
            Passed on: {datetime.now().strftime('%d %B %Y')}
            """
            
            story.append(Paragraph(resolution_text, self.styles['ProfessionalBody']))
            story.append(Spacer(1, 30))
            
            # Signature section
            story.extend(self._create_signature_block(company_details, law_firm))
            
            doc.build(story)
            
            file_size = output_path.stat().st_size
            logger.info(f"Resolution generated: {output_path}")
            
            return {
                'success': True,
                'output_file': str(output_path),
                'file_size': file_size,
                'document_type': doc_template.name,
                'law_firm': law_firm.name,
                'company': company_details.name
            }
            
        except Exception as e:
            logger.error(f"Resolution generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _generate_creditor_notice(
        self,
        law_firm: LawFirm,
        doc_template: DocumentTemplate,
        company_details: CompanyDetails,
        financial_summary: FinancialSummary,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate creditor notification document"""
        
        try:
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_company = "".join(c for c in company_details.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                law_firm_short = law_firm.name.split()[0]
                output_filename = f"Creditor_Notice_{safe_company}_{law_firm_short}_{timestamp}.pdf"
            
            output_path = self.config.pdf_output_dir / output_filename
            
            doc = ProfessionalDocumentTemplate(
                str(output_path),
                law_firm=law_firm,
                doc_template=doc_template,
                pagesize=A4
            )
            
            story = []
            
            # Header
            story.extend(self._create_modern_header(doc_template, {}))
            story.append(Spacer(1, 30))
            
            # Notice content
            story.append(Paragraph("<b>NOTICE TO CREDITORS</b>", self.styles['SectionHeading']))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph(f"<b>Re:</b> {company_details.name} (In Liquidation)", self.styles['ProfessionalBody']))
            story.append(Paragraph(f"<b>ACN:</b> {company_details.acn or 'Not provided'}", self.styles['ProfessionalBody']))
            story.append(Spacer(1, 20))
            
            # Notice body
            notice_text = f"""
            <b>NOTICE OF LIQUIDATION</b><br/><br/>
            
            TAKE NOTICE that {company_details.name} was placed into liquidation on {datetime.now().strftime('%d %B %Y')}.<br/><br/>
            
            {company_details.liquidator or 'The appointed liquidator'} has been appointed as liquidator of the company.<br/><br/>
            
            <b>CREDITORS ARE REQUIRED TO:</b><br/>
            1. Lodge formal proof of debt within 30 days<br/>
            2. Provide supporting documentation<br/>
            3. Include details of any security held<br/><br/>
            
            <b>ESTIMATED FINANCIAL POSITION:</b><br/>
            Assets: {self._format_currency(financial_summary.total_assets)}<br/>
            Liabilities: {self._format_currency(financial_summary.total_liabilities)}<br/>
            Estimated deficiency: {self._format_currency(abs(financial_summary.estimated_surplus_deficiency or 0))}<br/><br/>
            
            All inquiries should be directed to the liquidator's office.
            """
            
            story.append(Paragraph(notice_text, self.styles['ProfessionalBody']))
            story.append(Spacer(1, 30))
            
            # Contact information
            story.extend(self._create_signature_block(company_details, law_firm))
            
            doc.build(story)
            
            file_size = output_path.stat().st_size
            logger.info(f"Creditor notice generated: {output_path}")
            
            return {
                'success': True,
                'output_file': str(output_path),
                'file_size': file_size,
                'document_type': doc_template.name,
                'law_firm': law_firm.name,
                'company': company_details.name
            }
            
        except Exception as e:
            logger.error(f"Creditor notice generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _generate_director_statement(
        self,
        law_firm: LawFirm,
        doc_template: DocumentTemplate,
        company_details: CompanyDetails,
        financial_summary: FinancialSummary,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate director's statement document"""
        
        try:
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_company = "".join(c for c in company_details.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                law_firm_short = law_firm.name.split()[0]
                output_filename = f"Director_Statement_{safe_company}_{law_firm_short}_{timestamp}.pdf"
            
            output_path = self.config.pdf_output_dir / output_filename
            
            doc = ProfessionalDocumentTemplate(
                str(output_path),
                law_firm=law_firm,
                doc_template=doc_template,
                pagesize=A4
            )
            
            story = []
            
            # Header
            story.extend(self._create_traditional_header(doc_template, {}))
            story.append(Spacer(1, 30))
            
            # Statement content
            story.append(Paragraph("<b>DIRECTOR'S STATEMENT AS TO AFFAIRS</b>", self.styles['SectionHeading']))
            story.append(Spacer(1, 15))
            
            # Director information
            if company_details.directors:
                story.append(Paragraph(f"<b>Directors:</b> {', '.join(company_details.directors)}", self.styles['ProfessionalBody']))
            story.append(Paragraph(f"<b>Company:</b> {company_details.name}", self.styles['ProfessionalBody']))
            story.append(Spacer(1, 20))
            
            # Financial statement
            story.extend(self._create_financial_schedules(financial_summary))
            
            # Declaration
            declaration_text = f"""
            <b>DECLARATION</b><br/><br/>
            
            I/We, the director(s) of {company_details.name}, do solemnly and sincerely declare that:<br/><br/>
            
            1. The company is unable to pay its debts as and when they fall due.<br/>
            2. The attached statement of affairs is correct to the best of my/our knowledge.<br/>
            3. All assets and liabilities have been disclosed.<br/>
            4. The company should be wound up.<br/><br/>
            
            Date: {datetime.now().strftime('%d %B %Y')}
            """
            
            story.append(Paragraph(declaration_text, self.styles['ProfessionalBody']))
            story.append(Spacer(1, 30))
            
            story.extend(self._create_signature_block(company_details, law_firm))
            
            doc.build(story)
            
            file_size = output_path.stat().st_size
            logger.info(f"Director statement generated: {output_path}")
            
            return {
                'success': True,
                'output_file': str(output_path),
                'file_size': file_size,
                'document_type': doc_template.name,
                'law_firm': law_firm.name,
                'company': company_details.name
            }
            
        except Exception as e:
            logger.error(f"Director statement generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _generate_asset_notice(
        self,
        law_firm: LawFirm,
        doc_template: DocumentTemplate,
        company_details: CompanyDetails,
        financial_summary: FinancialSummary,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate asset realization notice document"""
        
        try:
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_company = "".join(c for c in company_details.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                law_firm_short = law_firm.name.split()[0]
                output_filename = f"Asset_Notice_{safe_company}_{law_firm_short}_{timestamp}.pdf"
            
            output_path = self.config.pdf_output_dir / output_filename
            
            doc = ProfessionalDocumentTemplate(
                str(output_path),
                law_firm=law_firm,
                doc_template=doc_template,
                pagesize=A4
            )
            
            story = []
            
            # Header
            story.extend(self._create_formal_header(doc_template, {}))
            story.append(Spacer(1, 30))
            
            # Notice content
            story.append(Paragraph("<b>NOTICE OF ASSET REALIZATION</b>", self.styles['SectionHeading']))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph(f"<b>Company:</b> {company_details.name} (In Liquidation)", self.styles['ProfessionalBody']))
            story.append(Spacer(1, 20))
            
            # Asset details
            asset_data = [
                ['Asset Category', 'Book Value', 'Estimated Realization'],
                ['Cash at Bank', self._format_currency(financial_summary.cash_at_bank), self._format_currency(financial_summary.cash_at_bank)],
                ['Debtors', self._format_currency(financial_summary.debtors), self._format_currency((financial_summary.debtors or 0) * 0.8)],
                ['Stock/Inventory', self._format_currency(financial_summary.stock_inventory), self._format_currency((financial_summary.stock_inventory or 0) * 0.6)],
                ['Plant & Equipment', self._format_currency(financial_summary.plant_equipment), self._format_currency((financial_summary.plant_equipment or 0) * 0.4)],
                ['Real Property', self._format_currency(financial_summary.real_property), self._format_currency((financial_summary.real_property or 0) * 0.9)]
            ]
            
            asset_table = Table(asset_data)
            asset_table.setStyle(self._get_financial_table_style())
            story.append(asset_table)
            story.append(Spacer(1, 20))
            
            # Realization notice
            notice_text = f"""
            <b>ASSET DISPOSAL NOTICE</b><br/><br/>
            
            Notice is hereby given that the liquidator intends to realize the above assets 
            for the benefit of creditors.<br/><br/>
            
            Interested parties may submit expressions of interest within 14 days.<br/><br/>
            
            All inquiries to: {law_firm.email}
            """
            
            story.append(Paragraph(notice_text, self.styles['ProfessionalBody']))
            story.append(Spacer(1, 30))
            
            story.extend(self._create_signature_block(company_details, law_firm))
            
            doc.build(story)
            
            file_size = output_path.stat().st_size
            logger.info(f"Asset notice generated: {output_path}")
            
            return {
                'success': True,
                'output_file': str(output_path),
                'file_size': file_size,
                'document_type': doc_template.name,
                'law_firm': law_firm.name,
                'company': company_details.name
            }
            
        except Exception as e:
            logger.error(f"Asset notice generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_financial_table_style(self) -> TableStyle:
        """Get professional financial table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ])
    
    def _format_currency(self, amount: Optional[float]) -> str:
        """Format currency values professionally"""
        if amount is None:
            return "[TO BE DETERMINED]"
        return f"${amount:,.2f}"
    
    def _get_default_legal_clauses(self) -> List[LegalClause]:
        """Get default legal clauses for liquidation proceedings"""
        return [
            LegalClause(
                reference="Section 491 Corporations Act 2001 (Cth)",
                title="Voluntary Winding Up",
                content="The company resolved to wind up voluntarily pursuant to Section 491 of the Corporations Act 2001 (Cth).",
                subsections=[
                    "The resolution was passed by special resolution of members",
                    "The company was solvent at the time of resolution",
                    "All statutory requirements have been satisfied"
                ]
            ),
            LegalClause(
                reference="Section 497 Corporations Act 2001 (Cth)",
                title="Creditor Notification Requirements",
                content="All creditors have been notified in accordance with statutory requirements.",
                subsections=[
                    "Notice published in prescribed manner",
                    "Individual notices sent to known creditors",
                    "ASIC notifications completed"
                ]
            ),
            LegalClause(
                reference="Section 499 Corporations Act 2001 (Cth)",
                title="Liquidator Appointment",
                content="The liquidator was properly appointed and has accepted the appointment.",
                subsections=[
                    "Liquidator is registered and qualified",
                    "Appropriate consent to act provided",
                    "No conflicts of interest exist"
                ]
            )
        ]
    
    def _estimate_pages(self, story: List[Any]) -> int:
        """Estimate number of pages in the document"""
        return max(5, len(story) // 15)  # Rough estimation
    
    async def _generate_text_fallback(
        self, 
        company_details: CompanyDetails, 
        financial_summary: FinancialSummary,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fallback to text if PDF generation unavailable"""
        try:
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_company = "".join(c for c in company_details.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_filename = f"Affidavit_{safe_company}_{timestamp}.txt"
            
            output_path = self.config.pdf_output_dir / output_filename
            
            # Create detailed text document
            content = f"""
FEDERAL COURT OF AUSTRALIA
COMMERCIAL AND CORPORATIONS LIST

AFFIDAVIT - LIQUIDATION PROCEEDINGS

Company: {company_details.name}
ACN: {company_details.acn or 'N/A'}
ABN: {company_details.abn or 'N/A'}
Date: {datetime.now().strftime('%d %B %Y')}

FINANCIAL SUMMARY:
- Total Assets: {self._format_currency(financial_summary.total_assets)}
- Total Liabilities: {self._format_currency(financial_summary.total_liabilities)}
- Estimated Result: {self._format_currency((financial_summary.total_assets or 0) - (financial_summary.total_liabilities or 0))}

LIQUIDATOR CERTIFICATION:
Liquidator: {company_details.liquidator or '[TO BE COMPLETED]'}
Registration: {company_details.liquidator_registration or '[TO BE COMPLETED]'}

This document was generated by the AI Agent System on {datetime.now().strftime('%d %B %Y')}.
Note: ReportLab unavailable - document saved as text file.
            """.strip()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = output_path.stat().st_size
            
            return {
                'success': True,
                'file_path': str(output_path),
                'file_size': file_size,
                'document_type': 'Text Affidavit (Fallback)',
                'company': company_details.name,
                'pages': 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'company': company_details.name
            } 