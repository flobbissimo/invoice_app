"""
Ricevute - Invoice Management System
Main application entry point
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
from .gui.main_window import MainWindow

def setup_logging():
    """Setup logging configuration"""
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
    """Start the application"""
    logger = setup_logging()
    
    try:
        logger.info("Starting Ricevute application...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {Path.cwd()}")
        
        app = MainWindow()
        logger.info("Main window created successfully")
        
        app.run()
        logger.info("Application closed normally")
        
    except Exception as e:
        logger.exception("Fatal error in main application")
        # Keep the console window open on error
        if sys.stderr.isatty():
            input("Press Enter to exit...")
        sys.exit(1)

# Make main function available at package level
__all__ = ['main'] 