"""
Settings Manager - Handles application configuration
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

class SettingsManager:
    """Manages application settings and configuration"""
    
    DEFAULT_SETTINGS = {
        "company_details": {
            "company_name": "",
            "address": "",
            "city": "",
            "postal_code": "",
            "country": "",
            "vat_number": "",
            "phone": "",
            "email": "",
            "website": "",
            "sdi": "",
            "billing_number": ""
        },
        "pdf_settings": {
            "font_size": 10,
            "page_size": "A4",
            "margin_top": 2.0,
            "margin_bottom": 2.0,
            "margin_left": 2.0,
            "margin_right": 2.0
        },
        "application": {
            "language": "it",
            "theme": "default",
            "auto_backup": True,
            "backup_interval": 24,  # hours
            "pdf_viewer": "system_default"
        },
        "paths": {
            "data_dir": "data",
            "config_dir": "config",
            "backup_dir": "data/backups"
        }
    }
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.settings_file = self.config_dir / "settings.json"
        self.company_file = self.config_dir / "company_details.json"
        self._ensure_directories()
        self.settings = self._load_settings()
        
    def _ensure_directories(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all settings exist
                return self._merge_settings(self.DEFAULT_SETTINGS, settings)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default settings
            self.save_settings(self.DEFAULT_SETTINGS)
            return self.DEFAULT_SETTINGS.copy()
            
    def _merge_settings(self, default: Dict, current: Dict) -> Dict:
        """Recursively merge settings with defaults"""
        result = default.copy()
        
        for key, value in current.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def save_settings(self, settings: Dict[str, Any]):
        """Save settings to file"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        self.settings = settings
        
    def get_setting(self, *keys: str, default: Any = None) -> Any:
        """Get setting value by key path"""
        current = self.settings
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
        
    def set_setting(self, *keys: str, value: Any):
        """Set setting value by key path"""
        if not keys:
            return
            
        current = self.settings
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        self.save_settings(self.settings)
        
    def get_company_details(self) -> Dict[str, str]:
        """Get company details"""
        try:
            with open(self.company_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.settings['company_details']
            
    def save_company_details(self, details: Dict[str, str]):
        """Save company details"""
        with open(self.company_file, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        self.settings['company_details'] = details
        self.save_settings(self.settings)
        
    def get_data_dir(self) -> Path:
        """Get data directory path"""
        return Path(self.get_setting('paths', 'data_dir'))
        
    def get_backup_dir(self) -> Path:
        """Get backup directory path"""
        return Path(self.get_setting('paths', 'backup_dir'))
        
    def should_auto_backup(self) -> bool:
        """Check if auto backup is enabled"""
        return self.get_setting('application', 'auto_backup', default=True)
        
    def get_backup_interval(self) -> int:
        """Get backup interval in hours"""
        return self.get_setting('application', 'backup_interval', default=24) 