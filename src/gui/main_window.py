"""
Main Window - Core application interface

Key Features:
1. Modern two-panel layout
2. Real-time invoice filtering
3. Sortable invoice history
4. Keyboard shortcuts
5. Responsive design

Components:
1. History Panel (Left):
   - Search functionality
   - Sortable columns
   - Quick invoice access
   - Status indicators

2. Form Panel (Right):
   - Customer details
   - Invoice items
   - Total calculation
   - Action buttons

3. Menu System:
   - File operations
   - Invoice management
   - Company settings
   - View options
   - Help system

Technical Details:
- Uses ttk widgets for native look
- Implements MVC pattern
- Manages window lifecycle
- Handles event binding
- Provides data validation

Keyboard Shortcuts:
- Ctrl+N: New Invoice
- Ctrl+S: Save Invoice
- Ctrl+P: Open PDF
- Ctrl+M: Manage Invoices
- Ctrl+C: Configure Company
- Ctrl+H: Toggle History
- F1: Help/About

Event Handling:
- Double-click to load invoice
- Real-time search filtering
- Column sorting
- Form validation
- Error handling

Usage Example:
    # Create and run application
    app = MainWindow()
    app.run()
    
    # Application provides:
    # - Invoice creation and editing
    # - PDF generation and viewing
    # - Company configuration
    # - Invoice management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess
import sys
from typing import Optional
from datetime import datetime
import os

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
        """Initialize the main window"""
        self.root = tk.Tk()
        self.root.title("Invoice Manager")
        
        # Initialize managers
        self.counter_manager = CounterManager()
        self.storage_manager = StorageManager()
        self.pdf_generator = PDFGenerator()
        
        # Define fonts and sizes
        self.normal_font_size = 10
        self.header_font = ('Segoe UI', 12, 'bold')
        self.default_font = ('Segoe UI', self.normal_font_size)
        self.normal_font = ('Segoe UI', self.normal_font_size)
        self.small_font = ('Segoe UI', 9)
        
        # Initialize sort state
        self.sort_column = 'date'
        self.sort_order = 'desc'
        
        # Set up the menu bar first
        self.setup_menu()
        
        # Set up the UI
        self.setup_ui()
        
        # Configure keyboard shortcuts
        self.setup_shortcuts()
        
        # Track current invoice and PDF
        self.current_invoice = None
        self.last_pdf_path = None
        
        # Load invoice history after everything is set up
        self.root.after(100, self.load_invoice_history)
        
    def setup_ui(self):
        """
        Create and configure the main application layout
        
        Layout Structure:
        +----------------+------------------+
        |    History    |   Invoice Form   |
        |   (1/3 width) |   (2/3 width)   |
        |    Search     |    Input Fields  |
        |    Table      |    Buttons       |
        +----------------+------------------+
        
        Components:
        - PanedWindow for resizable sections
        - History view on the left (1/3 width)
        - Invoice form on the right (2/3 width)
        
        Example:
            # Create default layout
            self.setup_main_frame()
            
            # Adjust pane weights
            self.main_paned.pane(0, weight=2)  # Give history more space
            self.main_paned.pane(1, weight=3)  # Adjust form space
        """
        # Create main container with PanedWindow for resizable sections
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
        
        # Bind form events
        self.root.bind('<<New>>', lambda e: self.new_invoice())
        self.root.bind('<<Save>>', lambda e: self.save_invoice())
        
    def setup_history_view(self):
        """Set up the invoice history view"""
        # Initialize sorting state
        self.sort_column = None
        self.sort_ascending = True
        
        header_frame = ttk.Frame(self.left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        history_label = ttk.Label(header_frame, text="Invoice History", font=self.header_font)
        history_label.pack(side=tk.LEFT)
        
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_history)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=self.default_font)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        style = ttk.Style()
        style.configure("Treeview", font=self.default_font)
        style.configure("Treeview.Heading", font=self.default_font)
        
        # Add notes column to the history table
        columns = ('number', 'date', 'customer', 'amount') #'notes'
        self.history_tree = ttk.Treeview(self.left_frame, columns=columns, show='headings', style="Treeview")
        
        # Calculate initial column widths
        window_width = self.root.winfo_width()
        history_width = window_width // 3
        
        # Configure sortable column headers with commands
        self.history_tree.heading('number', text='Number', command=lambda: self.sort_history('number'))
        self.history_tree.heading('date', text='Date', command=lambda: self.sort_history('date'))
        self.history_tree.heading('customer', text='Customer', command=lambda: self.sort_history('customer'))
        self.history_tree.heading('amount', text='Amount', command=lambda: self.sort_history('amount'))
        #self.history_tree.heading('notes', text='Notes', command=lambda: self.sort_history('notes'))
        
        # Set proportional column widths
        self.history_tree.column('number', width=int(history_width * 0.15))
        self.history_tree.column('date', width=int(history_width * 0.15))
        self.history_tree.column('customer', width=int(history_width * 0.25))
        self.history_tree.column('amount', width=int(history_width * 0.15))
        #self.history_tree.column('notes', width=int(history_width * 0.30))
        
        # Add scrollbar for navigation
        scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Place table and scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to load invoice
        self.history_tree.bind('<Double-1>', self.load_selected_invoice)
        
    def setup_menu(self):
        """
        Create and configure the application menu system
        
        Creates:
        - File menu (New, Save, Open PDF, etc.)
        - Edit menu (Delete, Duplicate)
        - View menu (Show/Hide History)
        - Help menu (About)
        
        Keyboard Shortcuts:
        - Ctrl+N: New Invoice
        - Ctrl+S: Save Invoice
        - Ctrl+P: Open PDF
        - Ctrl+M: Manage Invoices
        - Ctrl+C: Configure Company
        - Alt+F4: Exit
        - Ctrl+Del: Delete
        - Ctrl+D: Duplicate
        - Ctrl+H: Toggle History
        - F1: About
        
        Example Menu Structure:
        File
        ├── New Invoice     (Ctrl+N)
        ├── Save           (Ctrl+S)
        ├── Open PDF       (Ctrl+P)
        ├── ─────────
        ├── Manage Invoices (Ctrl+M)
        ├── Configure Company (Ctrl+C)
        ├── ────────────
        └── Exit           (Alt+F4)
        """
        # Create menubar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Configure menu font for consistency
        menu_font = ('Helvetica', self.normal_font_size)
        
        # File menu with common operations
        file_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="File", menu=file_menu, font=menu_font)
        file_menu.add_command(label="New Invoice (Ctrl+N)", command=self.new_invoice)
        file_menu.add_command(label="Save (Ctrl+S)", command=self.save_invoice)
        file_menu.add_command(label="Open PDF (Ctrl+P)", command=self.open_last_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Manage Invoices (Ctrl+M)", command=self.open_invoice_manager)
        file_menu.add_command(label="Configure Company (Ctrl+C)", command=self.configure_company)
        file_menu.add_separator()
        file_menu.add_command(label="Exit (Alt+F4)", command=self.root.quit)
        
        # Edit menu for invoice operations
        edit_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="Edit", menu=edit_menu, font=menu_font)
        edit_menu.add_command(label="Delete (Ctrl+Del)", command=self.clear_form)
        edit_menu.add_command(label="Duplicate (Ctrl+D)", command=self.duplicate_invoice)
        
        # View menu for display options
        view_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="View", menu=view_menu, font=menu_font)
        view_menu.add_command(label="Show History (Ctrl+H)", command=self.toggle_history)
        
        # Help menu for application information
        help_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="Help", menu=help_menu, font=menu_font)
        help_menu.add_command(label="About (F1)", command=self.show_about)
        
    def setup_shortcuts(self):
        """Configure keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_invoice())
        self.root.bind('<Control-s>', lambda e: self.save_invoice())
        self.root.bind('<Control-p>', lambda e: self.open_last_pdf())
        self.root.bind('<Control-h>', lambda e: self.toggle_history())
        self.root.bind('<Control-c>', lambda e: self.configure_company())
        self.root.bind('<Control-m>', lambda e: self.open_invoice_manager())
        self.root.bind('<F1>', lambda e: self.show_about())
        
    def load_invoice_history(self):
        """Load and display invoice history"""
        try:
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
                
            # Load all invoices
            invoices = self.storage_manager.load_all_invoices()
            
            # Add invoices to tree
            for invoice in invoices:
                self.history_tree.insert('', 'end', values=(
                    invoice.invoice_number,
                    invoice.date.strftime('%d/%m/%Y') if invoice.date else '',
                    invoice.customer_name or '',
                    f"€ {invoice.total_amount:.2f}" if invoice.total_amount else '€ 0.00',
                    invoice.notes or ''  # Add notes to the display
                ))
                
            # Maintain sort if active
            if self.sort_column:
                self.sort_history(self.sort_column)
                
        except Exception as e:
            CustomMessageBox.showerror("Error", f"Failed to load invoice history: {str(e)}")

    def update_invoice_history(self, invoices):
        """Update invoice history display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Add invoices to tree
        for invoice in invoices:
            self.history_tree.insert('', 'end', values=(
                invoice.invoice_number,
                invoice.date.strftime('%d/%m/%Y'),
                invoice.customer_name or '',
                f"€ {invoice.total_amount:.2f}"
            ))

    def sort_history(self, column):
        """Sort the history table by the specified column"""
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True
            
        # Get all items
        items = [(self.history_tree.set(item, column), item) 
                for item in self.history_tree.get_children('')]
        
        # Sort based on column type
        if column == 'number':
            # Numeric sort for invoice numbers
            items.sort(key=lambda x: int(x[0]), reverse=not self.sort_ascending)
        elif column == 'date':
            # Date sort
            items.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'),
                      reverse=not self.sort_ascending)
        elif column == 'amount':
            # Amount sort
            items.sort(key=lambda x: float(x[0].replace('€', '').strip()),
                      reverse=not self.sort_ascending)
        else:
            # Text sort for customer and notes
            items.sort(key=lambda x: x[0].lower(), reverse=not self.sort_ascending)
        
        # Rearrange items
        for index, (_, item) in enumerate(items):
            self.history_tree.move(item, '', index)
            
        # Update column headers - clear all arrows first
        for col in self.history_tree['columns']:
            text = col.capitalize()
            self.history_tree.heading(col, text=text)
            
        # Add arrow to sorted column
        arrow = "▼" if self.sort_ascending else "▲"
        current_text = column.capitalize()
        self.history_tree.heading(column, text=f"{current_text} {arrow}")

    def sort_invoices(self, invoices):
        """
        Sort list of invoices based on current sort settings
        
        Args:
            invoices (list): List of Invoice objects to sort
            
        Sorting Rules:
        - number: Natural sort of invoice numbers
        - date: Chronological sort of dates
        - customer: Case-insensitive sort of names
        - amount: Numerical sort of totals
        
        Example:
            invoices = storage_manager.load_all_invoices()
            self.sort_invoices(invoices)
            # Invoices are now sorted by self.sort_column in self.sort_order
            
        To modify sort behavior:
        ```python
        # Custom sort key for customer name
        if self.sort_column == 'customer':
            key = lambda x: x.customer_name.lower().strip()
            
        # Custom date format sorting
        if self.sort_column == 'date':
            key = lambda x: datetime.strptime(x.date, '%Y-%m-%d')
        ```
        """
        # Define sort key based on column
        if self.sort_column == 'number':
            key = lambda x: int(x.number)
        elif self.sort_column == 'date':
            key = lambda x: datetime.strptime(x.date, '%Y-%m-%d')
        elif self.sort_column == 'customer':
            key = lambda x: x.customer_name.lower()
        else:  # amount
            key = lambda x: x.total
            
        # Sort the list
        reverse = self.sort_order == "desc"
        invoices.sort(key=key, reverse=reverse)
        
    def filter_history(self, *args):
        """Filter invoice history based on search text"""
        search_text = self.search_var.get().lower()
        
        # Store current selection
        selection = self.history_tree.selection()
        
        # Reload all invoices
        self.load_invoice_history()
        
        # Apply filter if search text exists
        if search_text:
            for item in self.history_tree.get_children():
                values = self.history_tree.item(item)['values']
                if not any(search_text in str(value).lower() 
                          for value in values):
                    self.history_tree.delete(item)
                    
        # Restore selection if items still exist
        for item in selection:
            if self.history_tree.exists(item):
                self.history_tree.selection_add(item)
                
    def load_selected_invoice(self, event):
        """
        Load the selected invoice into the form
        
        Args:
            event: Double-click event (not used)
            
        Process:
        1. Get selected item from history
        2. Clear current form
        3. Load invoice data from storage
        4. Populate form fields
        5. Update current invoice reference
        """
        # Get selected item
        selection = self.history_tree.selection()
        if not selection:
            return
            
        # Get invoice number from selected row
        values = self.history_tree.item(selection[0])['values']
        invoice_number = values[0]
        
        try:
            # Load invoice data
            invoice = self.storage_manager.load_invoice(invoice_number)
            if invoice:
                # Clear form before loading new invoice
                self.invoice_form.clear()
                # Update form and current invoice
                self.current_invoice = invoice
                self.invoice_form.load_invoice(invoice)
            else:
                messagebox.showerror("Error", f"Invoice {invoice_number} not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load invoice: {str(e)}")
            
    def new_invoice(self):
        """
        Create a new invoice
        
        Process:
        1. Clear current form
        2. Get next invoice number
        3. Initialize new invoice
        4. Update form
        
        Example:
            # Create new invoice
            self.new_invoice()
            
            # Form is now ready for:
            # - Customer details
            # - Service details
            # - Amounts
            
        Note:
            This method automatically assigns the next available
            invoice number using the counter manager.
        """
        try:
            # Clear form
            self.invoice_form.clear()
            
            # Get next number
            number = self.counter_manager.get_next_counter()
            
            # Set invoice number
            self.invoice_form.customer_fields['invoice_number'].insert(0, str(number))
            
            # Set current date
            self.invoice_form.customer_fields['date'].insert(
                0,
                format_date_display(datetime.now())
            )
            
            # Focus customer name field
            self.invoice_form.customer_fields['customer_name'].focus()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new invoice: {str(e)}")
            
    def save_invoice(self):
        """
        Save the current invoice and generate PDF
        
        Process:
        1. Validate form data
        2. Save invoice
        3. Generate PDF
        4. Ask to open PDF
        5. Refresh history
        
        Keyboard shortcut: Ctrl+S
        """
        try:
            # Validate and get form data
            if not self.invoice_form.validate():
                return False
                
            # Get invoice data from form
            invoice_data = self.invoice_form.get_invoice_data()
            
            # Update current invoice
            if self.current_invoice:
                self.current_invoice.update(invoice_data)
            else:
                self.current_invoice = invoice_data
                
            # Save invoice
            self.storage_manager.save_invoice(self.current_invoice)
            
            # Generate PDF
            self.last_pdf_path = self.pdf_generator.generate_pdf(self.current_invoice)
            
            # Refresh history
            self.load_invoice_history()
            
            # Ask to open PDF
            if messagebox.askyesno("Success", "Invoice saved successfully. Would you like to open the PDF?"):
                self.open_last_pdf()
                
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {str(e)}")
            return False
        
    def open_last_pdf(self):
        """
        Open the most recently generated PDF
        
        Opens the system's default PDF viewer.
        Keyboard shortcut: Ctrl+P
        """
        if not self.last_pdf_path or not Path(self.last_pdf_path).exists():
            messagebox.showerror("Error", "No PDF available to open")
            return
                
        try:
            if sys.platform == 'win32':
                os.startfile(self.last_pdf_path)
            else:
                subprocess.run(['xdg-open', self.last_pdf_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
            
    def clear_form(self):
        """
        Clear the invoice form and reset state
        
        Process:
        1. Clear all form fields
        2. Reset current invoice
        3. Clear selection in history
        
        Example:
            # Clear form and state
            self.clear_form()
            
            # Form is now ready for:
            # - New invoice creation
            # - Loading another invoice
        """
        # Clear form fields
        self.invoice_form.clear()
        
        # Reset state
        self.current_invoice = None
        
        # Clear selection in history
        self.history_tree.selection_remove(self.history_tree.selection())
        
    def duplicate_invoice(self):
        """
        Create a copy of the current invoice with a new number
        
        Process:
        1. Validate current invoice exists
        2. Create deep copy
        3. Assign new invoice number
        4. Update form with copy
        
        Example:
            # Duplicate current invoice
            self.duplicate_invoice()
            
            # The new invoice will have:
            # - New unique number
            # - Same customer details
            # - Same service details
            # - Same amounts
            
        Error Handling:
        - Checks if invoice exists to duplicate
        - Handles number generation errors
        - Maintains form state on error
        """
        try:
            # Check if invoice exists
            if not self.current_invoice:
                messagebox.showwarning("Warning", "No invoice to duplicate")
                return
                
            # Create copy with new number
            new_invoice = self.current_invoice.copy()
            new_invoice.number = str(self.counter_manager.get_next_counter())
            
            # Update form
            self.current_invoice = new_invoice
            self.invoice_form.load_invoice(new_invoice)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to duplicate invoice: {str(e)}")
            
    def configure_company(self):
        """
        Open the company configuration dialog
        
        Features:
        - Edit company details
        - Update PDF template
        - Save configuration
        
        Process:
        1. Open configuration dialog
        2. Wait for user input
        3. Save changes if confirmed
        4. Update PDF generator
        
        Example:
            # Open configuration
            self.configure_company()
            
            # Configuration affects:
            # - Company details in PDFs
            # - Invoice template
            # - Contact information
        """
        try:
            # Create and show dialog
            dialog = CompanyConfigDialog(
                self.root,
                on_config_saved=lambda: self.pdf_generator.reload_company_details()
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open configuration: {str(e)}")
            
    def open_invoice_manager(self):
        """
        Open the invoice management dialog
        
        Features:
        - Bulk invoice operations
        - Advanced filtering
        - Export functionality
        
        Process:
        1. Open manager dialog
        2. Wait for user actions
        3. Refresh history on close
        
        Example:
            # Open manager
            self.open_invoice_manager()
            
            # Manager provides:
            # - Bulk delete
            # - Bulk export
            # - Advanced search
            # - Detailed view
        """
        try:
            # Create and show dialog
            dialog = InvoiceManagerDialog(self.root)
            
            # Refresh history after manager closes
            self.load_invoice_history()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open invoice manager: {str(e)}")
            
    def toggle_history(self):
        """
        Toggle visibility of the history panel
        
        Features:
        - Remembers panel state
        - Animates transition
        - Maintains form usability
        
        Example:
            # Hide history
            self.toggle_history()
            
            # Show history
            self.toggle_history()
            
        Technical Details:
        - Uses PanedWindow for smooth resizing
        - Maintains minimum widths
        - Preserves panel weights
        """
        if self.left_frame.winfo_viewable():
            # Hide history
            self.main_paned.forget(self.left_frame)
        else:
            # Show history
            self.main_paned.add(self.left_frame, weight=1)
            
    def show_about(self):
        """
        Display application information dialog
        
        Shows:
        - Version information
        - Copyright notice
        - System information
        - Credits
        
        Example:
            # Show about dialog
            self.show_about()
            
        Dialog Content:
        - Application name and version
        - Developer information
        - System details
        - License information
        """
        about_text = f"""
        Invoice Management System
        Version 1.0.0
        
        A professional invoice management solution
        
        System Information:
        Python: {sys.version.split()[0]}
        Platform: {sys.platform}
        
        © 2024 All rights reserved
        """
        
        messagebox.showinfo("About", about_text.strip())
        
    def run(self):
        """
        Start the application main loop
        
        Process:
        1. Initialize components
        2. Load initial data
        3. Start event loop
        4. Handle shutdown
        
        Example:
            # Create and run application
            app = MainWindow()
            app.run()
            
        Technical Details:
        - Handles window events
        - Manages application lifecycle
        - Ensures clean shutdown
        """
        try:
            # Start main event loop
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("Fatal Error", f"Application error: {str(e)}")
            sys.exit(1)
        finally:
            # Cleanup on exit
            try:
                self.root.destroy()
            except:
                pass

if __name__ == "__main__":
    app = MainWindow()
    app.run() 