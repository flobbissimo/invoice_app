"""
Storage Manager - Handles invoice data persistence and management

This module provides the StorageManager class which is responsible for:
1. Storing and retrieving invoice data in JSON format
2. Managing automatic backups of invoices
3. Providing search functionality across invoices
4. Handling file system operations for the application

Performance optimizations:
- Implements LRU cache for frequently accessed invoices
- Lazy loading of invoice data
- Index-based search for faster queries
"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor

from ..models.invoice import Invoice

class StorageManager:
    """Manages invoice storage and retrieval with automatic backup functionality
    
    This class handles all file system operations related to invoices, including:
    - Saving and loading invoice data in JSON format
    - Creating automatic backups before modifications
    - Searching through stored invoices
    - Managing the invoice directory structure
    
    Performance optimizations:
    - LRU cache for frequently accessed invoices
    - Background indexing for faster searches
    - Batch loading for invoice lists
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the storage manager with specified data directory
        
        Args:
            data_dir (str): Base directory for data storage. Defaults to "data"
        """
        self.data_dir = Path(data_dir)
        self.invoices_dir = self.data_dir / "invoices"
        self.backup_dir = self.data_dir / "backups"
        self._ensure_directories()
        
        # Initialize cache and index
        self._index: Dict[str, Dict] = {}  # Search index for quick lookups
        self._index_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)  # For background operations
        
        # Build initial index in background
        self._executor.submit(self._build_index)

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.invoices_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _build_index(self):
        """Build search index for all invoices
        
        Creates an in-memory index of invoice metadata for faster searching.
        This runs in the background when the application starts.
        """
        with self._index_lock:
            self._index.clear()
            for file_path in self.invoices_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Store minimal data in index
                        self._index[file_path.stem] = {
                            'invoice_number': data['invoice_number'],
                            'customer_name': data.get('customer_name', ''),
                            'date': data['date'],
                            'total_amount': data['total_amount'],
                            'notes': data.get('notes', '')
                        }
                except (json.JSONDecodeError, KeyError):
                    continue

    def _update_index(self, invoice: Invoice):
        """Update search index for a single invoice"""
        with self._index_lock:
            self._index[invoice.invoice_number] = {
                'invoice_number': invoice.invoice_number,
                'customer_name': invoice.customer_name or '',
                'date': invoice.date.isoformat(),
                'total_amount': str(invoice.total_amount),
                'notes': invoice.notes or ''
            }

    def _create_backup(self, invoice_file: Path):
        """Create a backup of the invoice file"""
        backup_file = self.backup_dir / f"{invoice_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(invoice_file, backup_file)
        
        # Clean old backups in background
        self._executor.submit(self._clean_old_backups, invoice_file.stem)

    def _clean_old_backups(self, invoice_number: str, keep_latest: int = 5):
        """Clean old backup files, keeping only the specified number of latest backups"""
        backup_files = sorted(
            self.backup_dir.glob(f"{invoice_number}_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Remove old backups
        for backup_file in backup_files[keep_latest:]:
            try:
                backup_file.unlink()
            except OSError:
                continue

    def save_invoice(self, invoice: Invoice) -> Path:
        """Save invoice to file and update index"""
        # Create file path
        file_path = self.invoices_dir / f"{invoice.invoice_number}.json"
        
        # Create backup if file exists
        if file_path.exists():
            self._create_backup(file_path)
        
        # Save invoice
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(invoice.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Update index in background
        self._executor.submit(self._update_index, invoice)
            
        return file_path

    @lru_cache(maxsize=100)  # Cache last 100 accessed invoices
    def load_invoice(self, invoice_number: str) -> Optional[Invoice]:
        """Load invoice from file with caching"""
        file_path = self.invoices_dir / f"{invoice_number}.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Invoice.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def load_all_invoices(self) -> List[Invoice]:
        """Load all invoices with batch processing
        
        Returns invoices sorted by date (newest first) using the index
        for better performance with large datasets.
        """
        # Use index to get sorted invoice numbers
        with self._index_lock:
            sorted_numbers = sorted(
                self._index.keys(),
                key=lambda x: self._index[x]['date'],
                reverse=True
            )
        
        # Load invoices in batches
        invoices = []
        batch_size = 50  # Adjust based on your needs
        
        for i in range(0, len(sorted_numbers), batch_size):
            batch = sorted_numbers[i:i + batch_size]
            for invoice_number in batch:
                invoice = self.load_invoice(invoice_number)
                if invoice:
                    invoices.append(invoice)
        
        return invoices

    def list_invoices(self) -> List[str]:
        """Get a list of all invoice numbers using the index"""
        with self._index_lock:
            return list(self._index.keys())

    def delete_invoice(self, invoice_number: str) -> bool:
        """Delete invoice file and update index"""
        file_path = self.invoices_dir / f"{invoice_number}.json"
        
        if not file_path.exists():
            return False
            
        # Create backup before deletion
        self._create_backup(file_path)
        
        # Delete file
        file_path.unlink()
        
        # Update index
        with self._index_lock:
            self._index.pop(invoice_number, None)
        
        # Clear cache for this invoice
        self.load_invoice.cache_clear()
        
        return True

    def search_invoices(self, query: str) -> List[Invoice]:
        """Search invoices using the index for better performance
        
        Uses the in-memory index to quickly find matching invoices
        without reading all files from disk.
        """
        results = []
        query = query.lower()
        
        # Search using index
        with self._index_lock:
            matching_numbers = [
                num for num, data in self._index.items()
                if (
                    query in data['invoice_number'].lower() or
                    query in data['customer_name'].lower() or
                    query in data['notes'].lower()
                )
            ]
        
        # Load matching invoices
        for invoice_number in matching_numbers:
            invoice = self.load_invoice(invoice_number)
            if invoice:
                results.append(invoice)
        
        return results

    def __del__(self):
        """Cleanup resources"""
        self._executor.shutdown(wait=False)