"""
Invoice Manager Dialog
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional
from .invoice_form import CustomMessageBox

class InvoiceManagerDialog:
    """Dialog for managing invoices"""
    
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Gestione Ricevute")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        window_width = 800
        window_height = 600
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.setup_ui()
        
    def delete_invoice(self):
        """Delete selected invoice"""
        selection = self.invoice_tree.selection()
        if not selection:
            CustomMessageBox.showerror(
                "Errore",
                "Seleziona una ricevuta da eliminare"
            )
            return
            
        if CustomMessageBox.askyesno(
            "Conferma",
            "Sei sicuro di voler eliminare questa ricevuta?"
        ):
            # Delete invoice logic here
            pass
            
    def export_invoices(self):
        """Export selected invoices"""
        selection = self.invoice_tree.selection()
        if not selection:
            CustomMessageBox.showerror(
                "Errore",
                "Seleziona le ricevute da esportare"
            )
            return
            
        # Export logic here
        CustomMessageBox.showerror(
            "Successo",
            "Ricevute esportate con successo"
        ) 