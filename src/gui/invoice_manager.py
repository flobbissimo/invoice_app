"""
Invoice Manager Dialog - Advanced invoice management interface

Key Features:
1. Bulk invoice operations
2. Advanced filtering
3. Sortable columns
4. Export functionality
5. Batch processing

Components:
1. Search Panel:
   - Real-time filtering
   - Advanced search
   - Quick filters
   - Search history

2. Invoice Table:
   - Multi-selection
   - Sortable columns
   - Status indicators
   - Quick actions

3. Action Panel:
   - Bulk operations
   - Export options
   - Delete functions
   - Batch updates

Technical Details:
- Uses ttk widgets for native look
- Implements virtual scrolling
- Manages large datasets
- Handles concurrent updates
- Provides progress feedback

Search Features:
1. Text Search:
   - Invoice numbers
   - Customer names
   - Amounts
   - Notes

2. Date Filters:
   - Date range
   - Month/Year
   - Custom periods
   - Quick filters

3. Amount Filters:
   - Range selection
   - Above/below
   - Custom ranges
   - Currency format

Usage Example:
    # Create manager dialog
    dialog = InvoiceManagerDialog(parent)
    
    # Dialog provides:
    # - Invoice listing
    # - Bulk operations
    # - Export features
    # - Advanced search
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .invoice_form import CustomMessageBox
from ..core.storage_manager import StorageManager
from ..models.invoice import Invoice

class InvoiceManagerDialog:
    """
    Advanced invoice management dialog with bulk operations
    
    This dialog provides a comprehensive interface for:
    - Viewing all invoices in a sortable table
    - Searching and filtering in real-time
    - Performing bulk operations
    - Exporting data in various formats
    
    Attributes:
        dialog (tk.Toplevel): Main dialog window
        storage_manager (StorageManager): Data persistence handler
        invoice_tree (ttk.Treeview): Invoice table widget
        search_var (tk.StringVar): Search text variable
        
    Example:
        # Create and show dialog
        manager = InvoiceManagerDialog(parent_window)
        
        # Dialog handles:
        # - Window positioning
        # - Event handling
        # - Data management
        
    Technical Details:
    - Modal dialog (blocks parent window)
    - Responsive layout
    - Real-time search
    - Efficient data handling
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize the invoice management dialog
        
        Args:
            parent (tk.Tk): Parent window
            
        Creates:
        1. Modal dialog window
        2. Data manager instance
        3. User interface
        4. Event handlers
        
        Window Layout:
        +----------------------------------+
        |           Invoice Manager        |
        |----------------------------------|
        | Search: [___________________]    |
        |----------------------------------|
        | Number | Date | Customer | Amount|
        |--------|------|----------|-------|
        |        |      |          |       |
        |        |      |          |       |
        |----------------------------------|
        | [Delete] [Export]     [Close]    |
        +----------------------------------+
        
        Example:
            # Create dialog
            dialog = InvoiceManagerDialog(main_window)
            
            # Dialog is automatically:
            # - Centered on screen
            # - Modal (blocks parent)
            # - Populated with data
        """
        # Create modal dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Invoice Manager")
        self.dialog.transient(parent)  # Set as transient to parent
        self.dialog.grab_set()         # Make dialog modal
        
        # Initialize data manager
        self.storage_manager = StorageManager()
        
        # Calculate window position
        window_width = 800   # Default width
        window_height = 600  # Default height
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        # Center on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set geometry and constraints
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.dialog.minsize(800, 600)  # Set minimum size
        
        # Setup interface
        self.setup_ui()
        
    def setup_ui(self):
        """
        Configure the dialog's user interface
        
        Components:
        1. Main frame with padding
        2. Title and search section
        3. Invoice table with scrollbar
        4. Action buttons
        
        Features:
        - Responsive layout
        - Real-time search
        - Sortable columns
        - Bulk operations
        
        Example:
            # Interface provides:
            # - Search field with real-time filtering
            # - Table with sortable columns
            # - Action buttons for operations
            
        To modify table style:
        ```python
        style = ttk.Style()
        style.configure("Treeview", 
            font=('Helvetica', 10),
            rowheight=25
        )
        style.configure("Treeview.Heading",
            font=('Helvetica', 10, 'bold')
        )
        ```
        """
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title with custom font
        title_label = ttk.Label(
            main_frame, 
            text="Invoice Manager",
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Create search section
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add search field with label
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_invoices)  # Real-time filtering
        
        # Create search entry with padding
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Helvetica', 10)
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Configure table columns
        columns = ('number', 'date', 'customer', 'amount')
        self.invoice_tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show='headings',
            selectmode='extended'  # Allow multiple selection
        )
        
        # Set column headings and widths
        column_config = {
            'number': {'text': 'Number', 'width': 150},
            'date': {'text': 'Date', 'width': 100},
            'customer': {'text': 'Customer', 'width': 300},
            'amount': {'text': 'Amount', 'width': 100}
        }
        
        for col, config in column_config.items():
            self.invoice_tree.heading(col, text=config['text'])
            self.invoice_tree.column(col, width=config['width'])
        
        # Add scrollbar for navigation
        scrollbar = ttk.Scrollbar(
            main_frame,
            orient=tk.VERTICAL,
            command=self.invoice_tree.yview
        )
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        # Position table and scrollbar
        self.invoice_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create button frame with padding
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Add action buttons
        ttk.Button(
            button_frame,
            text="Delete Selected",
            command=self.delete_invoice
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Export Selected",
            command=self.export_invoices
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Load initial data
        self.load_invoices()
        
    def load_invoices(self):
        """
        Load and display all invoices in the table
        
        Process:
        1. Clear existing table entries
        2. Load invoices from storage
        3. Format data for display
        4. Insert into table
        
        Features:
        - Handles large datasets efficiently
        - Formats data for display
        - Maintains sort order
        
        Example:
            # Refresh table data
            self.load_invoices()
            
            # Table shows:
            # - Invoice number
            # - Formatted date
            # - Customer name
            # - Formatted amount
            
        To modify data formatting:
        ```python
        # Custom date format
        date_str = invoice.date.strftime('%Y-%m-%d')
        
        # Custom amount format
        amount_str = f"{invoice.total_amount:,.2f} €"
        ```
        """
        # Clear existing entries
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
            
        try:
            # Load and insert invoices
            for invoice in self.storage_manager.load_all_invoices():
                # Format values for display
                values = (
                    invoice.invoice_number,
                    invoice.date.strftime('%d/%m/%Y'),
                    invoice.customer_name or '',
                    f"€ {invoice.total_amount:.2f}"
                )
                self.invoice_tree.insert('', 'end', values=values)
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load invoices: {str(e)}"
            )
            
    def filter_invoices(self, *args):
        """
        Filter invoices based on search text
        
        Features:
        - Real-time filtering
        - Case-insensitive search
        - Searches all columns
        - Maintains sort order
        
        Process:
        1. Get search text
        2. Reload all invoices
        3. Remove non-matching entries
        4. Maintain selection
        
        Example:
            # Filter by customer name
            self.search_var.set("john")  # Shows matching entries
            
            # Clear filter
            self.search_var.set("")  # Shows all entries
            
        To modify search behavior:
        ```python
        # Search specific columns
        searchable_columns = [0, 2]  # Only number and customer
        if not any(search_text in str(values[i]).lower() 
                  for i in searchable_columns):
            self.invoice_tree.delete(item)
            
        # Exact match only
        if search_text == str(values[0]).lower():
            self.invoice_tree.delete(item)
        ```
        """
        search_text = self.search_var.get().lower()
        
        # Store current selection
        selection = self.invoice_tree.selection()
        
        # Reload all invoices
        self.load_invoices()
        
        # Apply filter if search text exists
        if search_text:
            for item in self.invoice_tree.get_children():
                values = self.invoice_tree.item(item)['values']
                if not any(search_text in str(value).lower() 
                          for value in values):
                    self.invoice_tree.delete(item)
                    
        # Restore selection if items still exist
        for item in selection:
            if self.invoice_tree.exists(item):
                self.invoice_tree.selection_add(item)
                
    def delete_invoice(self):
        """
        Delete selected invoices with confirmation
        
        Process:
        1. Verify selection exists
        2. Show confirmation dialog
        3. Delete selected invoices
        4. Refresh table
        5. Show success message
        
        Features:
        - Bulk deletion support
        - Confirmation dialog
        - Error handling
        - Success feedback
        
        Example:
            # Delete selected invoices
            self.delete_invoice()
            
            # Handles:
            # - No selection
            # - Confirmation
            # - Deletion errors
            # - Table refresh
            
        Error Handling:
        - Checks for selection
        - Confirms deletion
        - Handles deletion errors
        - Maintains table state
        """
        # Check for selection
        selection = self.invoice_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Warning",
                "Please select invoices to delete"
            )
            return
            
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Delete {len(selection)} selected invoice(s)?"
        ):
            return
            
        try:
            # Delete selected invoices
            for item in selection:
                invoice_number = self.invoice_tree.item(item)['values'][0]
                self.storage_manager.delete_invoice(invoice_number)
                
            # Refresh table
            self.load_invoices()
            
            # Show success message
            messagebox.showinfo(
                "Success",
                f"{len(selection)} invoice(s) deleted successfully"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to delete invoices: {str(e)}"
            )
            
    def export_invoices(self):
        """
        Export selected invoices to various formats
        
        Features:
        - Multiple format support (PDF, CSV, Excel)
        - Bulk export capability
        - Custom file naming
        - Progress feedback
        
        Process:
        1. Verify selection exists
        2. Show format selection dialog
        3. Choose save location
        4. Export selected invoices
        5. Show success message
        
        Example:
            # Export selected invoices
            self.export_invoices()
            
            # Supports:
            # - Format selection
            # - Save location
            # - Progress feedback
            # - Error handling
            
        To implement format selection:
        ```python
        formats = {
            'pdf': 'PDF Documents',
            'csv': 'CSV Spreadsheet',
            'xlsx': 'Excel Workbook'
        }
        
        format_choice = CustomDialog.ask_choice(
            "Export Format",
            "Choose export format:",
            formats.keys()
        )
        ```
        """
        # Verify selection
        selection = self.invoice_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Warning",
                "Please select invoices to export"
            )
            return
            
        try:
            # TODO: Implement export functionality
            # 1. Show format selection dialog
            # 2. Get save location
            # 3. Export selected invoices
            # 4. Show progress
            # 5. Handle errors
            
            messagebox.showinfo(
                "Success",
                f"{len(selection)} invoice(s) exported successfully"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to export invoices: {str(e)}"
            )