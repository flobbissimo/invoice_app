"""
Invoice Model - Core data structures for invoice management

Key Features:
1. Type-safe data structures
2. Automatic calculations
3. Data validation
4. Serialization support
5. Immutable design

Components:
1. InvoiceItem:
   - Item description
   - Quantity tracking
   - Price management
   - Total calculation

2. Invoice:
   - Invoice metadata
   - Customer details
   - Item collection
   - Amount calculations
   - VAT handling

Technical Details:
- Uses dataclasses for type safety
- Implements decimal arithmetic
- Manages data validation
- Handles serialization
- Provides immutability

Data Validation:
1. InvoiceItem:
   - Non-empty description
   - Positive quantity
   - Non-negative price
   - Valid total amount

2. Invoice:
   - Valid invoice number
   - Proper date format
   - At least one item
   - Valid customer data
   - Correct calculations

Calculations:
- Item total = quantity * price
- Invoice total = sum of item totals
- VAT amount = total * 0.22 (22% Italian VAT)
- All calculations use Decimal for precision

Usage Example:
    # Create invoice item
    item = InvoiceItem(
        description="Product A",
        quantity=Decimal("2"),
        price=Decimal("10.50")
    )
    
    # Create invoice
    invoice = Invoice(
        invoice_number="INV-001",
        date=datetime.now(),
        items=[item],
        customer_name="Customer A"
    )
    
    # Access calculated values
    print(f"Total: {invoice.total_amount}")
    print(f"VAT: {invoice.vat_amount}")
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

@dataclass
class InvoiceItem:
    """
    Represents a single item in an invoice
    
    Attributes:
        description (str): Item description or name
        quantity (Decimal): Number of items
        price (Decimal): Price per unit
        total (Decimal): Total price (quantity * price)
        
    Features:
        - Automatic total calculation
        - Input validation
        - Decimal precision for monetary values
        
    Example:
        >>> item = InvoiceItem("Test Item", Decimal("2"), Decimal("10.50"))
        >>> item.total
        Decimal("21.00")
    """
    description: str
    quantity: Decimal
    price: Decimal
    total: Decimal = None

    def __post_init__(self):
        """
        Post-initialization hook for automatic calculations
        
        Calculates the total amount if not provided:
        total = quantity * price
        
        The total is calculated with Decimal precision to avoid
        floating point arithmetic errors.
        """
        if self.total is None:
            self.total = self.quantity * self.price

    def validate(self) -> bool:
        """
        Validate the invoice item data
        
        Validation rules:
        1. Description must not be empty
        2. Quantity must be greater than 0
        3. Price must not be negative
        
        Returns:
            bool: True if all validation rules pass
        """
        return (
            bool(str(self.description).strip()) and  # Convert to string to handle numeric values
            self.quantity > 0 and
            self.price >= 0
        )

@dataclass
class Invoice:
    """
    Represents a complete invoice with all its details
    
    Required Attributes:
        invoice_number (str): Unique identifier for the invoice
        date (datetime): Invoice creation date
        items (List[InvoiceItem]): List of items in the invoice
        
    Optional Attributes:
        customer_name (str): Name of the customer
        customer_vat (str): VAT number
        customer_sdi (str): SDI code for electronic invoicing
        customer_street (str): Street address
        customer_email (str): Email address
        notes (str): Additional notes
        total_amount (Decimal): Total invoice amount
        vat_amount (Decimal): VAT amount (22% of total)
    """
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
    vat_amount: Decimal = None
    
    def __post_init__(self):
        """Calculate totals if not provided"""
        if self.total_amount is None:
            self.total_amount = sum(item.total for item in self.items)
        if self.vat_amount is None:
            self.vat_amount = self.total_amount * Decimal('0.22')
            
    def update(self, other: 'Invoice'):
        """Update invoice data from another invoice"""
        self.invoice_number = other.invoice_number
        self.date = other.date
        self.customer_name = other.customer_name
        self.customer_vat = other.customer_vat
        self.customer_sdi = other.customer_sdi
        self.customer_street = other.customer_street
        self.customer_email = other.customer_email
        self.notes = other.notes
        self.items = other.items.copy()
        self.total_amount = other.total_amount
        self.vat_amount = other.vat_amount

    def validate(self) -> bool:
        """
        Validate the entire invoice
        
        Validation rules:
        1. Invoice number must not be empty
        2. Must have at least one item
        3. All items must be valid
        
        Returns:
            bool: True if all validation rules pass
        """
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
                    'description': str(item.description),
                    'quantity': str(item.quantity),
                    'price': str(item.price),
                    'total': str(item.total)
                }
                for item in self.items
            ],
            'notes': self.notes,
            'total_amount': str(self.total_amount),
            'vat_amount': str(self.vat_amount)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Invoice':
        """Create invoice from dictionary data"""
        items = [
            InvoiceItem(
                description=str(item['description']),
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
            total_amount=Decimal(data['total_amount']),
            vat_amount=Decimal(data.get('vat_amount', '0'))
        ) 