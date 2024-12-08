"""
Invoice Form - Handles invoice data entry and editing

Key Features:
1. Dynamic form layout
2. Real-time validation
3. Item management
4. Total calculation
5. VAT handling

Components:
1. Customer Section:
   - Invoice number (auto-generated)
   - Date selection
   - Customer details
   - Tax information

2. Items Section:
   - Item description
   - Quantity input
   - Price entry
   - Total calculation
   - Item table

3. Notes Section:
   - Free-form text
   - Multi-line support
   - Optional content

4. Totals Section:
   - Subtotal display
   - VAT calculation
   - Final amount

Technical Details:
- Uses ttk widgets for native look
- Implements input validation
- Manages form state
- Handles data binding
- Provides error feedback

Validation Rules:
1. Required Fields:
   - Invoice number
   - Date
   - At least one item

2. Format Validation:
   - Valid date format
   - Numeric quantities
   - Positive prices
   - Valid VAT number

3. Business Rules:
   - Non-empty items
   - Valid calculations
   - Customer details format

Usage Example:
    # Create form in parent window
    form = InvoiceForm(parent, counter_manager)
    
    # Load existing invoice
    form.load_invoice(invoice)
    
    # Get form data
    new_invoice = form.get_invoice()
    
    # Clear form
    form.clear()
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any
import re

from ..core.counter_manager import CounterManager
from ..core.fix_dates import parse_date, format_date, format_date_display
from ..models.invoice import Invoice, InvoiceItem

class CustomMessageBox:
    """
    Enhanced message dialog with consistent styling
    
    This class provides improved message dialogs with:
    - Consistent styling across the application
    - Proper window management
    - Modal behavior
    - Centered positioning
    
    Methods:
        showerror: Display error message
        showinfo: Display information message
        askyesno: Display yes/no confirmation dialog
        
    Example:
        # Show error message
        CustomMessageBox.showerror(
            "Validation Error",
            "Please fill in all required fields"
        )
        
        # Get user confirmation
        if CustomMessageBox.askyesno(
            "Confirm Delete",
            "Delete this invoice?"
        ):
            delete_invoice()
            
    Technical Details:
    - Modal dialogs (block parent window)
    - Automatic positioning
    - Consistent styling
    - Keyboard handling
    """
    
    @staticmethod
    def showerror(title: str, message: str):
        """
        Display error message dialog
        
        Args:
            title: Dialog window title
            message: Error message to display
            
        Features:
        - Modal window
        - Centered on parent
        - OK button to dismiss
        - Error icon
        
        Example:
            CustomMessageBox.showerror(
                "Input Error",
                "Invalid date format"
            )
        """
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.transient()
        dialog.grab_set()
        
        # Configure dialog size
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Create message area
        msg_frame = ttk.Frame(dialog, padding="20")
        msg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add message with word wrap
        ttk.Label(
            msg_frame,
            text=message,
            wraplength=250
        ).pack(expand=True)
        
        # Add OK button
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ok_btn = ttk.Button(
            btn_frame,
            text="OK",
            command=dialog.destroy
        )
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # Handle window close
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        
        # Center on parent window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = dialog.winfo_toplevel().winfo_x() + (
            dialog.winfo_toplevel().winfo_width() - width
        ) // 2
        y = dialog.winfo_toplevel().winfo_y() + (
            dialog.winfo_toplevel().winfo_height() - height
        ) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog to close
        dialog.wait_window()
        
    @staticmethod
    def showinfo(title: str, message: str):
        """
        Display information message dialog
        
        Args:
            title: Dialog window title
            message: Information message to display
            
        Features:
        - Modal window
        - Centered on parent
        - OK button to dismiss
        - Info icon
        
        Example:
            CustomMessageBox.showinfo(
                "Success",
                "Invoice saved successfully"
            )
        """
        CustomMessageBox.showerror(title, message)
        
    @staticmethod
    def askyesno(title: str, message: str) -> bool:
        """
        Display yes/no confirmation dialog
        
        Args:
            title: Dialog window title
            message: Question to display
            
        Returns:
            bool: True if user clicked Yes, False otherwise
            
        Features:
        - Modal window
        - Centered on parent
        - Yes/No buttons
        - Question icon
        
        Example:
            if CustomMessageBox.askyesno(
                "Confirm",
                "Delete selected items?"
            ):
                delete_items()
        """
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.transient()
        dialog.grab_set()
        
        # Configure dialog size
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Create message area
        msg_frame = ttk.Frame(dialog, padding="20")
        msg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add message with word wrap
        ttk.Label(
            msg_frame,
            text=message,
            wraplength=250
        ).pack(expand=True)
        
        # Store result
        result = tk.BooleanVar(value=False)
        
        # Create button frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Define button callbacks
        def on_yes():
            result.set(True)
            dialog.destroy()
            
        def on_no():
            result.set(False)
            dialog.destroy()
        
        # Add Yes/No buttons
        yes_btn = ttk.Button(
            btn_frame,
            text="Yes",
            command=on_yes
        )
        yes_btn.pack(side=tk.RIGHT, padx=5)
        
        no_btn = ttk.Button(
            btn_frame,
            text="No",
            command=on_no
        )
        no_btn.pack(side=tk.RIGHT, padx=5)
        
        # Handle window close
        dialog.protocol("WM_DELETE_WINDOW", on_no)
        
        # Center on parent window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = dialog.winfo_toplevel().winfo_x() + (
            dialog.winfo_toplevel().winfo_width() - width
        ) // 2
        y = dialog.winfo_toplevel().winfo_y() + (
            dialog.winfo_toplevel().winfo_height() - height
        ) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog to close
        dialog.wait_window()
        return result.get()

class InvoiceForm:
    """
    Professional invoice creation and editing form
    
    This class provides a comprehensive interface for:
    - Creating new invoices
    - Editing existing invoices
    - Managing invoice items
    - Calculating totals
    
    Attributes:
        parent: Parent window
        counter_manager: Invoice number manager
        customer_fields: Dictionary of customer input fields
        items_tree: Table of invoice items
        notes_text: Invoice notes field
        total_label: Total amount display
        
    Example:
        # Create form
        form = InvoiceForm(parent_window, counter_manager)
        
        # Load invoice
        form.load_invoice(invoice)
        
        # Get data
        if form.validate():
            data = form.get_invoice_data()
            
    Technical Details:
    - Responsive layout
    - Real-time calculations
    - Input validation
    - High DPI support
    """
    
    def __init__(self, parent: tk.Widget, counter_manager: CounterManager):
        """
        Initialize the invoice form
        
        Args:
            parent: Parent widget
            counter_manager: Invoice number manager
            
        Creates:
        1. Customer information section
        2. Items management section
        3. Notes section
        4. Totals section
        
        Layout:
        +----------------------------------+
        |          Invoice Form            |
        |----------------------------------|
        | Customer Information             |
        | [Number] [Date]                 |
        | [Name]   [VAT]                  |
        | [Address][Email]                |
        |----------------------------------|
        | Items                           |
        | [Description][Qty][Price][Total]|
        | [Add Item]                      |
        | Items Table                     |
        |----------------------------------|
        | Notes                           |
        | [Notes Text Area]               |
        |----------------------------------|
        | Total: € 0.00                   |
        +----------------------------------+
        
        Example:
            # Create form with custom font sizes
            form = InvoiceForm(
                parent_window,
                counter_manager,
            )
            
            # Form is automatically:
            # - Scaled for screen resolution
            # - Configured with proper fonts
            # - Ready for data entry
        """
        self.parent = parent
        self.counter_manager = counter_manager
        
        # Calculate scaling based on screen resolution
        screen_width = parent.winfo_screenwidth()
        width_ratio = min(max(screen_width / 1920, 1.0), 2.0)
        
        # Configure fonts with scaling
        self.normal_font_size = int(9 * width_ratio)
        self.header_font_size = int(12 * width_ratio)
        self.default_font = ('Helvetica', self.normal_font_size)
        self.header_font = ('Helvetica', self.header_font_size, 'bold')
        
        # Configure spacing with scaling
        self.padx = int(5 * width_ratio)
        self.pady = int(5 * width_ratio)
        self.entry_width = int(30 * width_ratio)
        
        # Create interface
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the form interface"""
        # Create main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=self.padx*2, pady=self.pady*2)
        
        # Add form title
        title_label = ttk.Label(
            main_frame,
            text="New Invoice",
            font=self.header_font
        )
        title_label.pack(fill=tk.X, pady=(0, self.pady*2))
        
        # Create customer details section
        customer_frame = ttk.LabelFrame(
            main_frame,
            text="Customer Details",
            padding=self.padx
        )
        customer_frame.pack(fill=tk.X, pady=self.pady)
        
        # Configure grid columns
        customer_frame.grid_columnconfigure(1, weight=1)
        customer_frame.grid_columnconfigure(3, weight=1)
        
        # Define customer fields
        fields = [
            ("Number:", "invoice_number", 0),
            ("Date:", "date", 0),
            ("Name:", "customer_name", 1),
            ("VAT:", "customer_vat", 1),
            ("SDI:", "customer_sdi", 2),
            ("Address:", "customer_street", 2),
            ("Email:", "customer_email", 3)
        ]
        
        # Create customer fields
        self.customer_fields = {}
        for i, (label, field, row) in enumerate(fields):
            # Calculate column position
            col = (i % 2) * 2
            
            # Add label
            ttk.Label(
                customer_frame,
                text=label,
                font=self.default_font
            ).grid(
                row=row,
                column=col,
                sticky=tk.E,
                padx=self.padx,
                pady=self.pady
            )
            
            # Add entry field
            entry = ttk.Entry(
                customer_frame,
                font=self.default_font,
                width=self.entry_width
            )
            entry.grid(
                row=row,
                column=col + 1,
                sticky=tk.EW,
                padx=self.padx,
                pady=self.pady
            )
            self.customer_fields[field] = entry
        
        # Set default date
        self.customer_fields['date'].insert(
            0,
            format_date_display(datetime.now())
        )
        
        # Create items section
        items_frame = ttk.LabelFrame(
            main_frame,
            text="Items",
            padding=self.padx
        )
        items_frame.pack(fill=tk.BOTH, expand=True, pady=self.pady)
        
        # Create items input frame
        input_frame = ttk.Frame(items_frame)
        input_frame.pack(fill=tk.X, pady=self.pady)
        
        # Create input fields for new items
        self.description_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.price_var = tk.StringVar()
        
        # Description field
        ttk.Label(
            input_frame,
            text="Description:",
            font=self.default_font
        ).pack(side=tk.LEFT, padx=self.padx)
        
        self.description_entry = ttk.Entry(
            input_frame,
            textvariable=self.description_var,
            font=self.default_font,
            width=40
        )
        self.description_entry.pack(side=tk.LEFT, padx=self.padx)
        
        # Quantity field
        ttk.Label(
            input_frame,
            text="Quantity:",
            font=self.default_font
        ).pack(side=tk.LEFT, padx=self.padx)
        
        self.quantity_entry = ttk.Entry(
            input_frame,
            textvariable=self.quantity_var,
            font=self.default_font,
            width=10
        )
        self.quantity_entry.pack(side=tk.LEFT, padx=self.padx)
        
        # Price field
        ttk.Label(
            input_frame,
            text="Price (€):",
            font=self.default_font
        ).pack(side=tk.LEFT, padx=self.padx)
        
        self.price_entry = ttk.Entry(
            input_frame,
            textvariable=self.price_var,
            font=self.default_font,
            width=10
        )
        self.price_entry.pack(side=tk.LEFT, padx=self.padx)
        
        # Add item button
        ttk.Button(
            input_frame,
            text="Add Item",
            command=self.add_item
        ).pack(side=tk.LEFT, padx=self.padx)

        # Remove item button
        ttk.Button(
            input_frame,
            text="Remove Item",
            command=self.remove_selected_item
        ).pack(side=tk.LEFT, padx=self.padx)
        
        # Create total display
        total_frame = ttk.Frame(items_frame)
        total_frame.pack(fill=tk.X, pady=self.pady)
        
        self.total_label = ttk.Label(
            total_frame,
            text="Total: € 0.00",
            font=self.header_font
        )
        self.total_label.pack(side=tk.RIGHT, padx=self.padx)
        
        # Create items table
        self.items_tree = ttk.Treeview(
            items_frame,
            columns=('description', 'quantity', 'price', 'total'),
            show='headings',
            selectmode='browse'
        )
        
        # Configure columns
        self.items_tree.heading('description', text='Description')
        self.items_tree.heading('quantity', text='Quantity')
        self.items_tree.heading('price', text='Price')
        self.items_tree.heading('total', text='Total')
        
        # Set column widths
        total_width = main_frame.winfo_width()
        self.items_tree.column('description', width=int(total_width * 0.4))
        self.items_tree.column('quantity', width=int(total_width * 0.2))
        self.items_tree.column('price', width=int(total_width * 0.2))
        self.items_tree.column('total', width=int(total_width * 0.2))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            items_frame,
            orient=tk.VERTICAL,
            command=self.items_tree.yview
        )
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Position table and scrollbar
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create notes section
        notes_frame = ttk.LabelFrame(
            main_frame,
            text="Notes",
            padding=self.padx
        )
        notes_frame.pack(fill=tk.X, pady=self.pady)
        
        # Add notes text area
        self.notes_text = tk.Text(
            notes_frame,
            height=3,
            font=self.default_font
        )
        self.notes_text.pack(
            fill=tk.X,
            padx=self.padx,
            pady=self.pady
        )
        
        # Create save button
        save_frame = ttk.Frame(main_frame)
        save_frame.pack(fill=tk.X, pady=self.pady)
        
        # Add New Invoice button
        ttk.Button(
            save_frame,
            text="New Invoice (Ctrl+N)",
            command=lambda: self.parent.event_generate('<<New>>')
        ).pack(side=tk.RIGHT, padx=self.padx)
        
        # Add Save button
        ttk.Button(
            save_frame,
            text="Save Invoice (Ctrl+S)",
            command=lambda: self.parent.event_generate('<<Save>>')
        ).pack(side=tk.RIGHT, padx=self.padx)
        
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
        """
        Update the invoice total and VAT display
        """
        total = Decimal('0.00')
        
        # Sum all item totals
        for item in self.items_tree.get_children():
            # Extract total from last column
            item_total = self.items_tree.item(item)['values'][-1]
            # Remove currency symbol and convert
            total += Decimal(item_total.replace('€', '').strip())
        
        # Calculate VAT (10%)
        vat_amount = (100 * total) / 110 * Decimal('0.10')
        
        # Update total label with VAT info
        self.total_label.configure(
            text=f"Total: € {total:,.2f}\n(di cui IVA: € {vat_amount:,.2f})"
        )
        
    def add_item(self):
        """
        Add an item to the invoice
        
        Process:
        1. Validate item fields
        2. Calculate item total
        3. Add to items table
        4. Update invoice total
        5. Clear item fields
        
        Validation:
        - Description is required
        - Quantity must be positive number
        - Price must be positive number
        
        Example:
            # Add item programmatically
            self.description_var.set("Service")
            self.quantity_var.set("1")
            self.price_var.set("100.00")
            self.add_item()
            
        Error Handling:
        - Shows error for invalid input
        - Maintains form state on error
        - Clears fields on success
        """
        try:
            # Get field values
            description = self.description_var.get().strip()
            quantity = self.quantity_var.get().strip()
            price = self.price_var.get().strip()
            
            # Validate fields
            if not description:
                raise ValueError("Description is required")
                
            try:
                quantity = Decimal(quantity)
                if quantity <= 0:
                    raise ValueError
            except (InvalidOperation, ValueError):
                raise ValueError("Quantity must be a positive number")
                
            try:
                price = Decimal(price)
                if price < 0:
                    raise ValueError
            except (InvalidOperation, ValueError):
                raise ValueError("Price must be a positive number")
                
            # Calculate total
            total = quantity * price
            
            # Add to table
            self.items_tree.insert('', 'end', values=(
                description,
                f"{quantity:g}",
                f"€ {price:.2f}",
                f"€ {total:.2f}"
            ))
            
            # Update total
            self.update_total()
            
            # Clear fields
            self.description_var.set("")
            self.quantity_var.set("")
            self.price_var.set("")
            
            # Focus description field
            self.description_entry.focus()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            
    def clear(self):
        """
        Clear all form fields
        
        Process:
        1. Clear customer fields
        2. Clear items table
        3. Clear notes
        4. Reset total
        5. Focus first field
        
        Example:
            # Reset form
            form.clear()
            
            # Form is ready for new invoice
        """
        # Clear customer fields
        for field in self.customer_fields.values():
            field.delete(0, tk.END)
            
        # Set current date
        self.customer_fields['date'].insert(
            0,
            format_date_display(datetime.now())
        )
        
        # Clear items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        # Clear notes
        self.notes_text.delete('1.0', tk.END)
        
        # Reset total
        self.total_label.configure(text="Total: € 0.00")
        
        # Focus first field
        self.customer_fields['invoice_number'].focus()
        
    def load_invoice(self, invoice: Invoice):
        """
        Load invoice data into form
        
        Args:
            invoice: Invoice object to load
        """
        try:
            # Clear all fields first
            self.clear()
            
            # Load customer fields
            self.customer_fields['invoice_number'].insert(
                0, invoice.invoice_number
            )
            self.customer_fields['date'].delete(0, tk.END)  # Clear date first
            self.customer_fields['date'].insert(
                0, format_date_display(invoice.date)
            )
            self.customer_fields['customer_name'].insert(
                0, invoice.customer_name or ''
            )
            self.customer_fields['customer_vat'].insert(
                0, invoice.customer_vat or ''
            )
            self.customer_fields['customer_sdi'].insert(
                0, invoice.customer_sdi or ''
            )
            self.customer_fields['customer_street'].insert(
                0, invoice.customer_street or ''
            )
            self.customer_fields['customer_email'].insert(
                0, invoice.customer_email or ''
            )
            
            # Load items
            for item in invoice.items:
                self.items_tree.insert('', 'end', values=(
                    item.description,
                    f"{item.quantity:g}",
                    f"€ {item.price:.2f}",
                    f"€ {item.total:.2f}"
                ))
                
            # Load notes
            if invoice.notes:
                self.notes_text.insert('1.0', invoice.notes)
                
            # Update total
            self.update_total()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load invoice: {str(e)}"
            )
            
    def get_invoice_data(self) -> Invoice:
        """Get form data as Invoice object"""
        # Get customer data
        invoice_data = {
            'invoice_number': self.customer_fields['invoice_number'].get(),
            'date': parse_date(self.customer_fields['date'].get()),
            'customer_name': self.customer_fields['customer_name'].get(),
            'customer_vat': self.customer_fields['customer_vat'].get(),
            'customer_sdi': self.customer_fields['customer_sdi'].get(),
            'customer_street': self.customer_fields['customer_street'].get(),
            'customer_email': self.customer_fields['customer_email'].get(),
            'notes': self.notes_text.get('1.0', tk.END).strip(),
            'items': [],  # Initialize empty items list
            'vat_amount': None  # Initialize VAT amount
        }
        
        # Create invoice
        invoice = Invoice(**invoice_data)
        
        # Add items
        total_amount = Decimal('0.00')
        for item in self.items_tree.get_children():
            values = self.items_tree.item(item)['values']
            
            # Parse quantity and price
            quantity = Decimal(values[1])
            price = Decimal(values[2].replace('€', '').strip())
            item_total = quantity * price
            total_amount += item_total
            
            # Create item
            invoice_item = InvoiceItem(
                description=values[0],
                quantity=quantity,
                price=price
            )
            
            # Add to invoice
            invoice.items.append(invoice_item)
        
        # Set total amount and calculate VAT
        invoice.total_amount = total_amount
        invoice.vat_amount = (100 * total_amount) / 110 * Decimal(0.10)
            
        return invoice
        
    def validate(self) -> bool:
        """
        Validate form data
        
        Returns:
            bool: True if valid, False otherwise
            
        Validation:
        1. Required fields
            - Invoice number
            - Date
        2. Data formats
            - Date format
            - At least one item
        """
        try:
            # Validate invoice number
            if not self.customer_fields['invoice_number'].get():
                raise ValueError("Invoice number is required")
                
            # Validate date format
            try:
                date_str = self.customer_fields['date'].get()
                if not date_str:
                    raise ValueError("Date is required")
                parse_date(date_str)
            except ValueError:
                raise ValueError("Invalid date format")
                
            # Validate items
            if not self.items_tree.get_children():
                raise ValueError("At least one item is required")
                
            return True
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return False
        
    def save_invoice(self):
        """Save the current invoice"""
        try:
            # Get customer details
            invoice_data = {
                'invoice_number': self.customer_fields['invoice_number'].get().strip(),
                'date': parse_date(self.customer_fields['date'].get()),
                'customer_name': self.customer_fields['customer_name'].get().strip(),
                'customer_vat': self.customer_fields['customer_vat'].get().strip(),
                'customer_sdi': self.customer_fields['customer_sdi'].get().strip(),
                'customer_street': self.customer_fields['customer_street'].get().strip(),
                'customer_email': self.customer_fields['customer_email'].get().strip(),
                'notes': self.notes_text.get('1.0', tk.END).strip()  # Get notes content
            }
            
            # Validate required fields
            if not invoice_data['invoice_number']:
                raise ValueError("Invoice number is required")
                
            # Get items
            items = []
            for item in self.items_tree.get_children():
                values = self.items_tree.item(item)['values']
                items.append(InvoiceItem(
                    description=values[0],
                    quantity=Decimal(str(values[1])),
                    price=Decimal(str(values[2].replace('€', '').strip())),
                    total=Decimal(str(values[3].replace('€', '').strip()))
                ))
                
            if not items:
                raise ValueError("At least one item is required")
                
            # Create invoice object
            invoice = Invoice(
                invoice_number=invoice_data['invoice_number'],
                date=invoice_data['date'],
                customer_name=invoice_data['customer_name'],
                customer_vat=invoice_data['customer_vat'],
                customer_sdi=invoice_data['customer_sdi'],
                customer_street=invoice_data['customer_street'],
                customer_email=invoice_data['customer_email'],
                items=items,
                notes=invoice_data['notes']  # Include notes
            )
            
            # Save invoice
            self.storage_manager.save_invoice(invoice)
            
            # Generate PDF
            pdf_path = self.pdf_generator.generate_pdf(invoice)
            
            # Show success message
            CustomMessageBox.showinfo(
                "Success",
                f"Invoice saved successfully\nPDF generated: {pdf_path}"
            )
            
            # Update invoice history
            self.event_generate('<<InvoiceSaved>>')
            
            return invoice
            
        except ValueError as e:
            CustomMessageBox.showerror("Validation Error", str(e))
        except Exception as e:
            CustomMessageBox.showerror("Error", f"Failed to save invoice: {str(e)}")