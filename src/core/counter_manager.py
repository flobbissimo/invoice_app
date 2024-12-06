"""
Counter Manager - Handles invoice numbering with improved reliability
"""
import json
import os
import time
from pathlib import Path
from typing import Optional

class CounterManager:
    """Manages invoice counter with file locking and backup"""
    
    def __init__(self, data_dir: str = "data"):
        self.counter_file = Path(data_dir) / "invoice_counter.json"
        self.backup_file = Path(data_dir) / "backups" / "invoice_counter.backup.json"
        self.lock_file = Path(data_dir) / "invoice_counter.lock"
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        self.counter_file.parent.mkdir(parents=True, exist_ok=True)
        self.backup_file.parent.mkdir(parents=True, exist_ok=True)

    def _read_counter_file(self, file_path: Path) -> Optional[int]:
        """Read counter value from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                counter = data.get('counter')
                if isinstance(counter, int) and counter > 0:
                    return counter
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        return None

    def _write_counter_file(self, file_path: Path, counter: int):
        """Write counter value to file"""
        with open(file_path, 'w') as f:
            json.dump({'counter': counter}, f)

    def _acquire_lock(self) -> bool:
        """Try to acquire lock by creating a lock file"""
        try:
            # Try to create the lock file
            with open(self.lock_file, 'x') as f:
                f.write('locked')
            return True
        except FileExistsError:
            return False

    def _release_lock(self):
        """Release lock by removing the lock file"""
        try:
            os.remove(self.lock_file)
        except FileNotFoundError:
            pass

    def get_next_counter(self) -> int:
        """Get next counter value with file locking"""
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Try to acquire lock
                if self._acquire_lock():
                    try:
                        # Read counter from main file
                        counter = self._read_counter_file(self.counter_file)
                        
                        # If main file is corrupted, try backup
                        if counter is None:
                            counter = self._read_counter_file(self.backup_file)
                        
                        # If both files are corrupted or don't exist, start from 1
                        if counter is None:
                            counter = 0
                        
                        # Increment counter
                        counter += 1
                        
                        # Write to both main and backup files
                        self._write_counter_file(self.counter_file, counter)
                        self._write_counter_file(self.backup_file, counter)
                        
                        return counter
                    finally:
                        # Always release lock
                        self._release_lock()
                else:
                    # Lock acquisition failed, wait and retry
                    attempt += 1
                    if attempt < max_attempts:
                        time.sleep(0.1 * attempt)
                    continue
                    
            except (IOError, OSError):
                # If any IO operation fails, wait and retry
                attempt += 1
                if attempt < max_attempts:
                    time.sleep(0.1 * attempt)
                continue
            
        raise RuntimeError("Could not acquire lock for counter file after multiple attempts") 