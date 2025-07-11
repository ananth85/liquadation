"""
PDF Generation System for AI Agent
Creates professional PDF documents with templates and styling
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import tempfile
import os

# PDF generation libraries
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Metadata for generated documents"""
    title: str
    document_type: str
    organization: str
    created_date: datetime
    author: str
    version: str = "1.0"


@dataclass
class PDFGenerationResult:
    """Result of PDF generation"""
    success: bool
    file_path: Optional[Path] = None
    file_size: Optional[int] = None
    pages: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None


class DocumentTemplate:
    """Base class for document templates"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        if not REPORTLAB_AVAILABLE:
            return
            
        # Legal document heading style
        self.styles.add(ParagraphStyle(
            name='LegalHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        ))
        
        # Legal body text style
        self.styles.add(ParagraphStyle(
            name='LegalBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20,
            alignment=4  # Justify
        ))
        
        # Legal clause style
        self.styles.add(ParagraphStyle(
            name='LegalClause',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leftIndent=30,
            bulletIndent=20
        ))
        
        # Signature style
        self.styles.add(ParagraphStyle(
            name='Signature',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=40,
            leftIndent=300
        ))
    
    def generate_content(self, content: str, metadata: DocumentMetadata) -> List[Any]:
        """Generate PDF content elements - to be overridden by subclasses"""
        if not REPORTLAB_AVAILABLE:
            raise Exception("ReportLab not available for PDF generation")
        
        story = []
        
        # Header
        story.append(Paragraph(metadata.title, self.styles['LegalHeading']))
        story.append(Spacer(1, 20))
        
        # Metadata table
        org_data = [
            ['Organization:', metadata.organization],
            ['Date:', metadata.created_date.strftime('%d %B %Y')],
            ['Document Type:', metadata.document_type],
            ['Version:', metadata.version]
        ]
        
        org_table = Table(org_data, colWidths=[2*inch, 4*inch])
        org_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(org_table)
        story.append(Spacer(1, 30))
        
        # Content
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                if para.strip().startswith('#'):
                    # Heading
                    story.append(Paragraph(para.strip('#').strip(), self.styles['Heading2']))
                elif para.strip().startswith('-') or para.strip().startswith('•'):
                    # Bullet point
                    story.append(Paragraph(para.strip(), self.styles['LegalClause']))
                else:
                    # Normal paragraph
                    story.append(Paragraph(para.strip(), self.styles['LegalBody']))
                story.append(Spacer(1, 12))
        
        return story


class LiquidationDocumentTemplate(DocumentTemplate):
    """Template for Australian liquidation documents"""
    
    def __init__(self):
        super().__init__("liquidation_document")
    
    def generate_content(self, content: str, metadata: DocumentMetadata) -> List[Any]:
        """Generate liquidation document with Australian legal formatting"""
        if not REPORTLAB_AVAILABLE:
            raise Exception("ReportLab not available for PDF generation")
        
        story = []
        
        # Letterhead
        story.append(Paragraph("AUSTRALIAN LIQUIDATION DOCUMENT", self.styles['LegalHeading']))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Pursuant to the Corporations Act 2001 (Cth)", self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Document details
        details_data = [
            ['Document Type:', metadata.document_type],
            ['Company/Organization:', metadata.organization],
            ['Date of Issue:', metadata.created_date.strftime('%d %B %Y')],
            ['Prepared by:', metadata.author],
            ['ACN/ABN:', '[TO BE COMPLETED]']
        ]
        
        details_table = Table(details_data, colWidths=[2.5*inch, 3.5*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 30))
        
        # Legal content
        story.append(Paragraph("NOTICE", self.styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Process content with legal formatting
        sections = content.split('\n\n')
        for section in sections:
            if section.strip():
                if any(keyword in section.lower() for keyword in ['whereas', 'hereby', 'resolved', 'notice']):
                    # Legal clause formatting
                    story.append(Paragraph(section.strip(), self.styles['LegalClause']))
                else:
                    # Standard legal body text
                    story.append(Paragraph(section.strip(), self.styles['LegalBody']))
                story.append(Spacer(1, 15))
        
        # Signature block
        story.append(Spacer(1, 40))
        story.append(Paragraph("Signatures:", self.styles['Heading3']))
        story.append(Spacer(1, 20))
        
        signature_data = [
            ['Director/Liquidator:', '_' * 40, 'Date:', '_' * 20],
            ['Print Name:', '_' * 40, '', ''],
            ['', '', '', ''],
            ['Witness:', '_' * 40, 'Date:', '_' * 20],
            ['Print Name:', '_' * 40, '', '']
        ]
        
        signature_table = Table(signature_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1.5*inch])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        story.append(signature_table)
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("This document has been prepared in accordance with Australian liquidation laws and regulations.", 
                              self.styles['Normal']))
        
        return story


class PDFGenerator:
    """Main PDF generation service"""
    
    def __init__(self, config):
        self.config = config
        self.templates = {
            'liquidation': LiquidationDocumentTemplate(),
            'general': DocumentTemplate('general'),
            'legal': DocumentTemplate('legal')
        }
        
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not installed. PDF generation will be limited.")
    
    async def generate_pdf(
        self,
        content: str,
        metadata: DocumentMetadata,
        template_type: str = 'general',
        output_filename: Optional[str] = None
    ) -> PDFGenerationResult:
        """
        Generate PDF document from content
        
        Args:
            content: Document content as text
            metadata: Document metadata
            template_type: Template to use (liquidation, general, legal)
            output_filename: Optional custom filename
            
        Returns:
            PDFGenerationResult with file path and metadata
        """
        if not REPORTLAB_AVAILABLE:
            return await self._generate_text_fallback(content, metadata, output_filename)
        
        try:
            # Get template
            template = self.templates.get(template_type, self.templates['general'])
            
            # Generate filename
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_org = "".join(c for c in metadata.organization if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_filename = f"{safe_org}_{metadata.document_type}_{timestamp}.pdf"
            
            output_path = self.config.pdf_output_dir / output_filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                topMargin=1*inch,
                bottomMargin=1*inch,
                leftMargin=1*inch,
                rightMargin=1*inch
            )
            
            # Generate content
            story = template.generate_content(content, metadata)
            
            # Build PDF
            doc.build(story)
            
            # Get file info
            file_size = output_path.stat().st_size
            
            logger.info(f"PDF generated successfully: {output_path}")
            
            return PDFGenerationResult(
                success=True,
                file_path=output_path,
                file_size=file_size,
                pages=1,  # Simplified for now
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return PDFGenerationResult(
                success=False,
                error=str(e),
                metadata=metadata
            )
    
    async def _generate_text_fallback(
        self,
        content: str,
        metadata: DocumentMetadata,
        output_filename: Optional[str] = None
    ) -> PDFGenerationResult:
        """Fallback to text file if PDF generation unavailable"""
        try:
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_org = "".join(c for c in metadata.organization if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_filename = f"{safe_org}_{metadata.document_type}_{timestamp}.txt"
            
            output_path = self.config.pdf_output_dir / output_filename
            
            # Create formatted text document
            formatted_content = f"""
{metadata.title}
{'=' * len(metadata.title)}

