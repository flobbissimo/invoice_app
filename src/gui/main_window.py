"""
Main Window - Primary application window and entry point
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
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ricevute - Pension Flora")
        
        # Configure message box font and style
        self.root.option_add('*Dialog.msg.font', 'Helvetica 10')
        self.root.option_add('*Dialog.msg.wrapLength', '300')
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate window size based on screen resolution
        # For HD (1920x1080) to 4K (3840x2160)
        width_ratio = min(max(screen_width / 1920, 1.0), 2.0)  # Scale between 1x and 2x
        height_ratio = min(max(screen_height / 1080, 1.0), 2.0)
        
        # Base sizes for HD resolution
        base_width = 1400
        base_height = 900
        
        # Calculate window size
        window_width = int(base_width * width_ratio)
        window_height = int(base_height * height_ratio)
        
        # Calculate font sizes
        self.normal_font_size = int(9 * width_ratio)
        self.header_font_size = int(12 * width_ratio)
        
        # Center window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configure font scaling
        self.default_font = ('Helvetica', self.normal_font_size)
        self.header_font = ('Helvetica', self.header_font_size, 'bold')
        
        # Initialize managers
        self.counter_manager = CounterManager()
        self.storage_manager = StorageManager()
        self.pdf_generator = PDFGenerator()
        
        # Initialize UI components
        self.current_invoice: Optional[Invoice] = None
        self.sort_order = "desc"
        self.setup_menu()
        self.setup_main_frame()
        self.setup_shortcuts()
        self.load_invoice_history()
        
        # Bind resize event
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
        """Setup the invoice history view"""
        # History header frame
        header_frame = ttk.Frame(self.left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # History label and sort button in the same row
        history_label = ttk.Label(header_frame, text="Cronologia Ricevute", font=self.header_font)
        history_label.pack(side=tk.LEFT, pady=(0, 5))
        
        self.sort_button = ttk.Button(
            header_frame,
            text="↓ Data",  # Start with descending order
            width=8,
            command=self.toggle_sort_order
        )
        self.sort_button.pack(side=tk.RIGHT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Cerca:", font=self.default_font).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_history)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=self.default_font)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Treeview style for larger fonts
        style = ttk.Style()
        style.configure("Treeview", font=self.default_font)
        style.configure("Treeview.Heading", font=self.default_font)
        
        # Treeview for history
        columns = ('number', 'date', 'customer', 'amount')
        self.history_tree = ttk.Treeview(self.left_frame, columns=columns, show='headings', style="Treeview")
        
        # Setup columns with proportional widths
        window_width = self.root.winfo_width()
        history_width = window_width // 3
        
        self.history_tree.heading('number', text='Numero')
        self.history_tree.heading('date', text='Data')
        self.history_tree.heading('customer', text='Cliente')
        self.history_tree.heading('amount', text='Importo')
        
        self.history_tree.column('number', width=int(history_width * 0.2))
        self.history_tree.column('date', width=int(history_width * 0.2))
        self.history_tree.column('customer', width=int(history_width * 0.4))
        self.history_tree.column('amount', width=int(history_width * 0.2))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack history view
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click
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
        """Load invoice history into the treeview"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Load invoices
        invoices = self.storage_manager.load_all_invoices()
        
        # Sort by date (newest first by default)
        reverse = self.sort_order == "desc"
        invoices.sort(key=lambda x: x.date, reverse=reverse)
        
        # Add to treeview
        for invoice in invoices:
            self.history_tree.insert('', 'end', values=(
                invoice.invoice_number,
                invoice.date.strftime('%d/%m/%Y'),
                invoice.customer_name or '',
                f"€ {invoice.total_amount:.2f}"
            ))
            
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
        
    def toggle_sort_order(self):
        """Toggle between ascending and descending sort order"""
        self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        self.sort_button.configure(text="↑ Data" if self.sort_order == "asc" else "↓ Data")
        self.load_invoice_history()
        
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