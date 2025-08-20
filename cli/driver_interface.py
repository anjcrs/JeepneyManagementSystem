import uuid
from datetime import datetime
from services.fare_calculator import FareCalculator
from services.analytics import AnalyticsService
from database.queries import JeepneyQueries, TransactionQueries
from models.jeepney import Jeepney
from models.passenger import Passenger
from models.transaction import Transaction
from utils.validators import InputValidator

class DriverInterface:
    """Command-line interface for jeepney drivers"""
    
    def __init__(self):
        self.fare_calculator = FareCalculator()
        self.analytics = AnalyticsService()
        self.jeepney_queries = JeepneyQueries()
        self.transaction_queries = TransactionQueries()
        self.validator = InputValidator()
        self.current_jeepney = None
    
    def run(self):
        """Main driver interface loop"""
        print("🚌 Jeepney Driver System")
        print("=" * 30)
        
        # Initialize jeepney
        self.setup_jeepney()
        
        while True:
            self.show_main_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "1":
                self.process_passenger()
            elif choice == "2":
                self.passenger_alighting()
            elif choice == "3":
                self.view_current_status()
            elif choice == "4":
                self.view_daily_summary()
            elif choice == "5":
                self.view_transaction_log()
            elif choice == "6":
                print("👋 Thank you for using the system!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def show_main_menu(self):
        """Display main menu options"""
        print("\n" + "="*40)
        print("📋 DRIVER MENU")
        print("="*40)
        print("1. 🧑‍🤝‍🧑 Process New Passenger")
        print("2. 🚶‍♂️ Passenger Alighting")
        print("3. 📊 Current Status")
        print("4. 📈 Daily Summary")
        print("5. 📒 Transaction Log")
        print("6. 🚪 Exit")
        
        if self.current_jeepney:
            occupancy = self.current_jeepney.get_current_occupancy()
            capacity = self.current_jeepney.capacity
            print(f"\n🚌 Current Passengers: {occupancy}/{capacity}")
    
    def setup_jeepney(self):
        """Setup current jeepney for the session"""
        print("\n🚌 Jeepney Setup")
        plate_number = input("Enter jeepney plate number: ").strip().upper()
        driver_name = input("Enter driver name: ").strip()
        route_id = input("Enter route (e.g., 01A, 02B): ").strip().upper()
        
        jeepney_id = f"JP_{plate_number}_{datetime.now().strftime('%Y%m%d')}"
        
        self.current_jeepney = Jeepney(
            jeepney_id=jeepney_id,
            plate_number=plate_number,
            driver_name=driver_name,
            route_id=route_id
        )
        
        print(f"✅ Jeepney {plate_number} setup complete!")
        print(f"📍 Route: {route_id}")
        print(f"👨‍✈️ Driver: {driver_name}")
    
    def process_passenger(self):
        """Process new passenger boarding"""
        print("\n🧑‍🤝‍🧑 New Passenger Boarding")
        print("-" * 25)
        
        # Check capacity
        if self.current_jeepney.get_current_occupancy() >= self.current_jeepney.capacity:
            print("❌ Jeepney is at full capacity!")
            return
        
        # Get passenger details
        passenger_type = self.get_passenger_type()
        if not passenger_type:
            return
        
        boarding_location = input("📍 Boarding location: ").strip()
        
        # Calculate fare
        try:
            required_fare = self.fare_calculator.calculate_fare(passenger_type)
            print(f"💰 Required fare: ₱{required_fare:.2f}")
            
            # Get payment
            amount_paid = self.get_payment_amount()
            if amount_paid is None:
                return
            
            # Validate payment
            payment_result = self.fare_calculator.validate_payment(required_fare, amount_paid)
            
            if not payment_result["valid"]:
                print(f"❌ {payment_result['error']}")
                return
            
            # Create passenger and transaction
            passenger_id = str(uuid.uuid4())[:8]
            
            passenger = Passenger(
                passenger_id=passenger_id,
                passenger_type=passenger_type,
                boarding_location=boarding_location
            )
            
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                jeepney_id=self.current_jeepney.jeepney_id,
                passenger_type=passenger_type,
                required_fare=required_fare,
                amount_paid=amount_paid,
                change_given=payment_result.get("change", 0),
                boarding_location=boarding_location
            )
            
            # Handle overpayment (ask for destination)
            if payment_result["status"] == "overpaid":
                destination = input("🎯 Passenger destination (for change): ").strip()
                passenger.set_destination(destination)
                transaction.destination = destination
                print(f"💵 Change to give: ₱{payment_result['change']:.2f}")
            
            # Add to jeepney
            self.current_jeepney.add_passenger(passenger, transaction)
            
            # Save to database (in real implementation)
            # self.transaction_queries.save_transaction(transaction)
            
            print(f"✅ Passenger {passenger_id} added successfully!")
            print(f"📊 Current occupancy: {self.current_jeepney.get_current_occupancy()}/{self.current_jeepney.capacity}")
            
        except Exception as e:
            print(f"❌ Error processing passenger: {str(e)}")
    
    def get_passenger_type(self) -> str:
        """Get and validate passenger type"""
        valid_types = ["regular", "student", "senior", "pwd"]
        
        while True:
            print("\nPassenger Types:")
            for i, ptype in enumerate(valid_types, 1):
                print(f"{i}. {ptype.title()}")
            
            try:
                choice = int(input("Select passenger type (1-4): "))
                if 1 <= choice <= 4:
                    return valid_types[choice - 1]
                else:
                    print("❌ Invalid choice. Please select 1-4.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def get_payment_amount(self) -> float:
        """Get and validate payment amount"""
        while True:
            try:
                amount = float(input("💵 Amount paid: ₱"))
                if amount < 0:
                    print("❌ Amount cannot be negative.")
                    continue
                return amount
            except ValueError:
                print("❌ Please enter a valid amount.")