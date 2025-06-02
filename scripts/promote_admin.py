#!/usr/bin/env python3
import sys
from app import app, db, User

def promote_to_admin(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found")
            sys.exit(1)
        
        if user.is_admin:
            print(f"User '{username}' is already an admin")
            sys.exit(0)
        
        user.is_admin = True
        db.session.commit()
        print(f"Successfully promoted '{username}' to admin")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python promote_admin.py <username>")
        sys.exit(1)
    
    promote_to_admin(sys.argv[1]) 