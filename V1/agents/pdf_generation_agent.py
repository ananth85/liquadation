import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentTask
import logging
from pathlib import Path
import os
from datetime import datetime

# PDF generation library
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class PDFGenerationAgent(BaseAgent):
    """Agent responsible for generating PDF documents from rendered templates using ReportLab"""
    
    def __init__(self, output_dir: str = "output_pdfs", logger: Optional[logging.Logger] = None):
        super().__init__("PDFGenerationAgent", logger)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Check ReportLab availability
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available. Install reportlab for PDF generation.")
        else:
            self.logger.info("PDF engine ready: ReportLab")
        
        # Default styles and settings
        self.default_styles = self._setup_default_styles()
    
    def get_capabilities(self) -> List[str]:
        return [
            "generate_pdf",
            "generate_pdf_from_html",
            "generate_pdf_from_text", 
            "add_letterhead",
            "batch_generate_pdfs",
            "merge_pdfs"
        ]

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process PDF generation tasks"""
        task_type = task.task_type
        input_data = task.input_data
        
        if task_type == "generate_pdf":
            return await self.generate_pdf(
                input_data.get("content"),
                input_data.get("filename"),
                input_data.get("document_type"),
                input_data.get("company_data")
            )
        elif task_type == "generate_pdf_from_html":
            return await self.generate_pdf_from_html(
                input_data.get("html_content"),
                input_data.get("filename")
            )
        elif task_type == "generate_pdf_from_text":
            return await self.generate_pdf_from_text(
                input_data.get("text_content"),
                input_data.get("filename"),
                input_data.get("company_data")
            )
        elif task_type == "batch_generate_pdfs":
            return await self.batch_generate_pdfs(input_data.get("documents"))
        elif task_type == "add_letterhead":
            return await self.add_letterhead(
                input_data.get("pdf_path"),
                input_data.get("company_data")
            )
        elif task_type == "merge_pdfs":
            return await self.merge_pdfs(input_data.get("pdf_paths"))
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def generate_pdf(self, content: str, filename: str, 
                          document_type: str = "document", 
                          company_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate PDF from content using ReportLab"""
        if not content:
            raise ValueError("Content is required")
        
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("ReportLab not available. Install reportlab for PDF generation.")
        
        if not filename:
            # Generate filename from company data and timestamp
            company_name = (company_data or {}).get('company_name', 'document')
            safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_name}_{document_type}_{timestamp}.pdf"
        
        # Ensure .pdf extension
        if not filename.endswith('.pdf'):
            filename = f"{filename}.pdf"
        
        output_path = self.output_dir / filename
        
        # Check if content is HTML and convert to text if needed
        if self._is_html_content(content):
            content = self._convert_html_to_text(content)
        
        # Generate PDF with ReportLab
        try:
            result = await self._generate_with_reportlab(content, output_path, company_data)
            return result
        except Exception as e:
            raise RuntimeError(f"PDF generation failed: {e}")
    
    def _is_html_content(self, content: str) -> bool:
        """Check if content is HTML"""
        content_lower = content.strip().lower()
        return (content_lower.startswith('<!doctype html>') or 
                content_lower.startswith('<html>') or 
                '<html>' in content_lower or
                '</html>' in content_lower)

    def _convert_html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text for ReportLab"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Add line breaks for block elements to preserve structure
            for br in soup.find_all("br"):
                br.replace_with("\n")
            
            for element in soup.find_all(['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                element.append('\n')
            
            # Add extra spacing for headers and major sections
            for header in soup.find_all(['h1', 'h2', 'h3']):
                header.append('\n')
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up excessive whitespace while preserving line breaks
            lines = []
            for line in text.splitlines():
                line = line.strip()
                if line:  # Only add non-empty lines
                    lines.append(line)
                elif lines and lines[-1]:  # Add single empty line for spacing
                    lines.append('')
            
            return '\n'.join(lines)
            
        except ImportError:
            # Fallback: simple HTML tag removal with better formatting
            import re
            
            # Remove CSS style blocks
            text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Convert common HTML elements to text with line breaks
            text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
            text = re.sub(r'</(div|p|h[1-6]|li)>', '\n', text, flags=re.IGNORECASE)
            text = re.sub(r'<h[1-6][^>]*>', '\n\n', text, flags=re.IGNORECASE)
            
            # Remove remaining HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            
            # Clean up whitespace while preserving some structure
            lines = []
            for line in text.splitlines():
                line = line.strip()
                if line:
                    lines.append(line)
                elif lines and lines[-1]:
                    lines.append('')
            
            return '\n'.join(lines)

    async def _generate_with_reportlab(self, content: str, output_path: Path,
                                      company_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate PDF using ReportLab"""
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("ReportLab not available")
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Add letterhead if company data provided
            if company_data:
                story.extend(self._create_letterhead(company_data))
                story.append(Spacer(1, 0.2*inch))
            
            # Add main content
            story.extend(self._format_content_for_reportlab(content))
            
            # Build PDF
            doc.build(story)
            
            file_size = output_path.stat().st_size
            
            self.logger.info(f"Generated PDF with ReportLab: {output_path}")
            
            return {
                "success": True,
                "engine": "reportlab",
                "output_path": str(output_path),
                "filename": output_path.name,
                "file_size": file_size
            }
            
        except Exception as e:
            raise RuntimeError(f"ReportLab generation failed: {e}")

    def _setup_default_styles(self) -> Dict[str, Any]:
        """Setup default styles for PDF generation"""
        if not REPORTLAB_AVAILABLE:
            return {}
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        custom_styles = {
            'CompanyName': ParagraphStyle(
                'CompanyName',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=6,
                alignment=1,  # Center alignment
                textColor=colors.black
            ),
            'CompanyDetails': ParagraphStyle(
                'CompanyDetails',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                alignment=1,  # Center alignment
                textColor=colors.grey
            ),
            'DocumentTitle': ParagraphStyle(
                'DocumentTitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12,
                alignment=0,  # Left alignment
                textColor=colors.black
            ),
            'BodyText': ParagraphStyle(
                'BodyText',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                leftIndent=0,
                rightIndent=0
            ),
            'SignatureLine': ParagraphStyle(
                'SignatureLine',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=3,
                spaceBefore=20
            )
        }
        
        return custom_styles
    
    def _create_letterhead(self, company_data: Dict[str, Any]) -> List[Any]:
        """Create letterhead for ReportLab PDFs"""
        if not REPORTLAB_AVAILABLE:
            return []
        
        letterhead = []
        
        # Company name
        company_name = company_data.get('company_name', 'Company Name')
        letterhead.append(Paragraph(company_name, self.default_styles['CompanyName']))
        
        # Company details
        abn = company_data.get('formatted_abn', company_data.get('abn', ''))
        acn = company_data.get('formatted_acn', company_data.get('acn', ''))
        details = f"ABN: {abn} | ACN: {acn}"
        letterhead.append(Paragraph(details, self.default_styles['CompanyDetails']))
        
        return letterhead
    
    def _format_content_for_reportlab(self, content: str) -> List[Any]:
        """Format text content for ReportLab"""
        if not REPORTLAB_AVAILABLE:
            return []
        
        story = []
        lines = content.split('\n')
        
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                # Empty line - end current paragraph
                if current_paragraph:
                    para_text = '\n'.join(current_paragraph)
                    story.append(Paragraph(para_text, self.default_styles['BodyText']))
                    current_paragraph = []
                story.append(Spacer(1, 6))
            
            elif line.startswith('_____'):
                # Signature line
                if current_paragraph:
                    para_text = '\n'.join(current_paragraph)
                    story.append(Paragraph(para_text, self.default_styles['BodyText']))
                    current_paragraph = []
                story.append(Paragraph("_" * 30, self.default_styles['SignatureLine']))
            
            elif line.isupper() and len(line) > 5:
                # Likely a title/header
                if current_paragraph:
                    para_text = '\n'.join(current_paragraph)
                    story.append(Paragraph(para_text, self.default_styles['BodyText']))
                    current_paragraph = []
                story.append(Paragraph(line, self.default_styles['DocumentTitle']))
            
            else:
                # Regular content
                current_paragraph.append(line)
        
        # Add remaining paragraph
        if current_paragraph:
            para_text = '\n'.join(current_paragraph)
            story.append(Paragraph(para_text, self.default_styles['BodyText']))
        
        return story

    async def generate_pdf_from_html(self, html_content: str, filename: str) -> Dict[str, Any]:
        """Generate PDF from HTML content by converting to text and using ReportLab"""
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("PDF generation requires ReportLab")
        
        if not filename.endswith('.pdf'):
            filename = f"{filename}.pdf"
        
        # Convert HTML to text
        text_content = self._convert_html_to_text(html_content)
        
        # Generate PDF using the standard method
        return await self.generate_pdf(text_content, filename)

    async def generate_pdf_from_text(self, text_content: str, filename: str,
                                    company_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate PDF from plain text content"""
        return await self.generate_pdf(text_content, filename, "text", company_data)

    async def batch_generate_pdfs(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate multiple PDFs in batch"""
        if not documents:
            raise ValueError("No documents provided for batch generation")
        
        results = []
        successful = 0
        failed = 0
        
        for doc in documents:
            try:
                result = await self.generate_pdf(
                    content=doc.get('content', ''),
                    filename=doc.get('filename', ''),
                    document_type=doc.get('document_type', 'document'),
                    company_data=doc.get('company_data')
                )
                results.append(result)
                successful += 1
                
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "filename": doc.get('filename', 'unknown')
                })
                failed += 1
                self.logger.error(f"Failed to generate PDF for {doc.get('filename', 'unknown')}: {e}")
        
        return {
            "success": True,
            "batch_results": results,
            "successful": successful,
            "failed": failed,
            "total": len(documents)
        }

    async def add_letterhead(self, pdf_path: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add letterhead to existing PDF (requires PyPDF2)"""
        # This would require PyPDF2 for PDF manipulation
        # For now, return not implemented
        return {
            "success": False,
            "error": "Letterhead addition to existing PDFs not implemented yet"
        }

    async def merge_pdfs(self, pdf_paths: List[str]) -> Dict[str, Any]:
        """Merge multiple PDFs into one"""
        # This would require PyPDF2 for PDF merging
        # For now, return not implemented
        return {
            "success": False,
            "error": "PDF merging not implemented yet"
        }

    def get_available_engines(self) -> List[str]:
        """Get list of available PDF generation engines"""
        return ["reportlab"] if REPORTLAB_AVAILABLE else []

    def cleanup_old_files(self, days_old: int = 7) -> Dict[str, Any]:
        """Clean up old PDF files"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_files = []
        deleted_count = 0
        
        try:
            for pdf_file in self.output_dir.glob("*.pdf"):
                file_mtime = datetime.fromtimestamp(pdf_file.stat().st_mtime)
                if file_mtime < cutoff_date:
                    pdf_file.unlink()
                    deleted_files.append(str(pdf_file))
                    deleted_count += 1
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "deleted_files": deleted_files
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 