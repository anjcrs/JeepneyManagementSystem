from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from models.passenger import Passenger
from models.transaction import Transaction

@dataclass
class Jeepney:
    """Represents a jeepney unit"""
    jeepney_id: str
    plate_number: str
    driver_name: str
    route_id: str
    capacity: int = 20
    current_passengers: List[Passenger] = field(default_factory=list)
    daily_transactions: List[Transaction] = field(default_factory=list)
    status: str = "active"  # active, maintenance, inactive
    
    def __post_init__(self):
        self.created_at = datetime.now()
    
    def add_passenger(self, passenger: Passenger, transaction: Transaction):
        """Add passenger and record transaction"""
        if len(self.current_passengers) >= self.capacity:
            raise ValueError("Jeepney at full capacity!")
        
        self.current_passengers.append(passenger)
        self.daily_transactions.append(transaction)
    
    def remove_passenger(self, passenger_id: str):
        """Remove passenger when they alight"""
        self.current_passengers = [p for p in self.current_passengers 
                                 if p.passenger_id != passenger_id]
    
    def get_current_occupancy(self) -> int:
        """Get current number of passengers"""
        return len(self.current_passengers)
    
    def get_daily_revenue(self) -> float:
        """Calculate total revenue for the day"""
        return sum(t.amount_paid for t in self.daily_transactions)
    
    def get_passenger_count(self) -> dict:
        """Get passenger count by type"""
        counts = {"regular": 0, "student": 0, "senior": 0, "pwd": 0}
        for transaction in self.daily_transactions:
            if transaction.passenger_type in counts:
                counts[transaction.passenger_type] += 1
        return counts