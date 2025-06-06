# D-Go Links

A simple URL shortener application built with Flask. Create short, memorable
links that redirect to longer URLs. 

A go-link is a short keyword that can be entered directly into your browser’s
address bar to quickly access internet resources. You can read more about
go-links [here](https://yiou.me/blog/posts/google-go-link).

There are lots of implementations of go-links around the internet, but
most of them seem to have a lot of extra cruft: They either use external cloud
services, or require Chrome extensions, or have extensive dependencies. I just
wanted a simple server I could host in a VM or Kubernetes for a relatively
small user base.

(It was also an excuse for me to try something more than toy
coding with Cursor. Vibe-coded in a couple of hours!)

And, it's called D-Go because I learned about go-links when I worked at Google,
where my login used to be dgo@.

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