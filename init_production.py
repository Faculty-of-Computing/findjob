#!/usr/bin/env python3
"""
Production deployment script for FindJob
This script handles database initialization and setup for production deployment
"""

import os
import sys
from app import create_app, db

def init_production():
    """Initialize the application for production"""
    try:
        app = create_app()

        with app.app_context():
            # Create all database tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")

            # Create admin user if it doesn't exist
            from app.models import User
            admin = User.query.filter_by(email='admin@findjob.com').first()
            if not admin:
                print("Creating default admin user...")
                from werkzeug.security import generate_password_hash
                admin = User(
                    username='admin',
                    email='admin@findjob.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    is_active=True
                )
                db.session.add(admin)
                db.session.commit()
                print("Admin user created: admin@findjob.com / admin123")
            else:
                print("Admin user already exists")

        print("Production initialization completed successfully!")
        return True

    except Exception as e:
        print(f"Error during production initialization: {e}")
        return False

if __name__ == '__main__':
    success = init_production()
    sys.exit(0 if success else 1)
