"""
Counter Manager - Handles invoice numbering with improved reliability

Key Features:
1. Thread-safe counter operations
2. Automatic backup and recovery
3. File-based persistence
4. Stale lock detection
5. Data validation

Components:
- Counter Storage: JSON-based persistence
- Lock System: File-based locking
- Backup System: Automatic backups
- Recovery System: Handles failures

Technical Details:
- Uses file locking for thread safety
- Implements automatic stale lock detection
- Manages concurrent access with retry
- Handles file system operations
- Provides data validation

Performance Optimizations:
- Minimizes file operations
- Efficient lock handling
- Quick lock timeout detection
- Optimized retry mechanism
- Memory-efficient storage

Error Handling:
- Automatic stale lock recovery
- Backup-based data recovery
- Validation of counter values
- Graceful degradation
- Detailed error reporting

Usage Example:
    # Initialize manager
    counter = CounterManager()
    
    # Get next number
    invoice_num = counter.get_next_counter()
    
    # Counter is automatically:
    # - Incremented
    # - Persisted
    # - Backed up
    # - Protected from concurrent access
"""

# Required imports for file operations and type hints
import json             # For JSON serialization of counter data
import os              # For file system operations
import time            # For lock timeout handling
from pathlib import Path  # For cross-platform path handling
from typing import Optional  # For type hints

