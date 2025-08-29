# =============================================================================
# 1. services/fare_calculator.py - PUT THIS CODE IN YOUR FILE
# =============================================================================

from jeepney_management_system.config import Config
from typing import Optional

class FareCalculator:
    """Handles fare calculations and validations"""
    
    def __init__(self):
        self.base_fares = Config.BASE_FARES
    
    def calculate_fare(self, passenger_type: str) -> float:
        """Calculate fare based on passenger type"""
        
        if passenger_type not in self.base_fares:
            raise ValueError(f"Invalid passenger type: {passenger_type}")
        
        return self.base_fares[passenger_type]
    
    def validate_payment(self, required_fare: float, amount_paid: float) -> dict:
        """Validate payment and calculate change"""
        
        if amount_paid < 0:
            return {"valid": False, "error": "Invalid amount"}
        
        if amount_paid < required_fare:
            shortage = required_fare - amount_paid
            return {
                "valid": False, 
                "error": f"Insufficient payment. Short by ₱{shortage:.2f}"
            }
        
        change = amount_paid - required_fare
        return {
            "valid": True,
            "change": change,
            "status": "exact" if change == 0 else "overpaid"
        }

# =============================================================================
# 2. utils/validators.py - PUT THIS CODE IN YOUR FILE
# =============================================================================

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_passenger_type(passenger_type: str) -> bool:
        """Validate passenger type"""
        valid_types = ["regular", "student", "senior", "pwd"]
        return passenger_type.lower() in valid_types
    
    @staticmethod
    def validate_amount(amount: str) -> tuple:
        """Validate monetary amount"""
        try:
            value = float(amount)
            if value < 0:
                return False, "Amount cannot be negative"
            return True, value
        except ValueError:
            return False, "Invalid amount format"
    
    @staticmethod
    def validate_plate_number(plate: str) -> bool:
        """Basic plate number validation"""
        return len(plate.strip()) >= 3