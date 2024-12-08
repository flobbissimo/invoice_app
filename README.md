# Invoice Manager

A professional invoice management system designed specifically for windsurf businesses. This application provides an intuitive graphical interface for creating, managing, and tracking invoices, with special focus on Italian fiscal requirements.

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-green.svg)

</div>

## 📋� Latest Updates (December 2023)

### New Features
- Modern UI design system with consistent color scheme
- Enhanced navigation with sidebar and quick action toolbar
- Improved invoice form with grid-based layout
- Real-time PDF preview functionality
- Advanced customer information auto-completion
- Dynamic item table with inline editing
- Improved company configuration interface
- Enhanced data validation and error prevention
- Responsive design for different screen sizes
- Performance optimizations for large datasets

### Technical Improvements
- Updated dependencies:
  - reportlab 4.0.0+
  - pillow 10.0.0+
  - python-dateutil 2.8.2+
- Enhanced logging system
- Improved error handling
- Better memory management
- Faster PDF generation
- Optimized data storage

## 📋 Table of Contents
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Configuration](#%EF%B8%8F-configuration)
- [Development](#-development)
- [Contributing](#-contributing)
- [Support](#-support)
- [License](#-license)

## 🚀 Features

### Core Functionality
- Modern and intuitive graphical user interface
- Professional PDF invoice generation
- Company profile management with logo support
- Automatic invoice numbering system
- Data persistence with JSON storage
- Automatic backups

### Invoice Management
- Create and edit invoices with real-time preview
- Customizable invoice templates
- Automatic calculations and VAT handling
- Multi-item invoice support
- Customer database management

### Localization & Compliance
- Multi-language support (Italian/English)
- Italian fiscal compliance features
- SDI (Sistema di Interscambio) support
- VAT number validation

### Data & Security
- Secure data storage
- Automatic backup system
- Export functionality
- Data validation and error prevention

## 📋 Prerequisites

### System Requirements
- Windows 10 or higher
- Python 3.8 or higher
- 4GB RAM minimum
- 100MB free disk space

### Required Python Packages
- tkinter (GUI framework)
- reportlab (PDF generation)
- pillow (Image processing)
- pytest (Testing)
- See `requirements.txt` for complete list

## 🔧 Installation

1. Clone this repository:
```bash
git clone https://github.com/flobbissimo/invoice_app.git
cd invoice_app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the application:
```bash
python -m src.setup
```

## 🎮 Usage

### Quick Start
1. Run the application:
```bash
.\run.bat
```

2. Configure your company profile:
   - Click "Configurazione" in the menu
   - Enter your company details
   - Upload your company logo

3. Create your first invoice:
   - Click "Nuova Ricevuta"
   - Fill in customer details
   - Add items
   - Save and generate PDF

### Running Modes

#### Production Mode
```bash
.\run.bat
```
- Optimized performance
- Error logging
- Production configuration

#### Development Mode
```bash
.\run_debug.bat
```
- Debug logging enabled
- Development configuration
- Real-time code reloading

## 📁 Project Structure

```
Invoice-App/
├── src/                    # Source code
│   ├── core/              # Core business logic
│   │   ├── pdf_generator.py   # PDF generation
│   │   └── storage_manager.py # Data persistence
│   ├── gui/               # GUI components
│   │   ├── main_window.py     # Main application window
│   │   └── invoice_form.py    # Invoice creation form
│   ├── models/            # Data models
│   │   └── invoice.py         # Invoice data model
│   └── utils/             # Utility functions
├── config/                # Configuration files
│   ├── default.json          # Default settings
│   └── company_config.json   # Company details
├── data/                  # Data storage
│   └── invoices/            # Invoice JSON files
├── logs/                  # Application logs
├── tests/                 # Test suite
│   └── test_invoice_model.py # Model unit tests
├── requirements.txt       # Python dependencies
├── run.bat               # Production startup
└── run_debug.bat         # Development startup
```

## 🛠️ Configuration

### Company Settings
- Company name and details
- VAT and fiscal information
- Invoice numbering format
- Logo and branding
- PDF template customization

### Application Settings
- Language preference
- Data storage location
- Backup frequency
- PDF output directory
- Log level configuration

## 💻 Development

### Testing
Run the test suite:
```bash
pytest tests/
```

### Code Style
Follow PEP 8 guidelines and use provided `.pylintrc`

### Documentation
- Code comments in English
- User documentation in Italian
- Follow Google Python Style Guide

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines
- Write meaningful commit messages
- Add tests for new features
- Update documentation
- Follow the code style guide

## 🆘 Support

- GitHub Issues: Bug reports and feature requests
- Email Support: [robertobondir3@gmail.com]
- Documentation: See `docs/` directory

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
Made with ❤️ by [Flobby/PensionFlora]