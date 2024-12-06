# Windsurf Invoice Manager

A professional invoice management system designed specifically for windsurf businesses. This application provides an intuitive graphical interface for creating, managing, and tracking invoices.

## 🚀 Features

- Modern and intuitive graphical user interface
- Company profile management
- Invoice generation with customizable templates
- PDF export functionality
- Data persistence and backup
- Multi-language support (Italian/English)

## 📋 Prerequisites

- Python 3.8 or higher
- Windows OS (tested on Windows 10)
- Required Python packages (see requirements.txt)

## 🔧 Installation

1. Clone this repository:
```bash
git clone [repository-url]
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

## 🎮 Usage

### Development Mode
Run the application in debug mode:
```bash
.\run_debug.bat
```

### Production Mode
Run the application in production mode:
```bash
.\run.bat
```

## 📁 Project Structure

```
windsurf-project/
├── src/                    # Source code
│   ├── core/              # Core business logic
│   ├── gui/               # GUI components
│   ├── models/            # Data models
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── data/                  # Data storage
├── logs/                  # Application logs
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## 🛠️ Configuration

The application can be configured through:
- Company profile settings in the GUI
- Configuration files in the `config/` directory

## 📝 Logging

Logs are stored in the `logs/` directory and include:
- Application events
- Error tracking
- User actions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and bug reports, please open an issue in the project repository.