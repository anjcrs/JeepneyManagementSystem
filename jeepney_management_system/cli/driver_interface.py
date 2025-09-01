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
    # CLI for the Driver
    
    def __init__(self):
        self.fare_calculator = FareCalculator()
        self.analytics = AnalyticsService()
        self.jeepney_queries = JeepneyQueries()
        self.transaction_queries = TransactionQueries()
        self.validator = InputValidator()
        self.current_jeepney = None
    
    def run(self):
        # Main driver interface loop
        print("Jeepney Driver System")
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
                print("Thank you for using the system!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def show_main_menu(self):
        # Display main menu options
        print("\n" + "="*40)
        print("DRIVER MENU")
        print("="*60)
        print("1. 🧑‍🤝‍🧑 Process New Passenger")
        print("2. 🚶‍♂️ Passenger Alighting")
        print("3. 📊 Current Status")
        print("4. 📈 Daily Summary")
        print("5. 📒 Transaction Log")
        print("6. 🚪 Exit")
        
        if self.current_jeepney:
            occupancy = self.current_jeepney.get_current_occupancy()
            capacity = self.current_jeepney.capacity
            print(f"\nCurrent Passengers: {occupancy}/{capacity}")
    
    def setup_jeepney(self):
        # Setup current jeepney for the session
        print("\nJeepney Setup")
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
        print("\nNew Passenger Boarding")
        print("-" * 45)
        
        # Check capacity
        if self.current_jeepney.get_current_occupancy() >= self.current_jeepney.capacity:
            print("Jeepney is at full capacity!")
            return
        
        # Get passenger details
        passenger_type = self.get_passenger_type()
        if not passenger_type:
            return
        
        boarding_location = input("Boarding location: ").strip()
        
        # Calculate fare
        try:
            required_fare = self.fare_calculator.calculate_fare(passenger_type)
            print(f"Required fare: ₱{required_fare:.2f}")
            
            # Get payment
            amount_paid = self.get_payment_amount()
            if amount_paid is None:
                return
            
            # Validate payment
            payment_result = self.fare_calculator.validate_payment(required_fare, amount_paid)
            
            if not payment_result["valid"]:
                print(f"{payment_result['error']}")
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
                payment_status=payment_result["status"], 
                boarding_location=boarding_location
            )
            
            # Handle overpayment (ask for destination)
            if payment_result["status"] == "overpaid":
                destination = input("Passenger destination (for change): ").strip()
                passenger.set_destination(destination)
                transaction.destination = destination
                print(f"Change to give: ₱{payment_result['change']:.2f}")
            
            # Add to jeepney
            self.current_jeepney.add_passenger(passenger, transaction)
            
            # Save to database (in real implementation)
            # self.transaction_queries.save_transaction(transaction)
            
            print(f"Passenger {passenger_id} added successfully!")
            print(f"Current occupancy: {self.current_jeepney.get_current_occupancy()}/{self.current_jeepney.capacity}")
            
        except Exception as e:
            print(f"Error processing passenger: {str(e)}")
    
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
                    print("Invalid choice. Please select 1-4.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_payment_amount(self) -> float:
        # Get and validate payment amount
        while True:
            try:
                amount = float(input("Amount paid: ₱"))
                if amount < 0:
                    print("Amount cannot be negative.")
                    continue
                return amount
            except ValueError:
                print("Please enter a valid amount.")
    
    def passenger_alighting(self):
        """Handle passenger getting off the jeepney"""
        print("\nPassenger Alighting")
        print("-" * 20)
        
        if not self.current_jeepney.current_passengers:
            print("No passengers currently on board!")
            return
        
        # Show current passengers
        print("\nCurrent Passengers:")
        for i, passenger in enumerate(self.current_jeepney.current_passengers, 1):
            boarding_time = passenger.boarding_time.strftime("%H:%M")
            print(f"{i}. ID: {passenger.passenger_id} | "
                  f"Type: {passenger.passenger_type.title()} | "
                  f"Boarded: {boarding_time} | "
                  f"From: {passenger.boarding_location}")
        
        try:
            choice = int(input("\nSelect passenger to alight (number): "))
            if 1 <= choice <= len(self.current_jeepney.current_passengers):
                passenger = self.current_jeepney.current_passengers[choice - 1]
                
                # Optional: Record alighting location
                alighting_location = input("Alighting location (optional): ").strip()
                if alighting_location:
                    passenger.destination = alighting_location
                
                # Record alighting time
                passenger.alighting_time = datetime.now()
                
                # Remove passenger
                self.current_jeepney.remove_passenger(passenger.passenger_id)
                
                print(f"✅ Passenger {passenger.passenger_id} has alighted!")
                print(f"📊 Current occupancy: {self.current_jeepney.get_current_occupancy()}/{self.current_jeepney.capacity}")
            else:
                print("Invalid passenger selection.")
        except ValueError:
            print("Please enter a valid number.")
    
    def view_current_status(self):
        """Display current jeepney status"""
        print("\nCurrent Status")
        print("=" * 30)
        
        if not self.current_jeepney:
            print("No jeepney configured!")
            return
        
        # Basic info
        print(f"🚌 Jeepney: {self.current_jeepney.plate_number}")
        print(f"👨‍✈️ Driver: {self.current_jeepney.driver_name}")
        print(f"📍 Route: {self.current_jeepney.route_id}")
        print(f"⏰ Session started: {self.current_jeepney.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Occupancy status
        occupancy = self.current_jeepney.get_current_occupancy()
        capacity = self.current_jeepney.capacity
        occupancy_percent = (occupancy / capacity) * 100
        
        print(f"\nPassengers: {occupancy}/{capacity} ({occupancy_percent:.1f}%)")
        
        # Revenue summary
        daily_revenue = self.current_jeepney.get_daily_revenue()
        transaction_count = len(self.current_jeepney.daily_transactions)
        
        print(f"Daily Revenue: ₱{daily_revenue:.2f}")
        print(f"Transactions: {transaction_count}")
        
        if transaction_count > 0:
            avg_fare = daily_revenue / transaction_count
            print(f"Average Fare: ₱{avg_fare:.2f}")
        
        # Passenger breakdown
        passenger_counts = self.current_jeepney.get_passenger_count()
        print(f"\nPassenger Breakdown:")
        for ptype, count in passenger_counts.items():
            if count > 0:
                print(f"   {ptype.title()}: {count}")
    
    def view_daily_summary(self):
        """Display daily summary and analytics"""
        print("\nDaily Summary")
        print("=" * 45)
        
        if not self.current_jeepney.daily_transactions:
            print("No transactions recorded today!")
            return
        
        transactions = self.current_jeepney.daily_transactions
        
        # Time-based analysis
        hours = {}
        for transaction in transactions:
            hour = transaction.transaction_time.hour
            if hour not in hours:
                hours[hour] = {"count": 0, "revenue": 0}
            hours[hour]["count"] += 1
            hours[hour]["revenue"] += transaction.amount_paid
        
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"🚌 Jeepney: {self.current_jeepney.plate_number}")
        print(f"📍 Route: {self.current_jeepney.route_id}")
        
        # Overall stats
        total_revenue = sum(t.amount_paid for t in transactions)
        total_passengers = len(transactions)
        total_change = sum(t.change_given for t in transactions)
        
        print(f"\n💰 Total Revenue: ₱{total_revenue:.2f}")
        print(f"👥 Total Passengers: {total_passengers}")
        print(f"💵 Total Change Given: ₱{total_change:.2f}")
        print(f"📊 Net Revenue: ₱{total_revenue - total_change:.2f}")
        
        # Busiest hours
        if hours:
            busiest_hour = max(hours.items(), key=lambda x: x[1]["count"])
            print(f"Busiest Hour: {busiest_hour[0]:02d}:00 ({busiest_hour[1]['count']} passengers)")
        
        # Passenger type breakdown
        passenger_counts = self.current_jeepney.get_passenger_count()
        print(f"\nPassenger Types:")
        for ptype, count in passenger_counts.items():
            if count > 0:
                percentage = (count / total_passengers) * 100
                print(f"   {ptype.title()}: {count} ({percentage:.1f}%)")
        
        # Payment efficiency
        exact_payments = sum(1 for t in transactions if t.payment_status == "exact")
        efficiency = (exact_payments / total_passengers) * 100 if total_passengers > 0 else 0
        print(f"\n💡 Payment Efficiency: {efficiency:.1f}% exact payments")
    
    def view_transaction_log(self):
        """Display transaction history"""
        print("\nTransaction Log")
        print("=" * 50)
        
        if not self.current_jeepney.daily_transactions:
            print("No transactions recorded!")
            return
        
        print(f"{'Time':<8} {'ID':<8} {'Type':<8} {'Fare':<6} {'Paid':<6} {'Change':<6} {'Location':<15}")
        print("-" * 70)
        
        for transaction in self.current_jeepney.daily_transactions:
            time_str = transaction.transaction_time.strftime("%H:%M")
            print(f"{time_str:<8} "
                  f"{transaction.transaction_id[:8]:<8} "
                  f"{transaction.passenger_type[:8]:<8} "
                  f"₱{transaction.required_fare:<5.2f} "
                  f"₱{transaction.amount_paid:<5.2f} "
                  f"₱{transaction.change_given:<5.2f} "
                  f"{transaction.boarding_location[:15]:<15}")
        
        # Summary at bottom
        total_revenue = sum(t.amount_paid for t in self.current_jeepney.daily_transactions)
        total_change = sum(t.change_given for t in self.current_jeepney.daily_transactions)
        
        print("-" * 70)
        print(f"{'TOTALS':<8} {'':<8} {'':<8} {'':<6} ₱{total_revenue:<5.2f} ₱{total_change:<5.2f}")
        print(f"Net Revenue: ₱{total_revenue - total_change:.2f}")
    
    def show_current_passengers(self):
        """Display currently boarded passengers (helper method)"""
        if not self.current_jeepney.current_passengers:
            print("No passengers currently on board.")
            return
        
        print(f"\nCurrent Passengers ({len(self.current_jeepney.current_passengers)}):")
        print("-" * 50)
        
        for i, passenger in enumerate(self.current_jeepney.current_passengers, 1):
            boarding_time = passenger.boarding_time.strftime("%H:%M")
            travel_duration = (datetime.now() - passenger.boarding_time).total_seconds() / 60
            
            print(f"{i:2d}. ID: {passenger.passenger_id} | "
                  f"Type: {passenger.passenger_type.title():<8} | "
                  f"Boarded: {boarding_time} ({travel_duration:.0f}m ago)")
            print(f"     From: {passenger.boarding_location}")
            if passenger.destination:
                print(f"     To: {passenger.destination}")
    
    def quick_stats_display(self):
        # How quick stats in a compact format
        if not self.current_jeepney:
            return
        
        occupancy = self.current_jeepney.get_current_occupancy()
        daily_revenue = self.current_jeepney.get_daily_revenue()
        transaction_count = len(self.current_jeepney.daily_transactions)
        
        print(f"Quick Stats: {occupancy}/20 passengers | "
              f"₱{daily_revenue:.2f} revenue | "
              f"{transaction_count} trips")

# Helper class for better user experience
class DisplayHelper:
    # Helper methods for improved console display
    
    @staticmethod
    def print_header(title: str, width: int = 40):
        # Print a formatted header
        print("\n" + "=" * width)
        print(f"{title:^{width}}")
        print("=" * width)
    
    @staticmethod
    def print_divider(char: str = "-", length: int = 30):
        # Prints a divider line
        print(char * length)
    
    @staticmethod
    def format_currency(amount: float) -> str:
        # Format currency for display
        return f"₱{amount:.2f}"
    
    @staticmethod
    def format_time(dt: datetime) -> str:
        """Format datetime for display"""
        return dt.strftime("%H:%M:%S")

# Enhanced input validation for better UX
class DriverInputValidator:
    # Enhanced input validation specifically for driver interface
    
    @staticmethod
    def get_valid_choice(prompt: str, valid_range: range) -> int:
        # Get a valid integer choice within range
        while True:
            try:
                choice = int(input(prompt))
                if choice in valid_range:
                    return choice
                else:
                    print(f"Please enter a number between {min(valid_range)} and {max(valid_range)}.")
            except ValueError:
                print("Please enter a valid number.")
    
    @staticmethod
    def get_valid_amount(prompt: str, min_amount: float = 0) -> float:
        """Get a valid monetary amount"""
        while True:
            try:
                amount = float(input(prompt))
                if amount >= min_amount:
                    return amount
                else:
                    print(f"Amount must be at least ₱{min_amount:.2f}")
            except ValueError:
                print("Please enter a valid amount (e.g., 15.00)")
    
    @staticmethod
    def confirm_action(prompt: str) -> bool:
        """Get yes/no confirmation"""
        while True:
            response = input(f"{prompt} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")