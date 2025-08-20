import sys
import argparse
from cli.driver_interface import DriverInterface
from cli.admin_interface import AdminInterface
from web.app import create_web_app
from database.connection import DatabaseManager
from database.migrations import setup_database

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Jeepney Management System')
    parser.add_argument('--mode', choices=['driver', 'admin', 'web'], 
                       default='driver', help='Application mode')
    parser.add_argument('--setup-db', action='store_true', 
                       help='Setup database tables')
    
    args = parser.parse_args()
    
    # Initialize database
    if args.setup_db:
        setup_database()
        print("✅ Database setup complete!")
        return
    
    # Run application based on mode
    if args.mode == 'driver':
        driver_app = DriverInterface()
        driver_app.run()
    elif args.mode == 'admin':
        admin_app = AdminInterface()
        admin_app.run()
    elif args.mode == 'web':
        web_app = create_web_app()
        web_app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()