"""
Invoice Management System - Main Application Package

This package provides a complete invoice management solution with the following features:
1. Professional invoice creation and management
2. PDF generation with customizable templates
3. Data persistence and backup
4. Logging system for debugging and auditing
5. Error handling and recovery

Package Structure:
- core/: Core business logic and data handling
- gui/: User interface components
- models/: Data models and validation
- utils/: Utility functions and helpers

Entry Points:
- main(): Application entry point
- setup_logging(): Logging configuration
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
from .gui.main_window import MainWindow

def setup_logging() -> logging.Logger:
    """
    Configure application-wide logging system
    
    Features:
    - Creates timestamped log files
    - Configures both file and console logging
    - Sets appropriate log format and level
    - Creates log directory if needed
    
    Log Format:
        timestamp - logger_name - log_level - message
    
    Returns:
        logging.Logger: Configured logger instance
        
    Directory Structure:
        logs/
        └── app_YYYYMMDD_HHMMSS.log
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"app_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """
    Application entry point - Initializes and runs the application
    
    Process Flow:
    1. Set up logging system
    2. Log system information
    3. Create main application window
    4. Start the application event loop
    5. Handle any fatal errors
    
    Error Handling:
    - Catches and logs all unhandled exceptions
    - Keeps console window open on error in interactive mode
    - Provides clean exit with status code
    
    Usage:
        To start the application:
        >>> from src import main
        >>> main()
    """
    logger = setup_logging()
    
    try:
        logger.info("Starting Invoice Management System...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {Path.cwd()}")
        
        app = MainWindow()
        logger.info("Main window created successfully")
        
        app.run()
        logger.info("Application closed normally")
        
    except Exception as e:
        logger.exception("Fatal error in main application")
        # Keep the console window open on error in interactive mode
        if sys.stderr.isatty():
            input("Press Enter to exit...")
        sys.exit(1)

# Make main function available at package level
__all__ = ['main'] 