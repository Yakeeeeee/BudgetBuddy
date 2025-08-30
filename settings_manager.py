"""
Settings Manager for Budget Tracker
Handles application settings persistence and configuration
"""

import json
import os
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime


class SettingsManager:
    def __init__(self):
        self.settings_file = "data/settings.json"
        self.csv_settings_file = "data/settings.csv"
        self.ensure_settings_directory()
        self.default_settings = self.get_default_settings()
    
    def ensure_settings_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists("data"):
            os.makedirs("data")
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings"""
        return {
            'theme': 'dark',
            'currency': 'PHP',
            'date_format': '%Y-%m-%d',
            # 'logo_path': None,  # Removed logo setting
            'window_geometry': '1400x800',
            'auto_save': True,
            'backup_frequency': 7,  # days
            'last_backup': None,
            'notifications_enabled': True,
            'budget_alerts': True,
            'overspending_alert_threshold': 10,  # percentage over budget
            'currency_symbol': '₱',
            'decimal_places': 2,
            'first_time_setup': True,
            'language': 'en',
            'export_format': 'xlsx',
            'chart_style': 'default',
            'sidebar_expanded': True,
            'default_page': 'dashboard',
            'income_categories': [
                'Salary',
                'Freelance',
                'Investments',
                'Business',
                'Other'
            ],
            'essential_categories': [
                'Housing',
                'Utilities',
                'Groceries',
                'Transportation',
                'Insurance',
                'Healthcare',
                'Debt Payments'
            ],
            'non_essential_categories': [
                'Entertainment',
                'Dining Out',
                'Shopping',
                'Hobbies',
                'Travel',
                'Subscriptions',
                'Personal Care'
            ]
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_settings = self.default_settings.copy()
                merged_settings.update(settings)
                return merged_settings
            else:
                # Try loading from CSV for backward compatibility
                return self.load_settings_from_csv()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def load_settings_from_csv(self) -> Dict[str, Any]:
        """Load settings from CSV file (backward compatibility)"""
        try:
            if os.path.exists(self.csv_settings_file):
                df = pd.read_csv(self.csv_settings_file)
                settings = self.default_settings.copy()
                
                for _, row in df.iterrows():
                    key = row['Key']
                    value = row['Value']
                    
                    # Convert string values to appropriate types
                    if key in ['auto_save', 'notifications_enabled', 'budget_alerts', 'first_time_setup', 'sidebar_expanded']:
                        settings[key] = str(value).lower() == 'true'
                    elif key in ['backup_frequency', 'overspending_alert_threshold', 'decimal_places']:
                        settings[key] = int(value) if value else self.default_settings[key]
                    elif key in ['income_categories', 'essential_categories', 'non_essential_categories']:
                        # Handle list values
                        try:
                            settings[key] = json.loads(value) if value else self.default_settings[key]
                        except:
                            settings[key] = self.default_settings[key]
                    else:
                        settings[key] = value if value else self.default_settings[key]
                
                return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading CSV settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save settings to JSON file"""
        try:
            # Ensure data directory exists
            self.ensure_settings_directory()
            
            # Save to JSON
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4, default=str)
            
            # Also save to CSV for compatibility
            self.save_settings_to_csv(settings)
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            raise Exception(f"Failed to save settings: {e}")
    
    def save_settings_to_csv(self, settings: Dict[str, Any]):
        """Save settings to CSV file for compatibility"""
        try:
            data = []
            for key, value in settings.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                elif isinstance(value, bool):
                    value = str(value).lower()
                data.append({'Key': key, 'Value': value})
            
            df = pd.DataFrame(data)
            df.to_csv(self.csv_settings_file, index=False)
            
        except Exception as e:
            print(f"Error saving CSV settings: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        settings = self.load_settings()
        return settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a specific setting value"""
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.save_settings(self.default_settings.copy())
    
    def export_settings(self, export_path: str):
        """Export settings to a file"""
        settings = self.load_settings()
        
        if export_path.endswith('.json'):
            with open(export_path, 'w') as f:
                json.dump(settings, f, indent=4, default=str)
        elif export_path.endswith('.csv'):
            data = []
            for key, value in settings.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                data.append({'Key': key, 'Value': str(value)})
            df = pd.DataFrame(data)
            df.to_csv(export_path, index=False)
        else:
            raise ValueError("Unsupported export format. Use .json or .csv")
    
    def import_settings(self, import_path: str):
        """Import settings from a file"""
        if not os.path.exists(import_path):
            raise FileNotFoundError(f"Settings file not found: {import_path}")
        
        if import_path.endswith('.json'):
            with open(import_path, 'r') as f:
                imported_settings = json.load(f)
        elif import_path.endswith('.csv'):
            df = pd.read_csv(import_path)
            imported_settings = {}
            for _, row in df.iterrows():
                key = row['Key']
                value = row['Value']
                try:
                    # Try to parse as JSON for complex types
                    imported_settings[key] = json.loads(value)
                except:
                    imported_settings[key] = value
        else:
            raise ValueError("Unsupported import format. Use .json or .csv")
        
        # Merge with current settings
        current_settings = self.load_settings()
        current_settings.update(imported_settings)
        self.save_settings(current_settings)
    
    def get_theme_settings(self) -> Dict[str, str]:
        """Get theme-specific settings"""
        settings = self.load_settings()
        theme = settings.get('theme', 'dark')
        
        if theme == 'light':
            return {
                'bg_color': '#ffffff',
                'fg_color': '#000000',
                'button_color': '#e1e1e1',
                'button_hover': '#d4edda',
                'accent_color': '#007bff'
            }
        else:
            return {
                'bg_color': '#2b2b2b',
                'fg_color': '#ffffff',
                'button_color': '#404040',
                'button_hover': '#4a4a4a',
                'accent_color': '#1f538d'
            }
    
    def get_currency_settings(self) -> Dict[str, str]:
        """Get currency formatting settings"""
        settings = self.load_settings()
        return {
            'symbol': settings.get('currency_symbol', '₱'),
            'code': settings.get('currency', 'PHP'),
            'decimal_places': settings.get('decimal_places', 2)
        }
    
    def format_currency(self, amount: float) -> str:
        """Format amount as currency based on settings"""
        currency = self.get_currency_settings()
        symbol = currency['symbol']
        decimal_places = currency['decimal_places']
        
        return f"{symbol}{amount:,.{decimal_places}f}"
    
    def get_date_format(self) -> str:
        """Get date format setting"""
        return self.get_setting('date_format', '%Y-%m-%d')
    
    def format_date(self, date) -> str:
        """Format date based on settings"""
        date_format = self.get_date_format()
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d')
            except:
                return str(date)
        
        return date.strftime(date_format)
    
    def should_show_backup_reminder(self) -> bool:
        """Check if backup reminder should be shown"""
        settings = self.load_settings()
        last_backup = settings.get('last_backup')
        backup_frequency = settings.get('backup_frequency', 7)
        
        if not last_backup:
            return True
        
        try:
            last_backup_date = datetime.strptime(last_backup, '%Y-%m-%d')
            days_since_backup = (datetime.now() - last_backup_date).days
            return days_since_backup >= backup_frequency
        except:
            return True
    
    def update_last_backup(self):
        """Update the last backup date"""
        self.set_setting('last_backup', datetime.now().strftime('%Y-%m-%d'))
    
    def get_budget_alert_settings(self) -> Dict[str, Any]:
        """Get budget alert settings"""
        settings = self.load_settings()
        return {
            'enabled': settings.get('budget_alerts', True),
            'threshold': settings.get('overspending_alert_threshold', 10),
            'notifications': settings.get('notifications_enabled', True)
        }
    
    def get_category_suggestions(self, category_type: str) -> list:
        """Get category suggestions based on type"""
        settings = self.load_settings()
        
        category_map = {
            'income': 'income_categories',
            'essentials': 'essential_categories',
            'non_essentials': 'non_essential_categories'
        }
        
        key = category_map.get(category_type)
        if key:
            return settings.get(key, [])
        return []
    
    def add_custom_category(self, category_type: str, category_name: str):
        """Add a custom category to suggestions"""
        categories = self.get_category_suggestions(category_type)
        if category_name not in categories:
            categories.append(category_name)
            
            category_map = {
                'income': 'income_categories',
                'essentials': 'essential_categories',
                'non_essentials': 'non_essential_categories'
            }
            
            key = category_map.get(category_type)
            if key:
                self.set_setting(key, categories)
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, list]:
        """Validate settings and return any issues"""
        issues = {}
        
        # Validate theme
        if settings.get('theme') not in ['light', 'dark']:
            issues.setdefault('theme', []).append('Invalid theme value')
        
        # Validate numeric values
        numeric_fields = {
            'backup_frequency': (1, 365),
            'overspending_alert_threshold': (0, 100),
            'decimal_places': (0, 4)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            value = settings.get(field)
            if value is not None:
                try:
                    num_value = float(value)
                    if not (min_val <= num_value <= max_val):
                        issues.setdefault(field, []).append(
                            f'Value must be between {min_val} and {max_val}'
                        )
                except (ValueError, TypeError):
                    issues.setdefault(field, []).append('Must be a valid number')
        
        # Validate logo path (removed)
        # logo_path = settings.get('logo_path')
        # if logo_path and not os.path.exists(logo_path):
        #     issues.setdefault('logo_path', []).append('Logo file does not exist')
        
        return issues
    
    def migrate_settings(self):
        """Migrate settings from older versions"""
        settings = self.load_settings()
        
        # Add any new default settings that might be missing
        updated = False
        for key, value in self.default_settings.items():
            if key not in settings:
                settings[key] = value
                updated = True
        
        if updated:
            self.save_settings(settings)
        
        return updated