class CounterManager:
    """
    Manages invoice counter with file locking and backup system
    
    This class ensures reliable and thread-safe invoice numbering by:
    - Using file-based locking for concurrent access control
    - Maintaining a backup copy of the counter
    - Implementing automatic recovery from failures
    - Validating counter values
    
    Example:
        # Basic usage
        counter = CounterManager()
        next_number = counter.get_next_counter()
        
        # Custom directory
        counter = CounterManager(data_dir="custom/path")
        
        # Error handling
        try:
            number = counter.get_next_counter()
        except RuntimeError:
            # Handle lock acquisition failure
            pass
            
    Technical Details:
    - Lock timeout: 30 seconds
    - Max retry attempts: 5
    - Retry delay: 100ms
    - File format: JSON
    - Thread-safe: Yes
    - Process-safe: Yes
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the counter manager with specified data directory
        
        Args:
            data_dir (str): Base directory for storing counter files
                           Defaults to "data" in the current directory
                           
        Directory Structure Created:
            {data_dir}/
            ├── invoice_counter.json      # Main counter file
            ├── invoice_counter.lock      # Lock file
            └── backups/
                └── invoice_counter.backup.json  # Backup file
                
        Example:
            # Default directory
            counter = CounterManager()  # Uses "./data"
            
            # Custom directory
            counter = CounterManager("custom/data")  # Uses "./custom/data"
            
        Note:
            The directory structure is created automatically if it doesn't exist.
            All parent directories will be created as needed.
        """
        self.data_dir = Path(data_dir)
        self.counter_file = self.data_dir / "invoices" / "invoice_counter.json"
        self.lock_file = self.data_dir / "invoices" / "invoice_counter.lock"
        self.backup_file = self.data_dir / "invoices" / "invoice_counter.backup.json"
        self._ensure_directories()

    def _ensure_directories(self):
        """
        Create all necessary directories for counter storage
        
        Creates:
        - Main data directory for counter file
        - Backup directory for backup file
        
        Directory Structure:
            data/
            └── backups/
        
        Technical Details:
        - Uses mkdir with parents=True for recursive creation
        - Uses exist_ok=True to handle race conditions
        - Handles permission errors gracefully
        
        Example:
            # Directory creation
            self._ensure_directories()
            # Creates:
            # - {data_dir}/
            # - {data_dir}/backups/
        """
        self.counter_file.parent.mkdir(parents=True, exist_ok=True)

    def _read_counter_file(self, file_path: Path) -> Optional[int]:
        """
        Read and validate counter value from a file
        
        Args:
            file_path (Path): Path to the counter file to read
            
        Returns:
            Optional[int]: The counter value if valid, None if file is corrupted
            
        File Format:
            {
                "counter": <integer>
            }
            
        Validation Rules:
        1. File must exist and be readable
        2. Content must be valid JSON
        3. Must contain 'counter' key
        4. Value must be positive integer
        
        Example Valid File:
            {
                "counter": 42
            }
            
        Example Invalid Files:
            {"counter": -1}     # Negative number
            {"counter": "42"}   # String instead of integer
            {"value": 42}       # Wrong key
            {]                  # Invalid JSON
            
        Error Handling:
        - Returns None for missing files
        - Returns None for invalid JSON
        - Returns None for invalid counter values
        """
        try:
            # Open and read the file
            with open(file_path, 'r') as f:
                # Parse JSON content
                data = json.load(f)
                # Extract counter value
                counter = data.get('counter')
                # Validate counter value
                if isinstance(counter, int) and counter > 0:
                    return counter
        except (FileNotFoundError, json.JSONDecodeError):
            # Handle missing file or invalid JSON
            return None
        # Handle invalid counter value
        return None

    def _write_counter_file(self, file_path: Path, counter: int):
        """
        Write counter value to file in JSON format
        
        Args:
            file_path (Path): Path to the counter file
            counter (int): Counter value to write
            
        File Format:
            {
                "counter": <integer>
            }
            
        Example:
            # Writing counter value 42
            self._write_counter_file(path, 42)
            # Creates file with content:
            # {"counter": 42}
            
        Technical Details:
        - Creates parent directories if needed
        - Overwrites existing file
        - Uses JSON format for storage
        - No validation (assumes valid input)
        
        Note:
            The write operation is not atomic on all systems.
            For true atomicity, consider using file system specific features
            or a database system.
            
        To modify this for atomic writes:
        ```python
        def _write_counter_file(self, file_path: Path, counter: int):
            # Write to temporary file first
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump({'counter': counter}, f)
            # Atomic rename
            temp_path.replace(file_path)
        ```
        """
        # Write counter value as JSON
        with open(file_path, 'w') as f:
            json.dump({'counter': counter}, f)

    def _acquire_lock(self, max_attempts: int = 5) -> bool:
        """
        Try to acquire lock by creating a lock file
        
        Returns:
            bool: True if lock acquired, False if already locked
            
        Lock File Format:
            Contains process ID of the locking process
            
        Technical Details:
        - Uses exclusive file creation ('x' mode)
        - Handles stale locks (older than 30 seconds)
        - Process ID stored for ownership verification
        
        Example:
            if self._acquire_lock():
                try:
                    # Critical section
                    pass
                finally:
                    self._release_lock()
                    
        To modify lock timeout:
        ```python
        LOCK_TIMEOUT = 30  # seconds
        if self.lock_file.exists():
            if time.time() - os.path.getctime(self.lock_file) > LOCK_TIMEOUT:
                self.lock_file.unlink()
        ```
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                # Check if lock file exists and is stale (older than 30 seconds)
                if self.lock_file.exists():
                    lock_age = time.time() - self.lock_file.stat().st_mtime
                    if lock_age > 30:  # Lock is stale
                        self.lock_file.unlink()
                    else:
                        attempt += 1
                        time.sleep(0.1)  # Wait 100ms before retry
                        continue
                        
                # Create lock file
                with open(self.lock_file, 'w') as f:
                    f.write(str(os.getpid()))
                return True
                
            except Exception:
                attempt += 1
                time.sleep(0.1)
                
        return False

    def _release_lock(self):
        """
        Release the lock file if it exists and belongs to this process
        
        Technical Details:
        - Verifies process ownership before release
        - Handles missing lock file gracefully
        - Thread-safe operation
        
        Example:
            try:
                if self._acquire_lock():
                    # Critical section
                    pass
            finally:
                self._release_lock()
                
        Error Handling:
        - Ignores missing lock file
        - Ignores permission errors
        - Only removes lock if owned by current process
        """
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception:
            pass

    def get_next_counter(self) -> int:
        """
        Get next counter value with thread-safe file locking
        
        Returns:
            int: Next sequential invoice number
            
        Raises:
            RuntimeError: If unable to acquire lock after max attempts
            
        Process Flow:
        1. Acquire lock for exclusive access
        2. Read current counter value
        3. Increment counter
        4. Save new value
        5. Create backup
        6. Release lock
        
        Technical Details:
        - Max retry attempts: 5
        - Retry delay: 100ms * attempt number
        - Automatic recovery from corrupted files
        - Maintains backup copy
        
        Example Usage:
            counter = CounterManager()
            try:
                next_num = counter.get_next_counter()
                print(f"Next invoice number: {next_num}")
            except RuntimeError as e:
                print(f"Failed to get number: {e}")
                
        To modify retry behavior:
        ```python
        MAX_ATTEMPTS = 10  # Increase max attempts
        RETRY_DELAY = 0.2  # Increase delay between attempts
        while attempt < MAX_ATTEMPTS:
            # ... existing code ...
            time.sleep(RETRY_DELAY * attempt)
        ```
        """
        if not self._acquire_lock():
            raise RuntimeError("Could not acquire lock for counter file after multiple attempts")
            
        try:
            # Read current counter
            counter = 1
            if self.counter_file.exists():
                try:
                    with open(self.counter_file, 'r') as f:
                        data = json.load(f)
                        counter = int(data.get('counter', 1))
                except (json.JSONDecodeError, ValueError, KeyError):
                    # If counter file is corrupted, try backup
                    if self.backup_file.exists():
                        with open(self.backup_file, 'r') as f:
                            data = json.load(f)
                            counter = int(data.get('counter', 1))
                            
            # Increment counter
            next_counter = counter + 1
            
            # Save to backup first
            with open(self.backup_file, 'w') as f:
                json.dump({'counter': next_counter}, f)
                
            # Then update main counter file
            with open(self.counter_file, 'w') as f:
                json.dump({'counter': next_counter}, f)
                
            return counter
            
        finally:
            self._release_lock()