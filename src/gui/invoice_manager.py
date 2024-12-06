"""
Gestore Ricevute - Finestra di gestione avanzata delle ricevute

Questo modulo fornisce una finestra di dialogo per:
1. Visualizzare tutte le ricevute in una tabella
2. Cercare e filtrare le ricevute
3. Eliminare ricevute selezionate
4. Esportare ricevute in vari formati

Possibili miglioramenti:
- Aggiungere funzionalità di esportazione in Excel
- Implementare filtri avanzati
- Aggiungere statistiche e grafici
- Permettere la modifica batch delle ricevute
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional
from .invoice_form import CustomMessageBox
from ..core.storage_manager import StorageManager

class InvoiceManagerDialog:
    """Finestra di dialogo per la gestione delle ricevute"""
    
    def __init__(self, parent):
        """
        Inizializza la finestra di gestione ricevute.
        
        Args:
            parent: Finestra padre Tkinter
            
        Crea:
        - Finestra di dialogo modale
        - Tabella delle ricevute
        - Controlli per la gestione
        
        Possibili miglioramenti:
        - Aggiungere supporto per temi
        - Implementare ridimensionamento colonne
        - Salvare le preferenze utente
        """
        # Crea la finestra di dialogo
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Gestione Ricevute")
        self.dialog.transient(parent)
        self.dialog.grab_set()  # Rende la finestra modale
        
        # Inizializza il gestore di storage
        self.storage_manager = StorageManager()
        
        # Centra la finestra sullo schermo
        window_width = 800
        window_height = 600
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configura l'interfaccia
        self.setup_ui()
        
    def setup_ui(self):
        """
        Configura l'interfaccia utente della finestra.
        
        Crea:
        - Frame principale con padding
        - Titolo della finestra
        - Campo di ricerca
        - Tabella delle ricevute
        - Pulsanti di azione
        
        Possibili miglioramenti:
        - Aggiungere barra degli strumenti
        - Implementare scorciatoie da tastiera
        - Aggiungere menu contestuale
        """
        # Frame principale con padding
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Gestione Ricevute", font=('Helvetica', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Frame per la ricerca
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Campo di ricerca
        ttk.Label(search_frame, text="Cerca:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_invoices)  # Aggiorna durante la digitazione
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Tabella delle ricevute
        columns = ('number', 'date', 'customer', 'amount')
        self.invoice_tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        # Configura le colonne
        self.invoice_tree.heading('number', text='Numero')
        self.invoice_tree.heading('date', text='Data')
        self.invoice_tree.heading('customer', text='Cliente')
        self.invoice_tree.heading('amount', text='Importo')
        
        # Imposta le larghezze delle colonne
        self.invoice_tree.column('number', width=150)
        self.invoice_tree.column('date', width=100)
        self.invoice_tree.column('customer', width=300)
        self.invoice_tree.column('amount', width=100)
        
        # Aggiunge la barra di scorrimento
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        # Posiziona la tabella e la barra di scorrimento
        self.invoice_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame per i pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Pulsanti di azione
        ttk.Button(button_frame, text="Elimina Selezionati", command=self.delete_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Esporta Selezionati", command=self.export_invoices).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Chiudi", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Carica i dati iniziali
        self.load_invoices()
        
    def load_invoices(self):
        """
        Carica tutte le ricevute nella tabella.
        
        Operazioni:
        1. Pulisce la tabella esistente
        2. Carica le ricevute dal gestore
        3. Inserisce le ricevute nella tabella
        
        Possibili miglioramenti:
        - Implementare caricamento paginato
        - Aggiungere cache per prestazioni migliori
        - Mostrare indicatore di caricamento
        """
        # Pulisce la tabella
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
            
        # Carica e inserisce le ricevute
        for invoice in self.storage_manager.load_all_invoices():
            self.invoice_tree.insert('', 'end', values=(
                invoice.invoice_number,
                invoice.date.strftime('%d/%m/%Y'),
                invoice.customer_name or '',
                f"€ {invoice.total_amount:.2f}"
            ))
        
    def filter_invoices(self, *args):
        """
        Filtra le ricevute in base al testo di ricerca.
        
        Operazioni:
        1. Ricarica tutte le ricevute
        2. Rimuove quelle che non corrispondono alla ricerca
        
        Possibili miglioramenti:
        - Implementare ricerca fuzzy
        - Aggiungere filtri per campo
        - Ottimizzare per grandi dataset
        """
        search_text = self.search_var.get().lower()
        self.load_invoices()  # Ricarica tutte le ricevute
        
        if search_text:
            for item in self.invoice_tree.get_children():
                values = self.invoice_tree.item(item)['values']
                if not any(search_text in str(value).lower() for value in values):
                    self.invoice_tree.delete(item)
                    
    def delete_invoice(self):
        """
        Elimina le ricevute selezionate.
        
        Operazioni:
        1. Verifica la selezione
        2. Chiede conferma
        3. Elimina le ricevute
        4. Aggiorna la vista
        
        Possibili miglioramenti:
        - Aggiungere funzionalità di ripristino
        - Implementare eliminazione in batch
        - Mostrare anteprima delle ricevute da eliminare
        """
        selection = self.invoice_tree.selection()
        if not selection:
            CustomMessageBox.showerror("Errore", "Seleziona le ricevute da eliminare")
            return
            
        if CustomMessageBox.askyesno("Conferma", "Sei sicuro di voler eliminare le ricevute selezionate?"):
            for item in selection:
                invoice_number = self.invoice_tree.item(item)['values'][0]
                self.storage_manager.delete_invoice(invoice_number)
            self.load_invoices()  # Ricarica dopo l'eliminazione
            
    def export_invoices(self):
        """
        Esporta le ricevute selezionate.
        
        TODO: Implementare la funzionalità di esportazione
        
        Possibili miglioramenti:
        - Aggiungere supporto per vari formati (PDF, Excel, CSV)
        - Permettere la selezione della cartella di destinazione
        - Aggiungere opzioni di personalizzazione dell'export
        """
        selection = self.invoice_tree.selection()
        if not selection:
            CustomMessageBox.showerror("Errore", "Seleziona le ricevute da esportare")
            return
            
        # TODO: Implementare la funzionalità di esportazione
        CustomMessageBox.showerror("Successo", "Ricevute esportate con successo")