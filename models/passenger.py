from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Passenger:
    """Represents a passenger"""
    passenger_id: str
    passenger_type: str  # regular, student, senior, pwd
    boarding_location: str
    destination: Optional[str] = None
    boarding_time: datetime = None
    
    def __post_init__(self):
        if self.boarding_time is None:
            self.boarding_time = datetime.now()
    
    def set_destination(self, destination: str):
        """Set passenger destination"""
        self.destination = destination
    
    def get_travel_duration(self) -> Optional[float]:
        """Get travel duration in minutes"""
        if hasattr(self, 'alighting_time'):
            duration = (self.alighting_time - self.boarding_time).total_seconds()
            return duration / 60  # Convert to minutes
        return None
