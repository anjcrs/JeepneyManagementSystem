from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    """Represents a fare transaction"""
    transaction_id: str
    jeepney_id: str
    passenger_type: str
    required_fare: float
    amount_paid: float
    change_given: float
    payment_status: str  # exact, overpaid, underpaid
    boarding_location: str
    destination: Optional[str] = None
    transaction_time: datetime = None
    
    def __post_init__(self):
        if self.transaction_time is None:
            self.transaction_time = datetime.now()
        
        # Calculate change and status
        if self.amount_paid == self.required_fare:
            self.payment_status = "exact"
            self.change_given = 0
        elif self.amount_paid > self.required_fare:
            self.payment_status = "overpaid"
            self.change_given = self.amount_paid - self.required_fare
        else:
            self.payment_status = "underpaid"
            self.change_given = 0
    
    def is_valid_payment(self) -> bool:
        """Check if payment is sufficient"""
        return self.amount_paid >= self.required_fare
    
    def get_transaction_summary(self) -> dict:
        """Get transaction summary"""
        return {
            "id": self.transaction_id,
            "type": self.passenger_type,
            "fare": self.required_fare,
            "paid": self.amount_paid,
            "change": self.change_given,
            "status": self.payment_status,
            "time": self.transaction_time.strftime("%H:%M:%S")
        }