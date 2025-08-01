from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime
from flask_caching import Cache

app = Flask(__name__)
CORS(app)

# Initialize cache with the app
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})  # Cache timeout 5 minutes

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '123456',  # Replace with your MySQL password
    'database': 'todo_app'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

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
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")
        
    except mysql.connector.Error as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    filter_type = request.args.get('filter', 'all')
    cache_key = f"tasks_{filter_type}"
    cached_tasks = cache.get(cache_key)
    if cached_tasks:
        print("Serving tasks from cache.")   # <-- THIS LINE
        return jsonify(cached_tasks)
    # Otherwise, fetch from db and cache
    print("Serving tasks from database and caching result.")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if filter_type == 'completed':
        cursor.execute("SELECT * FROM tasks WHERE completed = TRUE ORDER BY updated_at DESC")
    elif filter_type == 'pending':
        cursor.execute("SELECT * FROM tasks WHERE completed = FALSE ORDER BY updated_at DESC")
    else:
        cursor.execute("SELECT * FROM tasks ORDER BY updated_at DESC")

    tasks = cursor.fetchall()
    cursor.close()
    connection.close()

    cache.set(cache_key, tasks)

    return jsonify(tasks)

def clear_cache():
    """Clear all cache related to tasks"""
    cache.delete("tasks_all")
    cache.delete("tasks_completed")
    cache.delete("tasks_pending")

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)",
        (title, description)
    )
    connection.commit()
    
    task_id = cursor.lastrowid
    cursor.close()
    connection.close()
    clear_cache()  # Invalidate cache after data change
    
    return jsonify({'id': task_id, 'message': 'Task created successfully'}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
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
    
    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
    
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
def delete_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
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
