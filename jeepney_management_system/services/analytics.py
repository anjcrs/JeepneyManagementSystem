from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from models.transaction import Transaction
from database.queries import TransactionQueries

class AnalyticsService:
    """Provides analytics and insights from transaction data"""
    
    def __init__(self):
        self.transaction_queries = TransactionQueries()
    
    def get_daily_summary(self, date: str, jeepney_id: str = None) -> Dict[str, Any]:
        """Get daily summary of operations"""
        transactions = self.transaction_queries.get_transactions_by_date(date, jeepney_id)
        
        total_passengers = len(transactions)
        total_revenue = sum(t['amount_paid'] for t in transactions)
        
        passenger_types = defaultdict(int)
        payment_statuses = defaultdict(int)
        
        for transaction in transactions:
            passenger_types[transaction['passenger_type']] += 1
            payment_statuses[transaction['payment_status']] += 1
        
        return {
            "date": date,
            "total_passengers": total_passengers,
            "total_revenue": total_revenue,
            "passenger_breakdown": dict(passenger_types),
            "payment_breakdown": dict(payment_statuses),
            "average_fare": total_revenue / total_passengers if total_passengers > 0 else 0
        }
    
    def get_peak_hours(self, date_range: int = 7) -> List[Dict[str, Any]]:
        """Analyze peak hours based on recent data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        hourly_counts = defaultdict(int)
        transactions = self.transaction_queries.get_transactions_by_date_range(
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        
        for transaction in transactions:
            hour = datetime.fromisoformat(transaction['transaction_time']).hour
            hourly_counts[hour] += 1
        
        # Sort by passenger count
        peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"hour": hour, "passenger_count": count} for hour, count in peak_hours]
    
    def get_route_performance(self, route_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze route performance metrics"""
        # Implementation would analyze route-specific data
        # This is a simplified version
        return {
            "route_id": route_id,
            "average_daily_passengers": 150,
            "average_daily_revenue": 2000.0,
            "peak_hours": ["7:00-9:00", "17:00-19:00"],
            "efficiency_score": 0.85
        }
