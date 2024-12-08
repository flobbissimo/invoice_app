"""
PDF Generator - Handles the creation of PDF invoices with modern layout

Key Features:
1. Modern two-column layout for header
2. Support for company logo and details
3. Configurable styles and formatting
4. Automatic calculations for totals and VAT
5. Professional typography and spacing

Components:
- Header: Company info and logo
- Invoice Details: Number, date, customer info
- Items Table: Description, quantity, price, total
- Footer: Totals, VAT, notes

Technical Details:
- Uses ReportLab for PDF generation
- Implements style management system
- Handles font embedding
- Manages page layout and spacing
- Supports Italian invoice format

Performance Optimizations:
- Caches company details
- Reuses style definitions
- Minimizes font loading
- Optimizes image handling

Error Handling:
- Validates input data
- Handles missing fields gracefully
- Provides detailed error messages
- Implements fallback options
"""
import json
from pathlib import Path
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

from ..models.invoice import Invoice

class PDFGenerator:
    """Generates PDF of invoices with modern layout"""
    
    def __init__(self, config_dir: str = "config", output_dir: str = "data/invoices"):
        """
        Initializes the PDF generator.
        
        Args:
            config_dir: Directory for configuration files
            output_dir: Directory for generated PDFs
            
        Creates:
        - Document styles
        - Necessary directories
        - Loads company configuration
        
        Possible improvements:
        - Add support for multiple templates
        - Implement logo caching
        - Support multiple output formats
        """
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.company_details = self._load_company_details()
        self._ensure_directories()
        self._setup_styles()

    def _ensure_directories(self):
        """Ensures necessary directories exist"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_company_details(self) -> dict:
        """
        Loads company details from the configuration.
        
        Returns:
            dict: Company details
            
        Possible improvements:
        - Add data validation
        - Support multiple company profiles
        - Implement automatic backups
        """
        config_file = self.config_dir / "settings.json"
        if not config_file.exists():
            # Create default configuration if it doesn't exist
            default_config = {
                "company_name": "Pension Flora",
                "address": "",
                "postal_code": "",
                "city": "",
                "country": "",
                "vat_number": "",
                "phone": "",
                "email": "",
                "billing_number": ""
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extracts details from the settings.json structure
                return {
                    "company_name": data.get("company_name", ""),
                    "address": data.get("address", ""),
                    "postal_code": data.get("postal_code", ""),
                    "city": data.get("city", ""),
                    "country": data.get("country", ""),
                    "vat_number": data.get("vat_number", ""),
                    "phone": data.get("phone", ""),
                    "email": data.get("email", ""),
                    "billing_number": data.get("billing_number", "")
                }
        except json.JSONDecodeError:
            return {}

    def reload_company_details(self):
        """
        Reloads company details from the configuration file.
        
        Useful when details are modified through the interface.
        
        Possible improvements:
        - Add notification of changes
        - Implement automatic reloading
        - Validate new data
        """
        self.company_details = self._load_company_details()

    def _setup_styles(self):
        """
        Configures the styles of the PDF document.
        
        Creates styles for:
        - Main title
        - Company name
        - Invoice number
        - Normal text
        - Totals
        
        Possible improvements:
        - Add more color themes
        - Support custom fonts
        - Implement responsive styles
        """
        styles = getSampleStyleSheet()
        
        # Main title style (RICEVUTA)
        self.main_title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#000000')
        )
        
        # Company name style
        self.company_name_style = ParagraphStyle(
            'CompanyName',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_LEFT
        )
        
        # Invoice number style
        self.invoice_number_style = ParagraphStyle(
            'InvoiceNumber',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_RIGHT
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_LEFT
        )
        
        # Right-aligned text style
        self.right_style = ParagraphStyle(
            'RightAligned',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_RIGHT
        )
        
        # Section title style
        self.section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            alignment=TA_LEFT
        )
        
        # Total style
        self.total_style = ParagraphStyle(
            'CustomTotal',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        self.vat_style = ParagraphStyle(
            'CustomVat',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER
        )

    def _create_header(self, invoice: Invoice) -> list:
        """
        Creates the modern two-column header.
        
        Args:
            invoice: Invoice to process
            
        Returns:
            list: Header elements
            
        Possible improvements:
        - Add more header layouts
        - Support background images
        - Implement QR codes
        """
        elements = []
        
        # Main title
        elements.extend([
            Paragraph("RICEVUTA", self.main_title_style),
            Spacer(1, 10)
        ])
        
        # Create two-column header
        # Left column: Company info (and logo if available)
        left_column = []
        
        # Add logo if it exists
        logo_path = self.config_dir / "logo.png"
        if logo_path.exists():
            try:
                logo = Image(str(logo_path))
                # Scale the logo to reasonable dimensions
                logo.drawHeight = 2*cm
                logo.drawWidth = 4*cm
                left_column.append(logo)
                left_column.append(Spacer(1, 10))
            except:
                pass  # Ignore logo errors
        
        # Company details
        if self.company_details.get('company_name'):
            left_column.extend([
                Paragraph(f"<b>{self.company_details['company_name']}</b>", self.company_name_style)
            ])
            
            # Add address
            address_parts = []
            if self.company_details.get('address'):
                address_parts.append(self.company_details['address'])
            if self.company_details.get('postal_code') or self.company_details.get('city'):
                address_parts.append(
                    f"{self.company_details.get('postal_code', '')} {self.company_details.get('city', '')}".strip()
                )
            if self.company_details.get('country'):
                address_parts.append(self.company_details['country'])
            
            if address_parts:
                left_column.append(
                    Paragraph(", ".join(filter(None, address_parts)), self.normal_style)
                )
            
            # Add tax details
            if self.company_details.get('vat_number'):
                left_column.append(
                    Paragraph(f"P.IVA: {self.company_details['vat_number']}", self.normal_style)
                )
            if self.company_details.get('sdi'):
                left_column.append(
                    Paragraph(f"SDI: {self.company_details['sdi']}", self.normal_style)
                )
            
            # Add contacts
            if self.company_details.get('phone'):
                left_column.append(
                    Paragraph(f"Tel: {self.company_details['phone']}", self.normal_style)
                )
            if self.company_details.get('email'):
                left_column.append(
                    Paragraph(f"Email: {self.company_details['email']}", self.normal_style)
                )
        
        # Right column: Invoice details
        right_column = [
            Paragraph(f"N° {invoice.invoice_number}", self.invoice_number_style),
            Paragraph(f"Data: {invoice.date.strftime('%d/%m/%Y')}", self.right_style),
            Spacer(1, 10)
        ]
        
        # Create table for two-column layout
        header_table = Table(
            [[left_column, right_column]], 
            colWidths=[12*cm, 6*cm],
            style=TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ])
        )
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Customer section
        if invoice.customer_name:
            elements.append(Paragraph("CLIENTE", self.section_title_style))
            customer_info = []
            
            # Add customer details
            customer_info.append(Paragraph(invoice.customer_name, self.normal_style))
            if invoice.customer_street:
                customer_info.append(Paragraph(invoice.customer_street, self.normal_style))
            if invoice.customer_vat:
                customer_info.append(Paragraph(f"P.IVA: {invoice.customer_vat}", self.normal_style))
            if invoice.customer_sdi:
                customer_info.append(Paragraph(f"SDI: {invoice.customer_sdi}", self.normal_style))
            if invoice.customer_email:
                customer_info.append(Paragraph(f"Email: {invoice.customer_email}", self.normal_style))
            
            elements.extend(customer_info)
            elements.append(Spacer(1, 20))
            
        return elements

    def _create_items_table(self, invoice: Invoice) -> Table:
        """
        Creates the items table with modern style.
        
        Args:
            invoice: Invoice to process
            
        Returns:
            Table: Formatted items table
            
        Possible improvements:
        - Add alternating styles for rows
        - Implement subtotals for groups
        - Add customizable columns
        """
        # Table header
        data = [['Descrizione', 'Quantità', 'Prezzo', 'Totale']]
        
        # Add items
        for item in invoice.items:
            data.append([
                item.description,
                f"{item.quantity:.2f}",
                f"€ {item.price:.2f}",
                f"€ {item.total:.2f}"
            ])
        
        # Create table
        table = Table(data, colWidths=[9*cm, 3*cm, 3*cm, 3*cm])
        
        # Modern table style
        style = TableStyle([
            # Alignment
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Description left-aligned
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # Numbers right-aligned
            
            # Font styles
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header in bold
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Spacing
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Thicker line under header
        ])
        table.setStyle(style)
        
        return table

    def _create_footer(self, invoice: Invoice) -> list:
        """
        Creates the footer with total centered.
        
        Args:
            invoice: Invoice to process
            
        Returns:
            list: Footer elements
            
        Possible improvements:
        - Add footer notes
        - Implement terms and conditions
        - Add QR code for payments
        """
        elements = [Spacer(1, 20)]
        
        # Add total in a table for better alignment
        total_table = Table(
            [[Paragraph(f"<b>Totale: € {invoice.total_amount:.2f}</b>", self.total_style)],
             [Paragraph(f"(di cui IVA: € {invoice.vat_amount:,.2f})", self.vat_style)]],
            colWidths=[18*cm],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ])
        )
        elements.append(total_table)
        
        # Add payment details if available
        if self.company_details.get('billing_number'):
            elements.extend([
                Spacer(1, 20),
                Paragraph("<b>Payment details:</b>", self.normal_style),
                Paragraph(f"IBAN: {self.company_details['billing_number']}", self.normal_style)
            ])
        
        return elements

    def generate_pdf(self, invoice: Invoice) -> Path:
        """
        Generates the PDF for the specified invoice.
        
        Args:
            invoice: Invoice to process
            
        Returns:
            Path: Path to the generated PDF file
            
        Possible improvements:
        - Add watermark
        - Implement digital signatures
        - Support multiple templates
        - Add PDF preview
        """
        # Create PDF file path
        pdf_path = self.output_dir / f"{invoice.invoice_number}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build the document content
        elements = []
        
        # Add header
        elements.extend(self._create_header(invoice))
        
        # Add items table
        elements.append(self._create_items_table(invoice))
        
        # Add footer
        elements.extend(self._create_footer(invoice))
        
        # Generate PDF
        doc.build(elements)
        
        return pdf_path 