Organization: {metadata.organization}
Document Type: {metadata.document_type}
Date: {metadata.created_date.strftime('%d %B %Y')}
Author: {metadata.author}
Version: {metadata.version}

{'-' * 80}

{content}

{'-' * 80}

This document was generated by {metadata.author} on {metadata.created_date.strftime('%d %B %Y')}.
Note: PDF generation unavailable - document saved as text file.
            """.strip()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            file_size = output_path.stat().st_size
            
            logger.info(f"Text document generated as fallback: {output_path}")
            
            return PDFGenerationResult(
                success=True,
                file_path=output_path,
                file_size=file_size,
                pages=1,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Text fallback generation failed: {e}")
            return PDFGenerationResult(
                success=False,
                error=str(e),
                metadata=metadata
            )
    
    async def generate_multiple_pdfs(
        self,
        documents: List[Dict[str, Any]],
        template_type: str = 'liquidation'
    ) -> List[PDFGenerationResult]:
        """Generate multiple PDFs concurrently"""
        tasks = []
        
        for i, doc_data in enumerate(documents):
            content = doc_data.get('content', '')
            org_name = doc_data.get('organization', f'Organization_{i+1}')
            doc_type = doc_data.get('document_type', 'Legal Document')
            
            metadata = DocumentMetadata(
                title=f"{doc_type} - {org_name}",
                document_type=doc_type,
                organization=org_name,
                created_date=datetime.now(),
                author=self.config.agent_name,
                version="1.0"
            )
            
            task = asyncio.create_task(
                self.generate_pdf(content, metadata, template_type)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"PDF generation {i+1} failed: {result}")
                processed_results.append(PDFGenerationResult(
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results 