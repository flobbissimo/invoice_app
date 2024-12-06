"""
Generatore PDF - Gestisce la creazione di PDF con layout moderno a due colonne

Questo modulo fornisce la classe PDFGenerator che crea ricevute professionali con:
- Design moderno a due colonne per l'intestazione
- Supporto per il logo aziendale
- Spaziatura e tipografia moderne
- Chiara separazione delle sezioni

Possibili miglioramenti:
- Aggiungere più template tra cui scegliere
- Implementare la personalizzazione dei colori
- Aggiungere codici QR per pagamenti
- Supportare firme digitali
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
    """Genera PDF delle ricevute con layout moderno"""
    
    def __init__(self, config_dir: str = "config", output_dir: str = "data/invoices"):
        """
        Inizializza il generatore PDF.
        
        Args:
            config_dir: Directory per i file di configurazione
            output_dir: Directory per i PDF generati
            
        Crea:
        - Stili del documento
        - Directory necessarie
        - Carica configurazione aziendale
        
        Possibili miglioramenti:
        - Aggiungere supporto per template multipli
        - Implementare cache dei loghi
        - Supportare più formati di output
        """
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.company_details = self._load_company_details()
        self._ensure_directories()
        self._setup_styles()

    def _ensure_directories(self):
        """Assicura che le directory necessarie esistano"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_company_details(self) -> dict:
        """
        Carica i dettagli dell'azienda dalla configurazione.
        
        Returns:
            dict: Dettagli dell'azienda
            
        Possibili miglioramenti:
        - Aggiungere validazione dei dati
        - Supportare più profili aziendali
        - Implementare backup automatico
        """
        config_file = self.config_dir / "settings.json"
        if not config_file.exists():
            # Crea configurazione predefinita se non esiste
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
                # Estrae i dettagli dalla struttura di settings.json
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
        Ricarica i dettagli dell'azienda dal file di configurazione.
        
        Utile quando i dettagli vengono modificati dall'interfaccia.
        
        Possibili miglioramenti:
        - Aggiungere notifica di cambiamenti
        - Implementare ricaricamento automatico
        - Validare i nuovi dati
        """
        self.company_details = self._load_company_details()

    def _setup_styles(self):
        """
        Configura gli stili del documento PDF.
        
        Crea stili per:
        - Titolo principale
        - Nome azienda
        - Numero ricevuta
        - Testo normale
        - Totali
        
        Possibili miglioramenti:
        - Aggiungere più temi colore
        - Supportare font personalizzati
        - Implementare stili responsivi
        """
        styles = getSampleStyleSheet()
        
        # Stile titolo principale (RICEVUTA)
        self.main_title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#000000')
        )
        
        # Stile nome azienda
        self.company_name_style = ParagraphStyle(
            'CompanyName',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_LEFT
        )
        
        # Stile numero ricevuta
        self.invoice_number_style = ParagraphStyle(
            'InvoiceNumber',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_RIGHT
        )
        
        # Stile testo normale
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_LEFT
        )
        
        # Stile testo allineato a destra
        self.right_style = ParagraphStyle(
            'RightAligned',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_RIGHT
        )
        
        # Stile titolo sezione
        self.section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            alignment=TA_LEFT
        )
        
        # Stile totale
        self.total_style = ParagraphStyle(
            'CustomTotal',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )

    def _create_header(self, invoice: Invoice) -> list:
        """
        Crea l'intestazione moderna a due colonne.
        
        Args:
            invoice: Ricevuta da processare
            
        Returns:
            list: Elementi dell'intestazione
            
        Possibili miglioramenti:
        - Aggiungere più layout di intestazione
        - Supportare immagini di sfondo
        - Implementare codici QR
        """
        elements = []
        
        # Titolo principale
        elements.extend([
            Paragraph("RICEVUTA", self.main_title_style),
            Spacer(1, 10)
        ])
        
        # Crea intestazione a due colonne
        # Colonna sinistra: Info azienda (e logo se disponibile)
        left_column = []
        
        # Aggiunge il logo se esiste
        logo_path = self.config_dir / "logo.png"
        if logo_path.exists():
            try:
                logo = Image(str(logo_path))
                # Scala il logo a dimensioni ragionevoli
                logo.drawHeight = 2*cm
                logo.drawWidth = 4*cm
                left_column.append(logo)
                left_column.append(Spacer(1, 10))
            except:
                pass  # Ignora errori del logo
        
        # Dettagli azienda
        if self.company_details.get('company_name'):
            left_column.extend([
                Paragraph(f"<b>{self.company_details['company_name']}</b>", self.company_name_style)
            ])
            
            # Aggiunge indirizzo
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
            
            # Aggiunge dettagli fiscali
            if self.company_details.get('vat_number'):
                left_column.append(
                    Paragraph(f"P.IVA: {self.company_details['vat_number']}", self.normal_style)
                )
            if self.company_details.get('sdi'):
                left_column.append(
                    Paragraph(f"SDI: {self.company_details['sdi']}", self.normal_style)
                )
            
            # Aggiunge contatti
            if self.company_details.get('phone'):
                left_column.append(
                    Paragraph(f"Tel: {self.company_details['phone']}", self.normal_style)
                )
            if self.company_details.get('email'):
                left_column.append(
                    Paragraph(f"Email: {self.company_details['email']}", self.normal_style)
                )
        
        # Colonna destra: Dettagli ricevuta
        right_column = [
            Paragraph(f"N° {invoice.invoice_number}", self.invoice_number_style),
            Paragraph(f"Data: {invoice.date.strftime('%d/%m/%Y')}", self.right_style),
            Spacer(1, 10)
        ]
        
        # Crea tabella per layout a due colonne
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
        
        # Sezione cliente
        if invoice.customer_name:
            elements.append(Paragraph("CLIENTE", self.section_title_style))
            customer_info = []
            
            # Aggiunge dettagli cliente
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
        Crea la tabella degli articoli con stile moderno.
        
        Args:
            invoice: Ricevuta da processare
            
        Returns:
            Table: Tabella degli articoli formattata
            
        Possibili miglioramenti:
        - Aggiungere stili alternati per le righe
        - Implementare subtotali per gruppi
        - Aggiungere colonne personalizzabili
        """
        # Intestazione tabella
        data = [['Descrizione', 'Quantità', 'Prezzo', 'Totale']]
        
        # Aggiunge articoli
        for item in invoice.items:
            data.append([
                item.description,
                f"{item.quantity:.2f}",
                f"€ {item.price:.2f}",
                f"€ {item.total:.2f}"
            ])
        
        # Crea tabella
        table = Table(data, colWidths=[9*cm, 3*cm, 3*cm, 3*cm])
        
        # Stile moderno tabella
        style = TableStyle([
            # Allineamento
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Descrizione allineata a sinistra
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # Numeri allineati a destra
            
            # Stili font
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Intestazione in grassetto
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Spaziatura
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Griglia
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Linea più spessa sotto l'intestazione
        ])
        table.setStyle(style)
        
        return table

    def _create_footer(self, invoice: Invoice) -> list:
        """
        Crea il piè di pagina con totale centrato.
        
        Args:
            invoice: Ricevuta da processare
            
        Returns:
            list: Elementi del piè di pagina
            
        Possibili miglioramenti:
        - Aggiungere note di piè di pagina
        - Implementare termini e condizioni
        - Aggiungere QR code per pagamenti
        """
        elements = [Spacer(1, 20)]
        
        # Aggiunge totale in una tabella per miglior allineamento
        total_table = Table(
            [[Paragraph(f"<b>Totale: € {invoice.total_amount:.2f}</b>", self.total_style)]],
            colWidths=[18*cm],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ])
        )
        elements.append(total_table)
        
        # Aggiunge dettagli pagamento se disponibili
        if self.company_details.get('billing_number'):
            elements.extend([
                Spacer(1, 20),
                Paragraph("<b>Dettagli di pagamento:</b>", self.normal_style),
                Paragraph(f"IBAN: {self.company_details['billing_number']}", self.normal_style)
            ])
        
        return elements

    def generate_pdf(self, invoice: Invoice) -> Path:
        """
        Genera il PDF per la ricevuta specificata.
        
        Args:
            invoice: Ricevuta da processare
            
        Returns:
            Path: Percorso del file PDF generato
            
        Possibili miglioramenti:
        - Aggiungere watermark
        - Implementare firme digitali
        - Supportare più template
        - Aggiungere anteprima PDF
        """
        # Crea percorso file PDF
        pdf_path = self.output_dir / f"{invoice.invoice_number}.pdf"
        
        # Crea documento PDF
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Costruisce il contenuto del documento
        elements = []
        
        # Aggiunge intestazione
        elements.extend(self._create_header(invoice))
        
        # Aggiunge tabella articoli
        elements.append(self._create_items_table(invoice))
        
        # Aggiunge piè di pagina
        elements.extend(self._create_footer(invoice))
        
        # Genera PDF
        doc.build(elements)
        
        return pdf_path 