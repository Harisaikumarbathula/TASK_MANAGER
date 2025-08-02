from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
import mysql.connector
from datetime import datetime
from flask_caching import Cache
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize cache with the app
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})  # Cache timeout 5 minutes

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',  # Replace with your MySQL username
    'password': '123456',  # Replace with your MySQL password
    'database': 'todo_app'
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def check_and_fix_database():
    """Check if database structure is correct and fix if needed"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if user_id column exists in tasks table
        cursor.execute("SHOW COLUMNS FROM tasks LIKE 'user_id'")
        user_id_exists = cursor.fetchone()
        
        if not user_id_exists:
            print("Fixing database structure...")
            # Add user_id column
            cursor.execute("ALTER TABLE tasks ADD COLUMN user_id INT")
            
            # Create a default user for existing tasks
            default_password = generate_password_hash("default123")
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                ("default_user", "default@example.com", default_password)
            )
            default_user_id = cursor.lastrowid
            
            # Update existing tasks to belong to the default user
            cursor.execute("UPDATE tasks SET user_id = %s WHERE user_id IS NULL", (default_user_id,))
            
            # Make user_id NOT NULL and add foreign key
            cursor.execute("ALTER TABLE tasks MODIFY COLUMN user_id INT NOT NULL")
            cursor.execute("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE")
            
            connection.commit()
            print("Database structure fixed successfully!")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f"Error checking database structure: {e}")

def init_db():
    """Initialize the database and create tables"""
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
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create tasks table with user_id foreign key
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
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
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")
        
        # Check and fix database structure if needed
        check_and_fix_database()
        
    except mysql.connector.Error as e:
        print(f"Error initializing database: {e}")

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['email'])
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('signup.html')
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if username or email already exists
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Username or email already exists', 'error')
            cursor.close()
            connection.close()
            return render_template('signup.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        connection.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    filter_type = request.args.get('filter', 'all')
    cache_key = f"tasks_{current_user.id}_{filter_type}"
    cached_tasks = cache.get(cache_key)
    if cached_tasks:
        print("Serving tasks from cache.")   # <-- THIS LINE
        return jsonify(cached_tasks)
    # Otherwise, fetch from db and cache
    print("Serving tasks from database and caching result.")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if filter_type == 'completed':
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s AND completed = TRUE ORDER BY updated_at DESC", (current_user.id,))
    elif filter_type == 'pending':
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s AND completed = FALSE ORDER BY updated_at DESC", (current_user.id,))
    else:
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY updated_at DESC", (current_user.id,))

    tasks = cursor.fetchall()
    cursor.close()
    connection.close()

    cache.set(cache_key, tasks)

    return jsonify(tasks)

def clear_cache():
    """Clear all cache related to tasks for current user"""
    cache.delete(f"tasks_{current_user.id}_all")
    cache.delete(f"tasks_{current_user.id}_completed")
    cache.delete(f"tasks_{current_user.id}_pending")

@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "INSERT INTO tasks (user_id, title, description) VALUES (%s, %s, %s)",
        (current_user.id, title, description)
    )
    connection.commit()
    
    task_id = cursor.lastrowid
    cursor.close()
    connection.close()
    clear_cache()  # Invalidate cache after data change
    
    return jsonify({'id': task_id, 'message': 'Task created successfully'}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    data = request.get_json()
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Build dynamic update query
    update_fields = []
    values = []
    
    if 'title' in data:
        update_fields.append("title = %s")
        values.append(data['title'])
    
    if 'description' in data:
        update_fields.append("description = %s")
        values.append(data['description'])
    
    if 'completed' in data:
        update_fields.append("completed = %s")
        values.append(data['completed'])
    
    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400
    
    values.extend([current_user.id, task_id])
    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE user_id = %s AND id = %s"
    
    cursor.execute(query, values)
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({'error': 'Task not found'}), 404
    
    cursor.close()
    connection.close()
    clear_cache()  # Invalidate cache after data change    
    return jsonify({'message': 'Task updated successfully'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE user_id = %s AND id = %s", (current_user.id, task_id))
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({'error': 'Task not found'}), 404
    
    cursor.close()
    connection.close()
    clear_cache()  # Invalidate cache after data change
    return jsonify({'message': 'Task deleted successfully'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
