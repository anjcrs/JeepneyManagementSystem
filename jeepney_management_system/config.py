import os
from datetime import datetime

class Config:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/jeepney_database.db')
    
    # Fare Settings
    BASE_FARES = {
        "regular": 13.00,
        "student": 11.00,
        "senior": 11.00,
        "pwd": 11.00
    }
    
    # System Settings
    MAX_PASSENGERS = 20
    CURRENCY = "PHP"
    TIMEZONE = "Asia/Manila"
    
    # Web Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    WEB_HOST = '0.0.0.0'
    WEB_PORT = 5000
    
    # Reportings
    REPORTS_DIR = "reports/"
    BACKUP_DIR = "backups/"
    
    @staticmethod
    def get_current_date():
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def get_current_datetime():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")