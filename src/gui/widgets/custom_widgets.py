"""
Custom Widgets - Reusable GUI components
"""
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Optional

class LabelEntry(ttk.Frame):
    """Label and entry field combination"""
    
    def __init__(self, parent, label: str, width: int = 20):
        super().__init__(parent)
        self.label = ttk.Label(self, text=label)
        self.label.pack(side=tk.LEFT)
        
        self.entry = ttk.Entry(self, width=width)
        self.entry.pack(side=tk.LEFT, padx=(5, 0))
        
    def get(self) -> str:
        """Get entry value"""
        return self.entry.get()
        
    def set(self, value: str):
        """Set entry value"""
        self.entry.delete(0, tk.END)
        if value is not None:
            self.entry.insert(0, str(value))
        
    def clear(self):
        """Clear entry"""
        self.entry.delete(0, tk.END)

class ItemsTable(ttk.Frame):
    """Table for invoice items"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._total = Decimal('0')
        self.create_table()
        
    def create_table(self):
        """Create the items table"""
        columns = ('description', 'quantity', 'price', 'total')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        # Setup columns
        self.tree.heading('description', text='Descrizione')
        self.tree.heading('quantity', text='Quantità')
        self.tree.heading('price', text='Prezzo')
        self.tree.heading('total', text='Totale')
        
        self.tree.column('description', width=300)
        self.tree.column('quantity', width=100)
        self.tree.column('price', width=100)
        self.tree.column('total', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack components
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def add_item(self, description: str, quantity: Decimal, price: Decimal, total: Optional[Decimal] = None):
        """Add a new item to the table"""
        if total is None:
            total = quantity * price
            
        self.tree.insert('', tk.END, values=(
            description,
            f"{quantity:.2f}",
            f"{price:.2f}",
            f"{total:.2f}"
        ))
        
        # Update total
        self._total += total
        self._notify_total_changed()
        
    def delete_selected(self):
        """Delete selected items"""
        selected = self.tree.selection()
        if not selected:
            return
            
        if messagebox.askyesno("Conferma", "Eliminare gli elementi selezionati?"):
            for item_id in selected:
                values = self.tree.item(item_id)['values']
                self._total -= Decimal(str(values[3]))  # Subtract item total
                self.tree.delete(item_id)
            self._notify_total_changed()
            
    def clear(self):
        """Clear all items"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._total = Decimal('0')
        self._notify_total_changed()
        
    def get_items(self) -> List[Dict]:
        """Get all items as list of dictionaries"""
        items = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            quantity = Decimal(str(values[1]))
            price = Decimal(str(values[2]))
            total = Decimal(str(values[3]))
            items.append({
                'description': values[0],
                'quantity': quantity,
                'price': price,
                'total': total
            })
        return items
        
    def _notify_total_changed(self):
        """Notify total change to parent widgets"""
        event = tk.Event()
        event.widget = self
        event.total = self._total
        self.event_generate('<<TotalUpdated>>')
        if self.master:
            self.master.event_generate('<<TotalUpdated>>')
            
    def get_total(self) -> Decimal:
        """Get current total"""
        return self._total

class TotalDisplay(ttk.Frame):
    """Display for invoice total"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._total = Decimal('0')
        self.create_widgets()
        
    def create_widgets(self):
        """Create the total display widgets"""
        style = ttk.Style()
        style.configure('Total.TLabel', font=('Helvetica', 12, 'bold'))
        
        self.total_label = ttk.Label(self, text="Totale:", style='Total.TLabel')
        self.total_label.pack(side=tk.RIGHT, padx=5)
        
        self.total_amount = ttk.Label(self, text="€ 0.00", style='Total.TLabel')
        self.total_amount.pack(side=tk.RIGHT, padx=5)
        
    def update(self, amount: Decimal):
        """Update the displayed total"""
        self._total = amount
        self.total_amount.config(text=f"€ {amount:.2f}")
        
    def get_total(self) -> Decimal:
        """Get current total"""
        return self._total
        