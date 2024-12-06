"""
Invoice Model - Represents an invoice in the system
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

@dataclass
class InvoiceItem:
    """Represents a single item in an invoice"""
    description: str
    quantity: Decimal
    price: Decimal
    total: Decimal = None

    def __post_init__(self):
        """Calculate total if not provided"""
        if self.total is None:
            self.total = self.quantity * self.price

    def validate(self) -> bool:
        """Validate the invoice item"""
        return (
            bool(self.description.strip()) and
            self.quantity > 0 and
            self.price >= 0
        )

@dataclass
class Invoice:
    """Represents a complete invoice"""
    invoice_number: str
    date: datetime
    items: List[InvoiceItem]
    customer_name: Optional[str] = None
    customer_vat: Optional[str] = None
    customer_sdi: Optional[str] = None
    customer_street: Optional[str] = None
    customer_email: Optional[str] = None
    notes: Optional[str] = None
    total_amount: Decimal = None
    
    def __post_init__(self):
        """Calculate total amount if not provided"""
        if self.total_amount is None:
            self.total_amount = sum(item.total for item in self.items)

    def validate(self) -> bool:
        """Validate the entire invoice"""
        return (
            bool(self.invoice_number.strip()) and
            len(self.items) > 0 and
            all(item.validate() for item in self.items)
        )

    def to_dict(self) -> dict:
        """Convert invoice to dictionary for storage"""
        return {
            'invoice_number': self.invoice_number,
            'date': self.date.strftime('%Y-%m-%d'),  # Store date in ISO format
            'customer_name': self.customer_name,
            'customer_vat': self.customer_vat,
            'customer_sdi': self.customer_sdi,
            'customer_street': self.customer_street,
            'customer_email': self.customer_email,
            'items': [
                {
                    'description': item.description,
                    'quantity': str(item.quantity),
                    'price': str(item.price),
                    'total': str(item.total)
                }
                for item in self.items
            ],
            'notes': self.notes,
            'total_amount': str(self.total_amount)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Invoice':
        """Create invoice from dictionary"""
        items = [
            InvoiceItem(
                description=item['description'],
                quantity=Decimal(item['quantity']),
                price=Decimal(item['price']),
                total=Decimal(item['total'])
            )
            for item in data['items']
        ]
        
        # Parse date from ISO format
        try:
            invoice_date = datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            # Try parsing with time if present
            invoice_date = datetime.fromisoformat(data['date'])
        
        return cls(
            invoice_number=data['invoice_number'],
            date=invoice_date,
            customer_name=data.get('customer_name'),
            customer_vat=data.get('customer_vat'),
            customer_sdi=data.get('customer_sdi'),
            customer_street=data.get('customer_street'),
            customer_email=data.get('customer_email'),
            items=items,
            notes=data.get('notes'),
            total_amount=Decimal(data['total_amount'])
        ) 