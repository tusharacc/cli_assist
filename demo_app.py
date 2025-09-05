#!/usr/bin/env python3
"""Demo application with intentional bug for testing Lumos CLI debugging"""

import sqlite3
import os

class UserManager:
    def __init__(self):
        # Bug: database path is incorrect, missing .db extension
        self.db_path = "users"  # Should be "users.db"
        self.setup_database()
    
    def setup_database(self):
        """Initialize the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bug: SQL syntax error - missing comma between columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, name, email):
        """Add a new user to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Bug: Using format string instead of parameterized query (SQL injection risk)
            cursor.execute(f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')")
            conn.commit()
            print(f"User {name} added successfully")
        except Exception as e:
            print(f"Error adding user: {e}")
        finally:
            conn.close()
    
    def get_user(self, email):
        """Get user by email"""
        conn = sqlite3.connect(self.db_path) 
        cursor = conn.cursor()
        
        # Bug: Not handling case when user is not found
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        conn.close()
        return user[0]  # This will crash if user is None

def main():
    """Main application"""
    user_manager = UserManager()
    
    # Try to add some users
    user_manager.add_user("John Doe", "john@example.com")
    user_manager.add_user("Jane Smith", "jane@example.com")
    
    # Try to get a user (this will fail)
    user = user_manager.get_user("nonexistent@example.com")
    print(f"Found user: {user}")

if __name__ == "__main__":
    main()