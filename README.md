# Task Manager App with Authentication

A beautiful and modern task management application built with Flask, featuring user authentication and a glass-morphism design.

## Features

### Authentication
- **User Registration**: Create new accounts with username, email, and password
- **User Login**: Secure login with password hashing
- **Session Management**: Persistent user sessions with Flask-Login
- **Logout**: Secure logout functionality

### Task Management
- **Create Tasks**: Add new tasks with title and description
- **Edit Tasks**: Modify existing tasks
- **Delete Tasks**: Remove tasks from your list
- **Mark Complete**: Toggle task completion status
- **Filter Tasks**: View all, completed, or pending tasks
- **Real-time Updates**: Instant UI updates without page refresh

### Design
- **Glass Morphism**: Modern glass effect design
- **Responsive**: Works on desktop and mobile devices
- **Beautiful UI**: Gradient buttons and smooth animations
- **User-friendly**: Intuitive interface with clear navigation

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TASK_MANAGER
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database**
   - Update the `DB_CONFIG` in `app.py` with your MySQL credentials
   - Ensure MySQL server is running

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - You'll be redirected to the login page
   - Create a new account or log in with existing credentials

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp

### Tasks Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `title`: Task title
- `description`: Task description
- `completed`: Task completion status
- `created_at`: Task creation timestamp
- `updated_at`: Last update timestamp

## Security Features

- **Password Hashing**: Passwords are hashed using Werkzeug's security functions
- **Session Management**: Secure session handling with Flask-Login
- **User Isolation**: Each user can only access their own tasks
- **Input Validation**: Form validation and sanitization
- **SQL Injection Protection**: Parameterized queries

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Login form submission
- `GET /signup` - Registration page
- `POST /signup` - Registration form submission
- `GET /logout` - Logout user

### Tasks (Protected Routes)
- `GET /` - Main dashboard (requires login)
- `GET /api/tasks` - Get user's tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

## Usage

1. **First Time Users**
   - Visit the application
   - Click "Create Account" on the login page
   - Fill in your details and create an account
   - Log in with your credentials

2. **Returning Users**
   - Visit the application
   - Enter your username and password
   - Access your personalized task dashboard

3. **Managing Tasks**
   - Add new tasks using the form at the top
   - Filter tasks using the buttons (All, Completed, Pending)
   - Edit tasks by clicking the edit button
   - Mark tasks as complete using the checkbox
   - Delete tasks using the delete button

4. **Logging Out**
   - Click the "Logout" button in the top-right corner
   - You'll be redirected to the login page

## Technologies Used

- **Backend**: Flask, Flask-Login, Flask-Caching, Flask-CORS
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Icons**: Font Awesome
- **Security**: Werkzeug (password hashing)

## Customization

### Styling
- Modify `static/css/style.css` to change the appearance
- Update color variables in the `:root` selector
- Adjust glass effect properties as needed

### Database
- Update `DB_CONFIG` in `app.py` for your database settings
- Modify table schemas in the `init_db()` function

### Features
- Add new routes in `app.py`
- Create new templates in the `templates/` directory
- Add JavaScript functionality in `static/js/script.js`

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify MySQL server is running
   - Check database credentials in `app.py`
   - Ensure the database exists

2. **Import Errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Authentication Issues**
   - Clear browser cookies and cache
   - Restart the Flask application
   - Check if the database tables were created properly

## License

This project is open source and available under the MIT License. 