# Known Issues and Potential Problems

## Main Window (main_window.py)

### Invoice History Loading
```python
# In load_invoice_history():
for invoice in invoices:
    self.history_tree.insert('', 'end', values=(...))
```
**Issue**: When loading invoices, the sort state is not properly maintained. The `sort_column` and `sort_ascending` state variables might be undefined if `setup_history_view` hasn't been called yet. Should initialize these in `__init__`.

### Invoice Number Sorting
```python
# In sort_history():
if column == 'number':
    items.sort(key=lambda x: int(x[0]), reverse=not self.sort_ascending)
```
**Issue**: The numeric sort for invoice numbers assumes they can be converted to integers. This could fail if invoice numbers contain non-numeric characters.

### Search Performance
```python
# In filter_history():
self.load_invoice_history()
```
**Issue**: The filter reloads all invoices on every keystroke, which is inefficient. Should keep a cached copy of all invoices and filter from that instead of reloading.

### Window Size Calculation
```python
# In setup_history_view():
window_width = self.root.winfo_width()
history_width = window_width // 3
```
**Issue**: Column widths are calculated using `window_width` which might be 1 during initial setup since the window hasn't been drawn yet.

### Date Sorting
```python
# In sort_history():
items.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'),
          reverse=not self.sort_ascending)
```
**Issue**: Date sorting will fail if date string is empty. Should handle empty date values in the sort function.

### Search Case Sensitivity
```python
# In filter_history():
if not any(search_text in str(value).lower() 
          for value in values):
```
**Issue**: Search is case-sensitive for some values due to `str()` conversion. Should ensure consistent case handling for all value types.

### Invoice Loading Error Handling
```python
# In load_selected_invoice():
invoice = self.storage_manager.load_invoice(invoice_number)
```
**Issue**: No error handling for malformed invoice data. Should catch and handle potential exceptions when loading invoice data.

### Resource Cleanup
**Issue**: No cleanup of resources when window is closed. Should implement proper cleanup in a destructor or cleanup method.

## Invoice Form (invoice_form.py)

### Notes Loading
```python
# In load_invoice():
self.notes_text.insert('1.0', invoice.notes)
```
**Issue**: The notes field is not properly cleared before loading new content. Should explicitly clear the notes field with `delete()` before inserting new content.

### Notes Whitespace Handling
```python
# In save_invoice():
'notes': self.notes_text.get('1.0', tk.END).strip()
```
**Issue**: Notes are stripped of trailing whitespace which might be intentional formatting. Should consider preserving whitespace in notes.

## PDF Generator (pdf_generator.py)

### PDF File Path Handling
```python
# When generating PDF file paths
file_path = Path(output_dir) / f"{invoice.invoice_number}.pdf"
```
**Issue**: No validation for invalid characters in invoice numbers that could create invalid file paths.

### Resource Management
```python
# When creating PDF documents
canvas = Canvas(file_path)
```
**Issue**: No explicit cleanup of PDF resources if generation fails. Should use context managers or try-finally blocks.

## Storage Manager (storage_manager.py)

### Concurrent Access
```python
# When saving invoices
with open(file_path, 'w') as f:
    json.dump(invoice.to_dict(), f, indent=2)
```
**Issue**: No file locking mechanism for concurrent access. Multiple instances could corrupt data.

### Index Consistency
```python
# During index building
self._index.clear()
```
**Issue**: Index rebuild clears existing index before rebuilding, could cause temporary inconsistency.

### Backup Management
```python
# When creating backups
backup_file = self.backup_dir / f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
```
**Issue**: No cleanup of old backups. Could lead to disk space issues over time.

## Counter Manager (counter_manager.py)

### Counter Persistence
```python
# When getting next counter
next_number = self.current + 1
```
**Issue**: Counter updates might not be atomic. Risk of duplicate numbers in concurrent usage.

### Counter Validation
```python
# When setting counter
self.current = value
```
**Issue**: No validation for negative or non-numeric counter values.

## Fix Dates (fix_dates.py)

### Date Format Handling
```python
formats = [
    '%Y-%m-%d',
    '%Y-%m-%d %H:%M:%S',
    '%d/%m/%Y',
    '%d-%m-%Y',
]
```
**Issue**: Limited date format support. Could fail with international date formats.

### Error Messages
```python
raise ValueError(
    "Invalid date format. Accepted formats:\n"
    "YYYY-MM-DD (e.g., 2024-12-06)\n"
    "DD/MM/YYYY (e.g., 06/12/2024)"
)
```
**Issue**: Error message doesn't list all supported formats.

## Invoice Model (invoice.py)

### Data Validation
```python
@dataclass
class Invoice:
    invoice_number: str
    date: datetime
    items: List[InvoiceItem]
```
**Issue**: No validation for invoice_number format or uniqueness.

### Decimal Precision
```python
total = quantity * price
```
**Issue**: No standardized decimal precision handling. Could lead to rounding inconsistencies.

### Item Validation
```python
def validate(self) -> bool:
    return (
        bool(self.invoice_number.strip()) and
        len(self.items) > 0 and
        all(item.validate() for item in self.items)
    )
```
**Issue**: Validation doesn't check for duplicate item descriptions or negative totals.

## Company Config (company_config.py)

### Configuration Persistence
```python
# When saving company details
json.dump(config, f, indent=2)
```
**Issue**: No backup of previous configuration before saving new one.

### Input Validation
```python
# When saving company details
self.save_config()
```
**Issue**: No validation of required fields or field formats (e.g., VAT number format).

## Settings Manager (settings_manager.py)

### Default Settings
```python
# When loading settings
settings = json.load(f)
```
**Issue**: No fallback to default values if settings file is corrupted.

### Settings Migration
**Issue**: No version control or migration system for settings format changes.

## Custom Widgets (custom_widgets.py)

### Memory Management
```python
class ItemsTable(ttk.Frame):
```
**Issue**: No cleanup of large datasets in table widget. Could cause memory issues with many items.

### Event Handling
```python
self.event_generate('<<TotalChanged>>')
```
**Issue**: No error handling if event binding fails.

## General Issues

### Error Logging
**Issue**: Inconsistent error logging across modules. Some use print, others use logging.

### Internationalization
**Issue**: Hard-coded strings throughout the application. No support for multiple languages.

### Type Hints
**Issue**: Incomplete or missing type hints in many functions. Makes code harder to maintain.

### Documentation
**Issue**: Inconsistent documentation style and coverage across modules.

### Testing
**Issue**: Limited or no unit tests for critical functionality.

## Recommended Additional Solutions

11. Implement file locking for concurrent access
12. Add backup rotation and cleanup
13. Implement atomic counter updates
14. Add comprehensive date format support
15. Standardize decimal precision handling
16. Add configuration versioning
17. Implement proper memory management
18. Add comprehensive logging system
19. Implement internationalization support
20. Add complete test coverage

These additional issues should also be addressed in future updates to improve the overall system reliability and maintainability. 