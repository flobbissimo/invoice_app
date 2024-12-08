"""
Invoice Management System - Main Module

This module serves as the entry point when running the package directly.
It provides a clean way to start the application using:
    python -m src

Features:
1. Clean entry point for the application
2. Proper module execution handling
3. Import error handling
4. Exit code management
"""

try:
    from . import main
except ImportError as e:
    print(f"Error importing application modules: {e}")
    print("Please ensure you have installed all required dependencies.")
    print("Run: pip install -r requirements.txt")
    exit(1)

if __name__ == "__main__":
    """
    Execute the application when the module is run directly.
    
    This is the preferred way to start the application as it ensures:
    - Proper Python path handling
    - Correct module imports
    - Clean exit codes
    
    Usage:
        python -m src
    """
    main() 