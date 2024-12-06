"""
Finestra Principale - Gestisce l'interfaccia principale dell'applicazione

Questo modulo contiene la classe MainWindow che è responsabile di:
1. Visualizzare e gestire la lista delle ricevute
2. Permettere la creazione e modifica delle ricevute
3. Gestire l'ordinamento e la ricerca
4. Coordinare tutte le operazioni principali

Possibili miglioramenti:
- Aggiungere supporto per temi personalizzati
- Implementare la possibilità di personalizzare le colonne visibili
- Aggiungere grafici e statistiche
- Implementare filtri avanzati per la ricerca
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess
import sys
from typing import Optional
from datetime import datetime

from ..core.counter_manager import CounterManager
from ..core.storage_manager import StorageManager
from ..core.pdf_generator import PDFGenerator
from .invoice_form import InvoiceForm, CustomMessageBox
from .company_config import CompanyConfigDialog
from .invoice_manager import InvoiceManagerDialog
from ..models.invoice import Invoice

class MainWindow:
    """Finestra principale dell'applicazione"""
    
    def __init__(self):
        """
        Inizializza la finestra principale.
        
        Crea:
        - La finestra root con Tkinter
        - I manager per la gestione dei dati
        - L'interfaccia utente principale
        - Il sistema di ordinamento
        
        Possibili miglioramenti:
        - Salvare e caricare le dimensioni della finestra
        - Aggiungere supporto per monitor multipli
        - Implementare un sistema di temi
        """
        # Inizializza la finestra principale
        self.root = tk.Tk()
        self.root.title("Ricevute - Pension Flora")
        
        # Configura il font per i messaggi di dialogo
        self.root.option_add('*Dialog.msg.font', 'Helvetica 10')
        self.root.option_add('*Dialog.msg.wrapLength', '300')
        
        # Calcola le dimensioni della finestra in base alla risoluzione dello schermo
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcola il rapporto di scala per schermi ad alta risoluzione
        width_ratio = min(max(screen_width / 1920, 1.0), 2.0)  # Scala tra 1x e 2x
        height_ratio = min(max(screen_height / 1080, 1.0), 2.0)
        
        # Dimensioni base per risoluzione HD
        base_width = 1400
        base_height = 900
        
        # Calcola le dimensioni effettive della finestra
        window_width = int(base_width * width_ratio)
        window_height = int(base_height * height_ratio)
        
        # Calcola le dimensioni dei font
        self.normal_font_size = int(9 * width_ratio)
        self.header_font_size = int(12 * width_ratio)
        
        # Centra la finestra sullo schermo
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configura i font
        self.default_font = ('Helvetica', self.normal_font_size)
        self.header_font = ('Helvetica', self.header_font_size, 'bold')
        
        # Inizializza i manager per la gestione dei dati
        self.counter_manager = CounterManager()  # Gestisce la numerazione delle ricevute
        self.storage_manager = StorageManager()  # Gestisce il salvataggio e caricamento
        self.pdf_generator = PDFGenerator()      # Gestisce la generazione dei PDF
        
        # Inizializza le variabili di stato
        self.current_invoice: Optional[Invoice] = None  # Ricevuta correntemente in modifica
        self.sort_column = 'date'    # Colonna per l'ordinamento (default: data)
        self.sort_order = "desc"     # Ordine di ordinamento (default: decrescente)
        
        # Configura l'interfaccia
        self.setup_menu()            # Crea il menu principale
        self.setup_main_frame()      # Crea il layout principale
        self.setup_shortcuts()       # Configura le scorciatoie da tastiera
        self.load_invoice_history()  # Carica la lista delle ricevute
        
        # Gestisce il ridimensionamento della finestra
        self.root.bind('<Configure>', self.on_window_resize)
        
    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            # Update column widths based on window size
            window_width = event.width
            history_width = window_width // 3  # History takes 1/3 of window width
            
            # Calculate proportional column widths
            self.history_tree.column('number', width=int(history_width * 0.2))
            self.history_tree.column('date', width=int(history_width * 0.2))
            self.history_tree.column('customer', width=int(history_width * 0.4))
            self.history_tree.column('amount', width=int(history_width * 0.2))
            
    def setup_menu(self):
        """Setup the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Configure menu font
        menu_font = ('Helvetica', self.normal_font_size)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="File", menu=file_menu, font=menu_font)
        file_menu.add_command(label="Nuova Ricevuta (Ctrl+N)", command=self.new_invoice)
        file_menu.add_command(label="Salva (Ctrl+S)", command=self.save_invoice)
        file_menu.add_command(label="Apri PDF (Ctrl+P)", command=self.open_last_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Gestione Ricevute (Ctrl+M)", command=self.open_invoice_manager)
        file_menu.add_command(label="Configura Azienda (Ctrl+C)", command=self.configure_company)
        file_menu.add_separator()
        file_menu.add_command(label="Esci (Alt+F4)", command=self.root.quit)
        
        # Edit menu with font
        edit_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="Modifica", menu=edit_menu, font=menu_font)
        edit_menu.add_command(label="Cancella (Ctrl+Del)", command=self.clear_form)
        edit_menu.add_command(label="Duplica (Ctrl+D)", command=self.duplicate_invoice)
        
        # View menu with font
        view_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="Visualizza", menu=view_menu, font=menu_font)
        view_menu.add_command(label="Mostra Cronologia (Ctrl+H)", command=self.toggle_history)
        
        # Help menu with font
        help_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="Aiuto", menu=help_menu, font=menu_font)
        help_menu.add_command(label="Informazioni (F1)", command=self.show_about)
        
    def setup_main_frame(self):
        """Setup the main application frame"""
        # Create main container with PanedWindow
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for history (1/3 width)
        self.left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_frame, weight=1)
        self.setup_history_view()
        
        # Right panel for invoice form (2/3 width)
        self.right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_frame, weight=2)
        self.invoice_form = InvoiceForm(self.right_frame, self.counter_manager)
        
    def setup_history_view(self):
        """
        Configura la vista della cronologia delle ricevute.
        
        Crea:
        - Intestazione con titolo
        - Campo di ricerca
        - Tabella delle ricevute con colonne ordinabili
        - Barra di scorrimento
        
        Possibili miglioramenti:
        - Aggiungere filtri avanzati
        - Permettere la personalizzazione delle colonne
        - Aggiungere preview delle ricevute al passaggio del mouse
        - Implementare la selezione multipla
        """
        # Frame per l'intestazione
        header_frame = ttk.Frame(self.left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Etichetta del titolo
        history_label = ttk.Label(header_frame, text="Cronologia Ricevute", font=self.header_font)
        history_label.pack(side=tk.LEFT, pady=(0, 5))
        
        # Frame per la ricerca
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Campo di ricerca con etichetta
        ttk.Label(search_frame, text="Cerca:", font=self.default_font).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_history)  # Aggiorna la lista durante la digitazione
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=self.default_font)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Configura lo stile della tabella
        style = ttk.Style()
        style.configure("Treeview", font=self.default_font)
        style.configure("Treeview.Heading", font=self.default_font)
        
        # Crea la tabella delle ricevute
        columns = ('number', 'date', 'customer', 'amount')
        self.history_tree = ttk.Treeview(self.left_frame, columns=columns, show='headings', style="Treeview")
        
        # Calcola le larghezze delle colonne
        window_width = self.root.winfo_width()
        history_width = window_width // 3
        
        # Configura le intestazioni delle colonne con funzionalità di ordinamento
        self.history_tree.heading('number', text='Numero', command=lambda: self.sort_history('number'))
        self.history_tree.heading('date', text='Data', command=lambda: self.sort_history('date'))
        self.history_tree.heading('customer', text='Cliente', command=lambda: self.sort_history('customer'))
        self.history_tree.heading('amount', text='Importo', command=lambda: self.sort_history('amount'))
        
        # Imposta le larghezze delle colonne
        self.history_tree.column('number', width=int(history_width * 0.2))
        self.history_tree.column('date', width=int(history_width * 0.2))
        self.history_tree.column('customer', width=int(history_width * 0.4))
        self.history_tree.column('amount', width=int(history_width * 0.2))
        
        # Aggiunge la barra di scorrimento
        scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Posiziona la tabella e la barra di scorrimento
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configura il doppio click per aprire una ricevuta
        self.history_tree.bind('<Double-1>', self.load_selected_invoice)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_invoice())
        self.root.bind('<Control-s>', lambda e: self.save_invoice())
        self.root.bind('<Control-p>', lambda e: self.open_last_pdf())
        self.root.bind('<Control-h>', lambda e: self.toggle_history())
        self.root.bind('<Control-c>', lambda e: self.configure_company())
        self.root.bind('<Control-m>', lambda e: self.open_invoice_manager())
        self.root.bind('<Control-d>', lambda e: self.duplicate_invoice())
        self.root.bind('<Control-Delete>', lambda e: self.clear_form())
        self.root.bind('<F1>', lambda e: self.show_about())
        
    def load_invoice_history(self):
        """
        Carica la cronologia delle ricevute nella tabella.
        
        Operazioni:
        1. Pulisce la tabella esistente
        2. Carica tutte le ricevute dal gestore
        3. Inserisce le ricevute nella tabella
        4. Applica l'ordinamento iniziale
        
        Possibili miglioramenti:
        - Implementare il caricamento paginato per grandi dataset
        - Aggiungere una barra di progresso per il caricamento
        - Implementare il caricamento asincrono
        """
        # Pulisce la tabella
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Carica le ricevute dal gestore
        invoices = self.storage_manager.load_all_invoices()
        
        # Inserisce le ricevute nella tabella
        for invoice in invoices:
            self.history_tree.insert('', 'end', values=(
                invoice.invoice_number,
                invoice.date.strftime('%d/%m/%Y'),
                invoice.customer_name or '',
                f"€ {invoice.total_amount:.2f}"
            ))
        
        # Applica l'ordinamento iniziale per data (più recenti prima)
        self.sort_history('date')
        self._last_sort = ('date', True)
        
    def filter_history(self, *args):
        """Filter history based on search text"""
        search_text = self.search_var.get().lower()
        self.load_invoice_history()  # Reload all items
        
        if search_text:
            for item in self.history_tree.get_children():
                values = self.history_tree.item(item)['values']
                if not any(search_text in str(value).lower() for value in values):
                    self.history_tree.delete(item)
                    
    def load_selected_invoice(self, event):
        """Load the selected invoice from history"""
        selection = self.history_tree.selection()
        if not selection:
            return
            
        item = self.history_tree.item(selection[0])
        invoice_number = item['values'][0]
        
        invoice = self.storage_manager.load_invoice(invoice_number)
        if invoice:
            self.invoice_form.load_invoice(invoice)
            self.current_invoice = invoice
            
    def toggle_history(self):
        """Toggle history panel visibility"""
        if self.right_frame.winfo_viewable():
            self.main_paned.forget(self.right_frame)
        else:
            self.main_paned.add(self.right_frame, weight=1)
            
    def duplicate_invoice(self):
        """Duplicate current invoice with new number"""
        if not self.current_invoice:
            messagebox.showwarning("Attenzione", "Nessuna ricevuta da duplicare")
            return
            
        new_invoice = self.current_invoice.copy()
        new_invoice.invoice_number = str(self.counter_manager.get_next_counter())
        new_invoice.date = datetime.now()
        
        self.invoice_form.load_invoice(new_invoice)
        self.current_invoice = new_invoice
        
    def configure_company(self):
        """Open company configuration dialog"""
        CompanyConfigDialog(
            self.root,
            on_config_saved=lambda: self.pdf_generator.reload_company_details()
        )
        
    def new_invoice(self):
        """Create a new invoice"""
        self.invoice_form.clear()
        self.invoice_form.set_next_invoice_number()
        self.current_invoice = None
        
    def save_invoice(self):
        """Save the current invoice and generate PDF"""
        if self.invoice_form.validate():
            try:
                # Get invoice data
                invoice = self.invoice_form.get_invoice_data()
                if not invoice:
                    return
                
                # Save invoice data
                self.storage_manager.save_invoice(invoice)
                
                # Generate PDF
                pdf_path = self.pdf_generator.generate_pdf(invoice)
                
                self.current_invoice = invoice
                self.show_success(f"Ricevuta salvata con successo!\nPDF generato: {pdf_path.name}")
                
                # Open PDF
                if messagebox.askyesno("Apri PDF", "Vuoi aprire il PDF generato?"):
                    self.open_pdf(pdf_path)
                    
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante il salvataggio: {str(e)}")
        
    def open_last_pdf(self):
        """Open the last generated PDF"""
        if not self.current_invoice:
            messagebox.showwarning("Attenzione", "Nessuna ricevuta corrente")
            return
            
        pdf_path = self.pdf_generator.output_dir / f"{self.current_invoice.invoice_number}.pdf"
        if pdf_path.exists():
            self.open_pdf(pdf_path)
        else:
            messagebox.showerror("Errore", "PDF non trovato")
            
    def open_pdf(self, pdf_path: Path):
        """Open PDF file with default system viewer"""
        try:
            if sys.platform == 'win32':
                subprocess.run(['start', '', str(pdf_path)], shell=True)
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(pdf_path)])
            else:
                subprocess.run(['xdg-open', str(pdf_path)])
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il PDF: {str(e)}")
        
    def clear_form(self):
        """Clear the form"""
        if messagebox.askyesno("Conferma", "Vuoi davvero cancellare il form?"):
            self.invoice_form.clear()
            self.current_invoice = None
            
    def show_about(self):
        """Show about dialog"""
        CustomMessageBox.showerror(
            "Informazioni",
            "Ricevute - Pension Flora\nVersione 1.0\n\n© 2024 Pension Flora"
        )
        
    def show_success(self, message: str):
        """Show success message"""
        CustomMessageBox.showerror("Successo", message)
        
    def sort_history(self, column):
        """
        Ordina la cronologia delle ricevute in base alla colonna selezionata.
        
        Args:
            column (str): Nome della colonna su cui ordinare
        
        Funzionamento:
        - Primo click: ordine crescente
        - Secondo click: ordine decrescente
        - Click su colonna diversa: ordine crescente
        
        Possibili miglioramenti:
        - Aggiungere ordinamento per più colonne
        - Salvare l'ultimo ordinamento utilizzato
        - Aggiungere animazioni durante l'ordinamento
        """
        # Ottiene tutti gli elementi dalla tabella
        items = [(self.history_tree.set(item, column), item) for item in self.history_tree.get_children('')]
        
        # Gestisce l'inversione dell'ordine se si clicca la stessa colonna
        if hasattr(self, '_last_sort') and self._last_sort == (column, False):
            items.sort(reverse=True)
            self._last_sort = (column, True)
            arrow = "↑"  # Freccia per ordine crescente
        else:
            items.sort(reverse=False)
            self._last_sort = (column, False)
            arrow = "↓"  # Freccia per ordine decrescente
        
        # Riposiziona gli elementi nella tabella secondo il nuovo ordine
        for index, (val, item) in enumerate(items):
            self.history_tree.move(item, '', index)
        
        # Nomi delle colonne per l'interfaccia
        column_names = {
            'number': 'Numero',
            'date': 'Data',
            'customer': 'Cliente',
            'amount': 'Importo'
        }
        
        # Aggiorna le intestazioni delle colonne
        for col in column_names:
            if col == column:
                # Aggiunge la freccia alla colonna ordinata
                self.history_tree.heading(col, text=f"{column_names[col]} {arrow}")
            else:
                # Ripristina le altre colonne senza freccia
                self.history_tree.heading(col, text=column_names[col])

    def get_column_name(self, column):
        """Get the display name for a column"""
        column_names = {
            'number': 'Numero',
            'date': 'Data',
            'customer': 'Cliente',
            'amount': 'Importo'
        }
        return column_names[column]

    def open_invoice_manager(self):
        """Open the invoice manager dialog"""
        InvoiceManagerDialog(self.root)
        # Reload history after possible changes
        self.load_invoice_history()
        
    def run(self):
        """Start the main event loop"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run() 