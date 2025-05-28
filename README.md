# Go Links Server

A simple URL shortener service that allows users to create and manage short links.

## Features

- Create short links that redirect to full URLs
- User authentication and authorization
- Automatic creation page for unused short links
- SQLite database for data storage

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The server will start at http://localhost:5000

## Usage

1. Register a new account
2. Login to your account
3. Access any short path (e.g., http://localhost:5000/mylink)
   - If the link exists, you'll be redirected to the target URL
   - If the link doesn't exist, you'll be taken to a creation page
4. Create new links by accessing unused short paths 