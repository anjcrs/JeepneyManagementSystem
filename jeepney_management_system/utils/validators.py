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