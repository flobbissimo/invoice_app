"""
Date handling utilities for consistent date formatting across the application
"""
from datetime import datetime

def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats to datetime object"""
    formats = [
        '%Y-%m-%d',           # 2024-12-06
        '%Y-%m-%d %H:%M:%S',  # 2024-12-06 15:30:00
        '%d/%m/%Y',           # 06/12/2024
        '%d-%m-%Y',           # 06-12-2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
            
    raise ValueError(
        f"Data non valida. Formati accettati:\n"
        f"YYYY-MM-DD (es. 2024-12-06)\n"
        f"DD/MM/YYYY (es. 06/12/2024)"
    )

def format_date(date: datetime) -> str:
    """Format datetime object to standard string format"""
    return date.strftime('%Y-%m-%d')

def format_date_display(date: datetime) -> str:
    """Format datetime object for display"""
    return date.strftime('%d/%m/%Y') 