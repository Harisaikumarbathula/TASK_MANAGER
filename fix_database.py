#!/usr/bin/env python3
"""
Database Fix Script for Task Manager App
This script will fix the database structure to include user authentication.
"""

import mysql.connector
from werkzeug.security import generate_password_hash

# Database configuration - update these with your MySQL credentials
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'todo_app'
}

def fix_database():
    """Fix the database structure to include user authentication"""
    try:
        print("Connecting to database...")
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        print("Creating database if it doesn't exist...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS todo_app")
        cursor.execute("USE todo_app")
        
        # Create users table
        print("Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if tasks table exists and has user_id column
        cursor.execute("SHOW TABLES LIKE 'tasks'")
        tasks_exists = cursor.fetchone()
        
        if tasks_exists:
            print("Tasks table exists. Checking for user_id column...")
            cursor.execute("SHOW COLUMNS FROM tasks LIKE 'user_id'")
            user_id_exists = cursor.fetchone()
            
            if not user_id_exists:
                print("Adding user_id column to tasks table...")
                cursor.execute("ALTER TABLE tasks ADD COLUMN user_id INT")
                
                # Create a default user
                print("Creating default user...")
                default_password = generate_password_hash("default123")
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    ("default_user", "default@example.com", default_password)
                )
                default_user_id = cursor.lastrowid
                print(f"Default user created with ID: {default_user_id}")
                
                # Update existing tasks to belong to default user
                cursor.execute("UPDATE tasks SET user_id = %s WHERE user_id IS NULL", (default_user_id,))
                print(f"Updated {cursor.rowcount} existing tasks to belong to default user.")
                
                # Make user_id NOT NULL
                cursor.execute("ALTER TABLE tasks MODIFY COLUMN user_id INT NOT NULL")
                
                # Add foreign key constraint
                cursor.execute("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE")
                print("Foreign key constraint added.")
            else:
                print("user_id column already exists in tasks table.")
        else:
            print("Creating tasks table with user_id...")
            cursor.execute("""
                CREATE TABLE tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            print("Tasks table created successfully!")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✅ Database fixed successfully!")
        print("\nDefault login credentials:")
        print("Username: default_user")
        print("Password: default123")
        print("\nYou can now run the Flask app with: python app.py")
        
    except mysql.connector.Error as e:
        print(f"❌ Error fixing database: {e}")
        print("\nPlease check your MySQL connection settings in the script.")

if __name__ == "__main__":
    print("🔧 Task Manager Database Fix Script")
    print("=" * 40)
    fix_database() 