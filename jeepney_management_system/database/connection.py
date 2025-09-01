import sqlite3
import os
from contextlib import contextmanager
from config import Config

class DatabaseManager:
    # This handles database connections and operations
    
    def __init__(self):
        self.db_path = Config.DATABASE_URL.replace('sqlite:///', '')
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        # This creates a database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        # Context manager for database connections
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        # Execute a single query
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()
    
    def execute_many(self, query: str, params_list: list):
        # Execute multiple queries with different parameters
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
