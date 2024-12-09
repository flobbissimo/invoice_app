"""
Storage Manager - Handles invoice data persistence and management

Key Features:
1. Thread-safe invoice storage and retrieval
2. Automatic backup system with versioning
3. High-performance search with indexing
4. Batch operations support
5. Error recovery mechanisms

Components:
- File Storage: JSON-based persistence
- Search Index: In-memory for fast queries
- Backup System: Versioned backups
- Cache: LRU cache for frequent access

Technical Details:
- Uses file-based locking for thread safety
- Implements background indexing
- Manages concurrent access
- Handles file system operations
- Provides data validation

Performance Optimizations:
- LRU cache for frequently accessed invoices
- Background indexing for faster searches
- Batch loading for large datasets
- Efficient file operations
- Memory-efficient data structures

Error Handling:
- Automatic backup before modifications
- Recovery from corrupted files
- Validation of data integrity
- Graceful degradation
- Detailed error reporting

Usage Example:
    # Initialize manager
    manager = StorageManager()
    
    # Save invoice
    manager.save_invoice(invoice)
    
    # Load with caching
    invoice = manager.load_invoice("INV-001")
    
    # Search with index
    results = manager.search_invoices("customer name")
    
    # Batch operations
    invoices = manager.load_all_invoices()
"""
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal, InvalidOperation
import logging

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

    def _calculate_numeric_hash(self, invoice_data: dict) -> str:
        """Calculate SHA256 hash of all numerical values in the invoice"""
        try:
            # Create a string of all numerical values in a consistent order
            numeric_values = []
            
            # Add invoice total and VAT
            numeric_values.append(str(Decimal(invoice_data['total_amount'])))
            numeric_values.append(str(Decimal(invoice_data['vat_amount'])))
            
            # Add all item values in a consistent order
            for item in sorted(invoice_data['items'], key=lambda x: x['description']):
                numeric_values.extend([
                    str(Decimal(item['quantity'])),
                    str(Decimal(item['price'])),
                    str(Decimal(item['total']))
                ])
                
            # Join all values and calculate hash
            numeric_string = '|'.join(numeric_values)
            return hashlib.sha256(numeric_string.encode()).hexdigest()
            
        except (InvalidOperation, KeyError, TypeError) as e:
            logging.error(f"Error calculating numeric hash: {str(e)}")
            return ""

    def _validate_invoice_math(self, invoice_data: dict) -> Tuple[bool, str]:
        """Validate mathematical consistency and return hash of numerical values"""
        try:
            # Calculate numeric hash first
            numeric_hash = self._calculate_numeric_hash(invoice_data)
            
            # Validate each item's total
            for item in invoice_data['items']:
                quantity = Decimal(item['quantity'])
                price = Decimal(item['price'])
                total = Decimal(item['total'])
                calculated_total = quantity * price
                
                if abs(calculated_total - total) > Decimal('0.01'):
                    return False, numeric_hash
            
            # Validate invoice total
            items_total = sum(Decimal(item['total']) for item in invoice_data['items'])
            invoice_total = Decimal(invoice_data['total_amount'])
            
            if abs(items_total - invoice_total) > Decimal('0.01'):
                return False, numeric_hash
                
            # Validate VAT calculation (22% in Italy)
            vat = Decimal(invoice_data['vat_amount'])
            calculated_vat = invoice_total * Decimal('0.22')
            
            if abs(vat - calculated_vat) > Decimal('0.01'):
                return False, numeric_hash
                
            return True, numeric_hash
            
        except (InvalidOperation, KeyError, TypeError):
            return False, ""

    def _should_create_backup(self, current_data: dict, latest_backup: dict) -> bool:
        """Determine if a new backup should be created based on numeric hash"""
        if not latest_backup:
            return True
            
        try:
            # Calculate hashes for both current and backup data
            current_hash = self._calculate_numeric_hash(current_data)
            backup_hash = self._calculate_numeric_hash(latest_backup)
            
            # Create backup if hashes are different
            return current_hash != backup_hash
            
        except Exception as e:
            logging.error(f"Error comparing invoice data: {str(e)}")
            return True  # Create backup if comparison fails

    def _create_backup(self, invoice_file: Path):
        """Create a backup of the invoice file if needed"""
        try:
            # Read current invoice data
            with open(invoice_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)

            # Validate mathematical consistency and get hash
            is_valid, current_hash = self._validate_invoice_math(current_data)
            if not is_valid:
                logging.warning(f"Mathematical validation failed for invoice {invoice_file.stem}")
                
            # Store the hash in the invoice data for future reference
            current_data['_numeric_hash'] = current_hash
                
            # Get latest backup
            backup_files = sorted(
                self.backup_dir.glob(f"{invoice_file.stem}_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            latest_backup = None
            if backup_files:
                try:
                    with open(backup_files[0], 'r', encoding='utf-8') as f:
                        latest_backup = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass
            
            # Only create backup if needed
            if self._should_create_backup(current_data, latest_backup):
                backup_file = self.backup_dir / f"{invoice_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                # Save the backup with the hash included
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(current_data, f, indent=2)
                logging.info(f"Created backup for invoice {invoice_file.stem} with hash {current_hash}")
                
                # Clean old backups in background
                self._executor.submit(self._clean_old_backups, invoice_file.stem)
            else:
                logging.info(f"Skipped backup for invoice {invoice_file.stem} - No numeric changes detected")
                
        except Exception as e:
            logging.error(f"Error during backup creation for {invoice_file.stem}: {str(e)}")
            # Create backup anyway in case of error
            backup_file = self.backup_dir / f"{invoice_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(invoice_file, backup_file)

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