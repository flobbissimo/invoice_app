"""
Invoice Form - Form for creating and editing invoices
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from ..core.counter_manager import CounterManager
from ..core.fix_dates import parse_date, format_date, format_date_display
from ..models.invoice import Invoice, InvoiceItem

class CustomMessageBox:
    """Custom message box without font options"""
    @staticmethod
    def showerror(title, message):
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.transient()
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Message
        msg_frame = ttk.Frame(dialog, padding="20")
        msg_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(msg_frame, text=message, wraplength=250).pack(expand=True)
        
        # OK button
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ok_btn = ttk.Button(btn_frame, text="OK", command=dialog.destroy)
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # Handle window close button
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        
        # Position the dialog relative to the main window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = dialog.winfo_toplevel().winfo_x() + (dialog.winfo_toplevel().winfo_width() - width) // 2
        y = dialog.winfo_toplevel().winfo_y() + (dialog.winfo_toplevel().winfo_height() - height) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.wait_window()
        
    @staticmethod
    def showinfo(title, message):
        CustomMessageBox.showerror(title, message)
        
    @staticmethod
    def askyesno(title, message) -> bool:
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.transient()
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Message
        msg_frame = ttk.Frame(dialog, padding="20")
        msg_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(msg_frame, text=message, wraplength=250).pack(expand=True)
        
        # Result variable
        result = tk.BooleanVar(value=False)
        
        # Buttons frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def on_yes():
            result.set(True)
            dialog.destroy()
            
        def on_no():
            result.set(False)
            dialog.destroy()
        
        yes_btn = ttk.Button(btn_frame, text="Si", command=on_yes)
        yes_btn.pack(side=tk.RIGHT, padx=5)
        
        no_btn = ttk.Button(btn_frame, text="No", command=on_no)
        no_btn.pack(side=tk.RIGHT, padx=5)
        
        # Handle window close button
        dialog.protocol("WM_DELETE_WINDOW", on_no)
        
        # Position the dialog relative to the main window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = dialog.winfo_toplevel().winfo_x() + (dialog.winfo_toplevel().winfo_width() - width) // 2
        y = dialog.winfo_toplevel().winfo_y() + (dialog.winfo_toplevel().winfo_height() - height) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.wait_window()
        return result.get()

class InvoiceForm:
    """Form for creating and editing invoices"""
    
    def __init__(self, parent, counter_manager):
        self.parent = parent
        self.counter_manager = counter_manager
        
        # Get screen dimensions for scaling
        screen_width = parent.winfo_screenwidth()
        width_ratio = min(max(screen_width / 1920, 1.0), 2.0)  # Scale between 1x and 2x
        
        # Configure fonts
        self.normal_font_size = int(9 * width_ratio)
        self.header_font_size = int(12 * width_ratio)
        self.default_font = ('Helvetica', self.normal_font_size)
        self.header_font = ('Helvetica', self.header_font_size, 'bold')
        
        # Configure padding and spacing
        self.padx = int(5 * width_ratio)
        self.pady = int(5 * width_ratio)
        self.entry_width = int(30 * width_ratio)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the form UI"""
        # Main form container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=self.padx * 2, pady=self.pady * 2)
        
        # Form title
        title_label = ttk.Label(main_frame, text="Nuova Ricevuta", font=self.header_font)
        title_label.pack(fill=tk.X, pady=(0, self.pady * 2))
        
        # Customer details frame
        customer_frame = ttk.LabelFrame(main_frame, text="Dati Cliente", padding=self.padx)
        customer_frame.pack(fill=tk.X, pady=self.pady)
        
        # Configure grid weights
        customer_frame.grid_columnconfigure(1, weight=1)
        customer_frame.grid_columnconfigure(3, weight=1)
        
        # Customer fields with scaled fonts
        fields = [
            ("Numero:", "invoice_number", 0),
            ("Data:", "date", 0),
            ("Nome:", "customer_name", 1),
            ("P.IVA:", "customer_vat", 1),
            ("SDI:", "customer_sdi", 2),
            ("Indirizzo:", "customer_street", 2),
            ("Email:", "customer_email", 3)
        ]
        
        self.customer_fields = {}
        for i, (label, field, row) in enumerate(fields):
            col = (i % 2) * 2
            ttk.Label(customer_frame, text=label, font=self.default_font).grid(
                row=row, column=col, sticky=tk.E, padx=self.padx, pady=self.pady
            )
            entry = ttk.Entry(customer_frame, font=self.default_font, width=self.entry_width)
            entry.grid(row=row, column=col + 1, sticky=tk.EW, padx=self.padx, pady=self.pady)
            self.customer_fields[field] = entry
        
        # Set current date in display format
        self.customer_fields['date'].insert(0, format_date_display(datetime.now()))
        
        # Items frame
        items_frame = ttk.LabelFrame(main_frame, text="Articoli", padding=self.padx)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=self.pady)
        
        # Items entry frame
        entry_frame = ttk.Frame(items_frame)
        entry_frame.pack(fill=tk.X, pady=self.pady)
        
        # Item entry fields with scaled fonts
        ttk.Label(entry_frame, text="Descrizione:", font=self.default_font).pack(side=tk.LEFT, padx=self.padx)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(entry_frame, textvariable=self.description_var, font=self.default_font, width=int(self.entry_width * 1.5))
        self.description_entry.pack(side=tk.LEFT, padx=self.padx)
        
        ttk.Label(entry_frame, text="Quantità:", font=self.default_font).pack(side=tk.LEFT, padx=self.padx)
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ttk.Entry(entry_frame, textvariable=self.quantity_var, font=self.default_font, width=int(self.entry_width * 0.3))
        self.quantity_entry.pack(side=tk.LEFT, padx=self.padx)
        
        ttk.Label(entry_frame, text="Prezzo:", font=self.default_font).pack(side=tk.LEFT, padx=self.padx)
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(entry_frame, textvariable=self.price_var, font=self.default_font, width=int(self.entry_width * 0.3))
        self.price_entry.pack(side=tk.LEFT, padx=self.padx)
        
        add_button = ttk.Button(entry_frame, text="Aggiungi", command=self.add_item)
        add_button.pack(side=tk.LEFT, padx=self.padx)
        
        # Items list with scaled fonts
        columns = ('description', 'quantity', 'price', 'total')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', style="Treeview")
        
        # Configure Treeview style for larger fonts
        style = ttk.Style()
        style.configure("Treeview", font=self.default_font)
        style.configure("Treeview.Heading", font=self.default_font)
        
        # Setup columns with proportional widths
        self.items_tree.heading('description', text='Descrizione')
        self.items_tree.heading('quantity', text='Quantità')
        self.items_tree.heading('price', text='Prezzo')
        self.items_tree.heading('total', text='Totale')
        
        # Set column widths proportionally
        total_width = main_frame.winfo_width()
        self.items_tree.column('description', width=int(total_width * 0.4))
        self.items_tree.column('quantity', width=int(total_width * 0.2))
        self.items_tree.column('price', width=int(total_width * 0.2))
        self.items_tree.column('total', width=int(total_width * 0.2))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack items list
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Notes frame with scaled fonts
        notes_frame = ttk.LabelFrame(main_frame, text="Note", padding=self.padx)
        notes_frame.pack(fill=tk.X, pady=self.pady)
        
        self.notes_text = tk.Text(notes_frame, height=3, font=self.default_font)
        self.notes_text.pack(fill=tk.X, padx=self.padx, pady=self.pady)
        
        # Totals frame with scaled fonts
        totals_frame = ttk.Frame(main_frame)
        totals_frame.pack(fill=tk.X, pady=self.pady)
        
        self.total_label = ttk.Label(
            totals_frame,
            text="Totale: € 0.00",
            font=self.header_font,
            anchor=tk.E
        )
        self.total_label.pack(side=tk.RIGHT, padx=self.padx)
        
        # Bind events
        self.description_entry.bind('<Return>', lambda e: self.add_item())
        self.quantity_entry.bind('<Return>', lambda e: self.add_item())
        self.price_entry.bind('<Return>', lambda e: self.add_item())
        self.items_tree.bind('<Delete>', self.remove_selected_item)
        
        # Bind resize event
        self.parent.bind('<Configure>', self.on_resize)
        
    def on_resize(self, event):
        """Handle resize events"""
        if event.widget == self.parent:
            # Update column widths based on new size
            total_width = event.width
            self.items_tree.column('description', width=int(total_width * 0.4))
            self.items_tree.column('quantity', width=int(total_width * 0.2))
            self.items_tree.column('price', width=int(total_width * 0.2))
            self.items_tree.column('total', width=int(total_width * 0.2))
            
    def remove_selected_item(self, event=None):
        """Remove the selected item from the tree"""
        selection = self.items_tree.selection()
        if not selection:
            return
            
        # Remove selected items
        for item in selection:
            self.items_tree.delete(item)
            
        # Update total
        self.update_total()
        
    def update_total(self):
        """Update the total amount"""
        total = Decimal('0')
        
        # Sum all item totals
        for item in self.items_tree.get_children():
            values = self.items_tree.item(item)['values']
            # Extract the numeric value from the total column (format: "€ XX.XX")
            total += Decimal(values[3].replace('€', '').strip())
            
        # Update total label
        self.total_label.configure(text=f"Totale: € {total:.2f}")
        
    def add_item(self):
        """Add a new item to the table"""
        try:
            description = self.description_var.get().strip()
            quantity = Decimal(self.quantity_var.get() or '0')
            price = Decimal(self.price_var.get() or '0')
            
            if not description:
                CustomMessageBox.showerror("Errore", "Descrizione mancante")
                return
                
            if quantity <= 0:
                CustomMessageBox.showerror("Errore", "Quantità deve essere maggiore di zero")
                return
                
            if price < 0:
                CustomMessageBox.showerror("Errore", "Prezzo non può essere negativo")
                return
                
            # Calculate total
            total = quantity * price
            
            # Add to tree
            self.items_tree.insert('', 'end', values=(
                description,
                f"{quantity:.2f}",
                f"€ {price:.2f}",
                f"€ {total:.2f}"
            ))
            
            # Clear entry fields
            self.description_var.set('')
            self.quantity_var.set('')
            self.price_var.set('')
            
            # Update total
            self.update_total()
            
            # Focus back to description
            self.description_entry.focus()
            
        except (ValueError, InvalidOperation):
            CustomMessageBox.showerror(
                "Errore",
                "Inserisci valori numerici validi per quantità e prezzo"
            )
            
    def clear(self):
        """Clear all form fields"""
        for field in self.customer_fields.values():
            field.delete(0, tk.END)
        self.customer_fields['date'].insert(0, format_date_display(datetime.now()))
        
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        self.description_var.set('')
        self.quantity_var.set('')
        self.price_var.set('')
        self.notes_text.delete('1.0', tk.END)
        self.update_total()
        
    def set_next_invoice_number(self):
        """Set the next invoice number"""
        next_number = self.counter_manager.get_next_counter()
        self.customer_fields['invoice_number'].delete(0, tk.END)
        self.customer_fields['invoice_number'].insert(0, f"RICEVUTA #{next_number}")
        
    def validate(self) -> bool:
        """Validate form data"""
        if not self.customer_fields['invoice_number'].get().strip():
            CustomMessageBox.showerror("Errore", "Numero ricevuta mancante")
            return False
            
        if not self.items_tree.get_children():
            CustomMessageBox.showerror("Errore", "Nessun articolo inserito")
            return False
            
        return True
        
    def get_invoice_data(self) -> Optional[Invoice]:
        """Get invoice data from form"""
        if not self.validate():
            return None
            
        try:
            # Get items
            items = []
            for item in self.items_tree.get_children():
                values = self.items_tree.item(item)['values']
                items.append(InvoiceItem(
                    description=values[0],
                    quantity=Decimal(values[1]),
                    price=Decimal(values[2].replace('€', '').strip()),
                    total=Decimal(values[3].replace('€', '').strip())
                ))
            
            # Parse date using utility function
            try:
                invoice_date = parse_date(self.customer_fields['date'].get().strip())
            except ValueError as e:
                CustomMessageBox.showerror("Errore", str(e))
                return None
            
            # Create invoice
            return Invoice(
                invoice_number=self.customer_fields['invoice_number'].get().strip(),
                date=invoice_date,
                customer_name=self.customer_fields['customer_name'].get().strip() or None,
                customer_vat=self.customer_fields['customer_vat'].get().strip() or None,
                customer_sdi=self.customer_fields['customer_sdi'].get().strip() or None,
                customer_street=self.customer_fields['customer_street'].get().strip() or None,
                customer_email=self.customer_fields['customer_email'].get().strip() or None,
                items=items,
                notes=self.notes_text.get('1.0', tk.END).strip() or None
            )
            
        except (ValueError, InvalidOperation) as e:
            CustomMessageBox.showerror("Errore", f"Errore nei dati: {str(e)}")
            return None
            
    def load_invoice(self, invoice: Invoice):
        """Load invoice data into form"""
        # Clear current data
        self.clear()
        
        # Set invoice data
        self.customer_fields['invoice_number'].insert(0, invoice.invoice_number)
        self.customer_fields['date'].insert(0, format_date_display(invoice.date))
        
        if invoice.customer_name:
            self.customer_fields['customer_name'].insert(0, invoice.customer_name)
        if invoice.customer_vat:
            self.customer_fields['customer_vat'].insert(0, invoice.customer_vat)
        if invoice.customer_sdi:
            self.customer_fields['customer_sdi'].insert(0, invoice.customer_sdi)
        if invoice.customer_street:
            self.customer_fields['customer_street'].insert(0, invoice.customer_street)
        if invoice.customer_email:
            self.customer_fields['customer_email'].insert(0, invoice.customer_email)
            
        # Add items
        for item in invoice.items:
            self.items_tree.insert('', 'end', values=(
                item.description,
                f"{item.quantity:.2f}",
                f"€ {item.price:.2f}",
                f"€ {item.total:.2f}"
            ))
            
        # Set notes
        if invoice.notes:
            self.notes_text.insert('1.0', invoice.notes)
            
        # Update total
        self.update_total()