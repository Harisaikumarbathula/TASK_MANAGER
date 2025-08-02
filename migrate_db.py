import mysql.connector
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'todo_app'
}

def migrate_database():
    """Migrate the database to include user authentication"""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS todo_app")
        cursor.execute("USE todo_app")
        
        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        users_table_exists = cursor.fetchone()
        
        if not users_table_exists:
            print("Creating users table...")
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Users table created successfully!")
        else:
            print("Users table already exists.")
        
        # Check if tasks table exists
        cursor.execute("SHOW TABLES LIKE 'tasks'")
        tasks_table_exists = cursor.fetchone()
        
        if tasks_table_exists:
            # Check if user_id column exists in tasks table
            cursor.execute("SHOW COLUMNS FROM tasks LIKE 'user_id'")
            user_id_exists = cursor.fetchone()
            
            if not user_id_exists:
                print("Adding user_id column to tasks table...")
                # Add user_id column
                cursor.execute("ALTER TABLE tasks ADD COLUMN user_id INT")
                print("user_id column added successfully!")
                
                # Create a default user for existing tasks
                print("Creating default user for existing tasks...")
                default_password = generate_password_hash("default123")
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    ("default_user", "default@example.com", default_password)
                )
                default_user_id = cursor.lastrowid
                
                # Update existing tasks to belong to the default user
                cursor.execute("UPDATE tasks SET user_id = %s WHERE user_id IS NULL", (default_user_id,))
                print(f"Updated {cursor.rowcount} existing tasks to belong to default user.")
                
                # Make user_id NOT NULL and add foreign key
                cursor.execute("ALTER TABLE tasks MODIFY COLUMN user_id INT NOT NULL")
                cursor.execute("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE")
                print("Foreign key constraint added successfully!")
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
        print("Database migration completed successfully!")
        
    except mysql.connector.Error as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_database() 