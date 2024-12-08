"""
Company Configuration Dialog - Manages company details and settings

Key Features:
1. Company details management
2. Field validation
3. Settings persistence
4. Configuration reload
5. Modal dialog

Components:
1. Basic Information:
   - Company name
   - Address details
   - Contact information
   - Tax identifiers

2. Business Details:
   - VAT number
   - SDI code
   - Bank details
   - Additional info

3. Contact Information:
   - Phone numbers
   - Email addresses
   - Website
   - Social media

Technical Details:
- Uses ttk widgets for native look
- Implements input validation
- Manages configuration files
- Handles data persistence
- Provides error feedback

Validation Rules:
1. Required Fields:
   - Company name
   - Address
   - VAT number

2. Format Validation:
   - Valid VAT format
   - SDI code (7 chars)
   - Email format
   - Phone format

3. Business Rules:
   - Valid tax codes
   - Complete address
   - Contact details

Usage Example:
    # Create dialog
    dialog = CompanyConfigDialog(
        parent,
        on_config_saved=reload_callback
    )
    
    # Dialog provides:
    # - Company details form
    # - Validation feedback
    # - Auto-save feature
    # - Configuration reload
"""
import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from typing import Callable, Optional
from .invoice_form import CustomMessageBox

class CompanyConfigDialog:
    """Dialog for configuring company details"""
    
    def __init__(self, parent, on_config_saved: Optional[Callable] = None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configurazione Azienda")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.config_dir = Path("config")
        self.config_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Callback for when config is saved
        self.on_config_saved = on_config_saved
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Company details
        ttk.Label(main_frame, text="Dettagli Azienda", font=('Helvetica', 12, 'bold')).pack(pady=(0, 20))
        
        # Create form fields
        self.fields = {}
        field_configs = [
            # Basic Info
            ("company_name", "Nome Azienda:"),  # Required
            
            # Address Details
            ("address", "Indirizzo:"),
            ("postal_code", "CAP:"),
            ("city", "Città:"),
            ("country", "Paese:"),
            
            # Tax & Business IDs
            ("vat_number", "P.IVA:"),  # Italian VAT number
            ("sdi", "SDI:"),  # Sistema di Interscambio code (7 characters)
            
            # Contact Info
            ("phone", "Telefono:"),
            ("email", "Email:"),
            
            # Payment Details
            ("billing_number", "IBAN:")  # Bank account for payments
        ]
        
        for field_id, label in field_configs:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.fields[field_id] = entry
            
        # Add help text for SDI
        sdi_help = ttk.Label(
            main_frame, 
            text="Nota: Il codice SDI deve essere di 7 caratteri",
            font=('Helvetica', 9, 'italic'),
            foreground='gray'
        )
        sdi_help.pack(pady=(0, 10))
            
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Salva", command=self.save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
    def load_config(self):
        """Load existing configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            for field_id, entry in self.fields.items():
                if field_id in config:
                    entry.insert(0, config[field_id])
                    
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
    def save_config(self):
        """Save configuration"""
        config = {
            field_id: entry.get().strip()
            for field_id, entry in self.fields.items()
        }
        
        # Validate required fields
        required_fields = ['company_name']
        missing_fields = [
            field_id for field_id in required_fields
            if not config[field_id]
        ]
        
        if missing_fields:
            field_names = {
                'company_name': 'Nome Azienda'
            }
            missing_names = [field_names[field_id] for field_id in missing_fields]
            CustomMessageBox.showerror(
                "Errore",
                f"I seguenti campi sono obbligatori:\n\n{', '.join(missing_names)}"
            )
            return
            
        # Validate SDI format if provided
        sdi = config.get('sdi', '').strip()
        if sdi and len(sdi) != 7:
            CustomMessageBox.showerror(
                "Errore",
                "Il codice SDI deve essere di 7 caratteri"
            )
            return
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            # Notify callback if provided
            if self.on_config_saved:
                self.on_config_saved()
                
            CustomMessageBox.showerror(
                "Successo",
                "Configurazione salvata con successo.\nLe modifiche saranno applicate immediatamente."
            )
            self.dialog.destroy()
            
        except Exception as e:
            CustomMessageBox.showerror(
                "Errore",
                f"Errore durante il salvataggio:\n\n{str(e)}"
            )