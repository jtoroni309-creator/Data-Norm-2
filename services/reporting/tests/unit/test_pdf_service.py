"""Unit tests for PDF generation service"""
import pytest
from app.pdf_service import PDFGenerationService, pdf_service
from app.schemas import PDFGenerationOptions


class TestPDFGenerationService:
    """Test PDF generation functionality"""

    def test_generate_from_html_simple(self):
        """Test simple HTML to PDF conversion"""
        service = PDFGenerationService()

        html = "<h1>Test Report</h1><p>This is a test.</p>"

        pdf_bytes = service.generate_from_html(html)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')  # PDF magic number

    def test_generate_with_css(self):
        """Test HTML to PDF with CSS"""
        service = PDFGenerationService()

        html = "<h1>Styled Report</h1>"
        css = "h1 { color: blue; font-size: 24pt; }"

        pdf_bytes = service.generate_from_html(html, css_content=css)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_with_options(self):
        """Test PDF generation with custom options"""
        service = PDFGenerationService()

        html = "<h1>Custom Report</h1>"
        options = PDFGenerationOptions(
            page_size="A4",
            orientation="landscape",
            enable_watermark=False,
            compress=True
        )

        pdf_bytes = service.generate_from_html(html, options=options)

        assert pdf_bytes is not None

    def test_generate_with_watermark(self):
        """Test PDF generation with watermark"""
        service = PDFGenerationService()

        html = "<h1>Confidential Report</h1>"
        options = PDFGenerationOptions(
            enable_watermark=True,
            watermark_text="DRAFT",
            watermark_opacity=0.5
        )

        pdf_bytes = service.generate_from_html(html, options=options)

        assert pdf_bytes is not None
        # Watermarked PDF should be larger than non-watermarked
        assert len(pdf_bytes) > 1000

    def test_render_template(self):
        """Test Jinja2 template rendering"""
        service = PDFGenerationService()

        template_html = "<h1>{{ title }}</h1><p>{{ content }}</p>"
        context = {
            "title": "Test Report",
            "content": "This is dynamic content"
        }

        rendered = service.render_template(template_html, context)

        assert "Test Report" in rendered
        assert "This is dynamic content" in rendered

    def test_render_template_with_loop(self):
        """Test template rendering with loops"""
        service = PDFGenerationService()

        template_html = """
        <ul>
        {% for item in items %}
            <li>{{ item }}</li>
        {% endfor %}
        </ul>
        """

        context = {
            "items": ["Item 1", "Item 2", "Item 3"]
        }

        rendered = service.render_template(template_html, context)

        assert "Item 1" in rendered
        assert "Item 2" in rendered
        assert "Item 3" in rendered

    def test_add_metadata(self):
        """Test adding metadata to PDF"""
        service = PDFGenerationService()

        html = "<h1>Test</h1>"
        pdf_bytes = service.generate_from_html(html)

        pdf_with_metadata = service.add_metadata(
            pdf_bytes,
            title="Test Report",
            author="Aura Audit AI",
            subject="Testing",
            keywords="test, pdf"
        )

        assert pdf_with_metadata is not None
        assert len(pdf_with_metadata) > 0

    def test_compute_hash(self):
        """Test PDF hash computation"""
        service = PDFGenerationService()

        html = "<h1>Test</h1>"
        pdf_bytes = service.generate_from_html(html)

        hash1 = service.compute_hash(pdf_bytes)
        hash2 = service.compute_hash(pdf_bytes)

        # Same content should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex string

        # Different content should produce different hash
        html2 = "<h1>Different</h1>"
        pdf_bytes2 = service.generate_from_html(html2)
        hash3 = service.compute_hash(pdf_bytes2)

        assert hash1 != hash3

    def test_page_size_options(self):
        """Test different page sizes"""
        service = PDFGenerationService()

        html = "<h1>Test</h1>"

        for page_size in ["LETTER", "A4", "LEGAL"]:
            options = PDFGenerationOptions(page_size=page_size)
            pdf_bytes = service.generate_from_html(html, options=options)
            assert pdf_bytes is not None

    def test_complex_html(self):
        """Test PDF generation with complex HTML"""
        service = PDFGenerationService()

        html = """
        <html>
        <body>
            <h1>Annual Audit Report</h1>
            <h2>Executive Summary</h2>
            <p>This is the executive summary.</p>

            <h2>Financial Statements</h2>
            <table>
                <tr>
                    <th>Account</th>
                    <th>Balance</th>
                </tr>
                <tr>
                    <td>Cash</td>
                    <td>$1,000,000</td>
                </tr>
                <tr>
                    <td>Accounts Receivable</td>
                    <td>$500,000</td>
                </tr>
            </table>

            <h2>Conclusion</h2>
            <p>The financial statements present fairly...</p>
        </body>
        </html>
        """

        pdf_bytes = service.generate_from_html(html)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 2000  # Should be substantial

    def test_header_footer(self):
        """Test PDF generation with header and footer"""
        service = PDFGenerationService()

        html = "<h1>Main Content</h1>"
        header_html = "<div>Header Text</div>"
        footer_html = "<div>Footer Text</div>"

        options = PDFGenerationOptions(
            include_header=True,
            include_footer=True
        )

        pdf_bytes = service.generate_from_html(
            html,
            options=options,
            header_html=header_html,
            footer_html=footer_html
        )

        assert pdf_bytes is not None

    def test_invalid_template(self):
        """Test error handling for invalid templates"""
        service = PDFGenerationService()

        template_html = "{{ missing_var }}"  # Will raise error
        context = {}

        # Should handle Jinja2 errors gracefully
        with pytest.raises(Exception):
            service.render_template(template_html, context)
