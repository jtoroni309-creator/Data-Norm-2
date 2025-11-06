"""PDF generation service using ReportLab and WeasyPrint"""
import io
import logging
import hashlib
from typing import Optional, Tuple
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
from weasyprint import HTML, CSS
from jinja2 import Template

from .config import settings
from .schemas import PDFGenerationOptions

logger = logging.getLogger(__name__)


class PDFGenerationService:
    """Service for generating PDFs from HTML templates"""

    def __init__(self):
        self.page_sizes = {
            "LETTER": letter,
            "A4": A4,
            "LEGAL": legal
        }

    def _get_page_size(self, size_name: str) -> Tuple[float, float]:
        """Get page size dimensions"""
        return self.page_sizes.get(size_name.upper(), letter)

    def generate_from_html(
        self,
        html_content: str,
        css_content: Optional[str] = None,
        options: Optional[PDFGenerationOptions] = None,
        header_html: Optional[str] = None,
        footer_html: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from HTML content using WeasyPrint

        Args:
            html_content: HTML content to convert
            css_content: Optional CSS styles
            options: PDF generation options
            header_html: Optional HTML for header
            footer_html: Optional HTML for footer

        Returns:
            PDF content as bytes
        """
        if options is None:
            options = PDFGenerationOptions()

        logger.info("Generating PDF from HTML")

        # Prepare full HTML with styles
        full_html = self._prepare_html(
            html_content,
            css_content,
            options,
            header_html,
            footer_html
        )

        # Generate PDF with WeasyPrint
        try:
            pdf_bytes = HTML(string=full_html).write_pdf(
                stylesheets=[CSS(string=self._get_base_css(options))],
                presentational_hints=True
            )

            logger.info(f"Generated PDF: {len(pdf_bytes)} bytes")

            # Add watermark if enabled
            if options.enable_watermark:
                pdf_bytes = self._add_watermark(
                    pdf_bytes,
                    options.watermark_text or settings.WATERMARK_TEXT,
                    options.watermark_opacity
                )

            # Compress if enabled
            if options.compress:
                pdf_bytes = self._compress_pdf(pdf_bytes)

            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF generation failed: {e}", exc_info=True)
            raise

    def _prepare_html(
        self,
        html_content: str,
        css_content: Optional[str],
        options: PDFGenerationOptions,
        header_html: Optional[str],
        footer_html: Optional[str]
    ) -> str:
        """Prepare complete HTML with header, footer, and page numbers"""

        # Build HTML structure
        html_parts = []

        html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
    """)

        # Add custom CSS
        if css_content:
            html_parts.append(css_content)

        html_parts.append("""
    </style>
</head>
<body>
""")

        # Add header
        if options.include_header and header_html:
            html_parts.append(f'<header>{header_html}</header>')

        # Add main content
        html_parts.append(f'<main>{html_content}</main>')

        # Add footer
        if options.include_footer and footer_html:
            html_parts.append(f'<footer>{footer_html}</footer>')

        html_parts.append("""
</body>
</html>
""")

        return '\n'.join(html_parts)

    def _get_base_css(self, options: PDFGenerationOptions) -> str:
        """Get base CSS for PDF generation"""
        page_size_map = {
            "LETTER": "letter",
            "A4": "A4",
            "LEGAL": "legal"
        }

        page_size = page_size_map.get(options.page_size.upper(), "letter")

        return f"""
@page {{
    size: {page_size} {options.orientation};
    margin-top: {options.margin_top}in;
    margin-bottom: {options.margin_bottom}in;
    margin-left: {options.margin_left}in;
    margin-right: {options.margin_right}in;

    @top-center {{
        content: element(header);
    }}

    @bottom-center {{
        content: element(footer);
    }}

    @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
        font-size: 10pt;
        color: #666;
    }}
}}

body {{
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}}

header {{
    position: running(header);
    border-bottom: 1px solid #ddd;
    padding-bottom: 10px;
    margin-bottom: 20px;
}}

footer {{
    position: running(footer);
    border-top: 1px solid #ddd;
    padding-top: 10px;
    margin-top: 20px;
}}

h1 {{
    font-size: 20pt;
    color: #1a1a1a;
    margin-top: 0;
}}

h2 {{
    font-size: 16pt;
    color: #2a2a2a;
    page-break-after: avoid;
}}

h3 {{
    font-size: 13pt;
    color: #3a3a3a;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    page-break-inside: avoid;
}}

table th {{
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
    font-weight: bold;
}}

table td {{
    border: 1px solid #ddd;
    padding: 8px;
}}

table tr:nth-child(even) {{
    background-color: #fafafa;
}}

.page-break {{
    page-break-after: always;
}}

.avoid-break {{
    page-break-inside: avoid;
}}
"""

    def _add_watermark(
        self,
        pdf_bytes: bytes,
        watermark_text: str,
        opacity: float = 0.3
    ) -> bytes:
        """
        Add watermark to PDF

        Args:
            pdf_bytes: Original PDF content
            watermark_text: Text to use as watermark
            opacity: Watermark opacity (0-1)

        Returns:
            PDF with watermark
        """
        logger.info(f"Adding watermark: {watermark_text}")

        try:
            # Read original PDF
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf_writer = PdfWriter()

            # Create watermark
            watermark_buffer = io.BytesIO()
            c = canvas.Canvas(watermark_buffer, pagesize=letter)

            # Configure watermark
            c.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
            c.setFont("Helvetica", 48)

            # Center watermark diagonally
            width, height = letter
            c.saveState()
            c.translate(width / 2, height / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, watermark_text)
            c.restoreState()

            c.save()

            # Get watermark page
            watermark_buffer.seek(0)
            watermark_reader = PdfReader(watermark_buffer)
            watermark_page = watermark_reader.pages[0]

            # Apply watermark to all pages
            for page in pdf_reader.pages:
                page.merge_page(watermark_page)
                pdf_writer.add_page(page)

            # Write output
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)

            return output_buffer.read()

        except Exception as e:
            logger.error(f"Failed to add watermark: {e}")
            # Return original PDF if watermarking fails
            return pdf_bytes

    def _compress_pdf(self, pdf_bytes: bytes) -> bytes:
        """
        Compress PDF to reduce file size

        Args:
            pdf_bytes: Original PDF content

        Returns:
            Compressed PDF
        """
        logger.info("Compressing PDF")

        try:
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf_writer = PdfWriter()

            for page in pdf_reader.pages:
                page.compress_content_streams()
                pdf_writer.add_page(page)

            # Add compression
            pdf_writer.add_metadata(pdf_reader.metadata)

            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)

            compressed_bytes = output_buffer.read()

            compression_ratio = len(compressed_bytes) / len(pdf_bytes)
            logger.info(f"Compression ratio: {compression_ratio:.2%}")

            return compressed_bytes

        except Exception as e:
            logger.error(f"PDF compression failed: {e}")
            return pdf_bytes

    def add_metadata(
        self,
        pdf_bytes: bytes,
        title: Optional[str] = None,
        author: Optional[str] = None,
        subject: Optional[str] = None,
        keywords: Optional[str] = None
    ) -> bytes:
        """
        Add metadata to PDF

        Args:
            pdf_bytes: Original PDF content
            title: Document title
            author: Document author
            subject: Document subject
            keywords: Document keywords

        Returns:
            PDF with metadata
        """
        try:
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf_writer = PdfWriter()

            # Copy pages
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

            # Add metadata
            metadata = {}
            if title:
                metadata['/Title'] = title
            if author:
                metadata['/Author'] = author
            if subject:
                metadata['/Subject'] = subject
            if keywords:
                metadata['/Keywords'] = keywords

            metadata['/Creator'] = 'Aura Audit AI Reporting Service'
            metadata['/Producer'] = 'Aura Audit AI'
            metadata['/CreationDate'] = datetime.now()

            pdf_writer.add_metadata(metadata)

            # Write output
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)

            return output_buffer.read()

        except Exception as e:
            logger.error(f"Failed to add metadata: {e}")
            return pdf_bytes

    def compute_hash(self, pdf_bytes: bytes) -> str:
        """
        Compute SHA256 hash of PDF for integrity verification

        Args:
            pdf_bytes: PDF content

        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(pdf_bytes).hexdigest()

    def render_template(
        self,
        template_html: str,
        context: dict
    ) -> str:
        """
        Render Jinja2 template with context data

        Args:
            template_html: Jinja2 template HTML
            context: Template context data

        Returns:
            Rendered HTML
        """
        try:
            template = Template(template_html)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}", exc_info=True)
            raise ValueError(f"Template rendering error: {str(e)}")


# Global PDF service instance
pdf_service = PDFGenerationService()
