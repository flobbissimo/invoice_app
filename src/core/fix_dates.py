"""
Date Handling Utilities - Provides consistent date formatting across the application

This module handles all date-related operations with the following features:
1. Flexible date string parsing with multiple format support
2. Consistent date formatting for storage and display
3. Error handling for invalid date formats
4. Localized date display formatting

Key Functions:
- parse_date: Converts various date string formats to datetime objects
- format_date: Standardizes date format for storage
- format_date_display: Formats dates for user interface display
"""
from datetime import datetime

def parse_date(date_str: str) -> datetime:
    """
    Parse date string in various formats to datetime object
    
    Supported formats:
    - ISO format: '%Y-%m-%d' (e.g., 2024-12-06)
    - ISO with time: '%Y-%m-%d %H:%M:%S' (e.g., 2024-12-06 15:30:00)
    - European format: '%d/%m/%Y' (e.g., 06/12/2024)
    - European with dashes: '%d-%m-%Y' (e.g., 06-12-2024)
    
    Args:
        date_str (str): Date string in any supported format
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If the date string doesn't match any supported format
    """
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
        "Invalid date format. Accepted formats:\n"
        "YYYY-MM-DD (e.g., 2024-12-06)\n"
        "DD/MM/YYYY (e.g., 06/12/2024)"
    )

def format_date(date: datetime) -> str:
    """
    Format datetime object to standard string format
    
    Converts any datetime object to ISO format (YYYY-MM-DD)
    for consistent storage and processing.
    
    Args:
        date (datetime): Date to format
        
    Returns:
        str: Formatted date string in ISO format
        
    Example:
        >>> format_date(datetime(2024, 12, 6))
        '2024-12-06'
    """
    return date.strftime('%Y-%m-%d')

def format_date_display(date: datetime) -> str:
    """
    Format datetime object for display in the user interface
    
    Converts datetime to localized format (DD/MM/YYYY)
    for better readability in the European context.
    
    Args:
        date (datetime): Date to format
        
    Returns:
        str: Formatted date string in European format
        
    Example:
        >>> format_date_display(datetime(2024, 12, 6))
        '06/12/2024'
    """
    return date.strftime('%d/%m/%Y') 