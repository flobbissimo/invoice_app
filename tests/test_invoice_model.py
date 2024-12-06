"""
Tests for the Invoice model
"""
import pytest
from decimal import Decimal
from datetime import datetime
from src.models.invoice import Invoice, InvoiceItem

def test_invoice_item_creation():
    """Test creating an invoice item"""
    item = InvoiceItem(
        description="Test Item",
        quantity=Decimal("2"),
        price=Decimal("10.50")
    )
    
    assert item.description == "Test Item"
    assert item.quantity == Decimal("2")
    assert item.price == Decimal("10.50")
    assert item.total == Decimal("21.00")

def test_invoice_item_validation():
    """Test invoice item validation"""
    valid_item = InvoiceItem(
        description="Valid Item",
        quantity=Decimal("1"),
        price=Decimal("10.00")
    )
    assert valid_item.validate() is True
    
    invalid_items = [
        InvoiceItem("", Decimal("1"), Decimal("10.00")),  # Empty description
        InvoiceItem("Test", Decimal("0"), Decimal("10.00")),  # Zero quantity
        InvoiceItem("Test", Decimal("1"), Decimal("-1.00")),  # Negative price
    ]
    
    for item in invalid_items:
        assert item.validate() is False

def test_invoice_creation():
    """Test creating an invoice"""
    items = [
        InvoiceItem("Item 1", Decimal("2"), Decimal("10.00")),
        InvoiceItem("Item 2", Decimal("1"), Decimal("15.00"))
    ]
    
    invoice = Invoice(
        invoice_number="TEST-001",
        date=datetime.now(),
        customer_name="Test Customer",
        items=items
    )
    
    assert invoice.invoice_number == "TEST-001"
    assert invoice.customer_name == "Test Customer"
    assert len(invoice.items) == 2
    assert invoice.total_amount == Decimal("35.00")

def test_invoice_validation():
    """Test invoice validation"""
    valid_items = [InvoiceItem("Test Item", Decimal("1"), Decimal("10.00"))]
    
    valid_invoice = Invoice(
        invoice_number="TEST-001",
        date=datetime.now(),
        customer_name="Test Customer",
        items=valid_items
    )
    assert valid_invoice.validate() is True
    
    # Test invalid cases
    invalid_invoices = [
        # Empty invoice number
        Invoice(
            invoice_number="",
            date=datetime.now(),
            customer_name="Test Customer",
            items=valid_items
        ),
        # Empty customer name
        Invoice(
            invoice_number="TEST-001",
            date=datetime.now(),
            customer_name="",
            items=valid_items
        ),
        # No items
        Invoice(
            invoice_number="TEST-001",
            date=datetime.now(),
            customer_name="Test Customer",
            items=[]
        )
    ]
    
    for invoice in invalid_invoices:
        assert invoice.validate() is False

def test_invoice_serialization():
    """Test invoice serialization to/from dict"""
    items = [InvoiceItem("Test Item", Decimal("2"), Decimal("10.00"))]
    date = datetime.now()
    
    original_invoice = Invoice(
        invoice_number="TEST-001",
        date=date,
        customer_name="Test Customer",
        items=items,
        notes="Test Notes"
    )
    
    # Convert to dict and back
    invoice_dict = original_invoice.to_dict()
    restored_invoice = Invoice.from_dict(invoice_dict)
    
    # Check if data is preserved
    assert restored_invoice.invoice_number == original_invoice.invoice_number
    assert restored_invoice.customer_name == original_invoice.customer_name
    assert restored_invoice.notes == original_invoice.notes
    assert restored_invoice.total_amount == original_invoice.total_amount
    assert len(restored_invoice.items) == len(original_invoice.items)
    
    # Check first item
    assert restored_invoice.items[0].description == original_invoice.items[0].description
    assert restored_invoice.items[0].quantity == original_invoice.items[0].quantity
    assert restored_invoice.items[0].price == original_invoice.items[0].price
    assert restored_invoice.items[0].total == original_invoice.items[0].total 