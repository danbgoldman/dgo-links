# Go Links

A simple URL shortener application built with Flask. Create short, memorable links that redirect to longer URLs.

## Features

- User authentication (login/register)
- Create, edit, and delete short links
- View your own links or all links
- Admin functionality:
  - Create and manage users
  - Promote/demote users to admin
  - Edit or delete any link
- First registered user automatically becomes an admin
- URL validation
- No-frills UI

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
# Development mode
python app.py

# Production mode
gunicorn app:app
```

The application will be available at `http://localhost:5000`

## Usage

1. Register a new account (first user becomes admin)
2. Create short links by visiting `/create` or by trying to access a non-existent short link
3. View and manage your links at `/links`
4. Admins can manage users at `/users`

## Development

- Built with Flask 3.0.2
- Uses SQLite for data storage
- Flask-Login for authentication
- Flask-SQLAlchemy for database management
- Gunicorn for production deployment

## Security

- Passwords are hashed using Werkzeug's security functions
- Admin-only routes are protected
- Users can only edit/delete their own links
- URL validation to prevent invalid redirects 