from config import Config
from typing import Optional


class FareCalculator:
    # Handles fare calculations and validations
    
    def __init__(self):
        self.base_fares = Config.BASE_FARES
    
    def calculate_fare(self, passenger_type: str) -> float:
        # Calculates fares based on passenger type
        
        if passenger_type not in self.base_fares:
            raise ValueError(f"Invalid passenger type: {passenger_type}")
        
        return self.base_fares[passenger_type]
    
    def validate_payment(self, required_fare: float, amount_paid: float) -> dict:
        # Validate payment and calculate change
        
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
