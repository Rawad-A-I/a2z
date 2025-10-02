#!/usr/bin/env python3
"""
PostgreSQL Setup Script for Django eCommerce Website

This script helps set up PostgreSQL for the Django eCommerce project.
It creates a database and user for local development.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_postgresql_installed():
    """Check if PostgreSQL is installed."""
    try:
        subprocess.run(['psql', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_database():
    """Set up PostgreSQL database and user."""
    print("🚀 Setting up PostgreSQL for Django eCommerce Website")
    print("=" * 50)
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installed():
        print("❌ PostgreSQL is not installed or not in PATH")
        print("Please install PostgreSQL first:")
        print("- Windows: Download from https://www.postgresql.org/download/windows/")
        print("- macOS: brew install postgresql")
        print("- Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return False
    
    # Database configuration
    db_name = "ecommerce_db"
    db_user = "ecommerce_user"
    db_password = "ecommerce_password"
    
    print(f"📊 Creating database: {db_name}")
    print(f"👤 Creating user: {db_user}")
    
    # Create user
    create_user_cmd = f"psql -U postgres -c \"CREATE USER {db_user} WITH PASSWORD '{db_password}';\""
    if not run_command(create_user_cmd, "Creating database user"):
        print("⚠️  User might already exist, continuing...")
    
    # Create database
    create_db_cmd = f"psql -U postgres -c \"CREATE DATABASE {db_name} OWNER {db_user};\""
    if not run_command(create_db_cmd, "Creating database"):
        print("⚠️  Database might already exist, continuing...")
    
    # Grant privileges
    grant_cmd = f"psql -U postgres -c \"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};\""
    run_command(grant_cmd, "Granting privileges")
    
    # Create .env file
    env_content = f"""# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (PostgreSQL)
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/0

# Domain
DOMAIN=localhost:8000
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file with PostgreSQL configuration")
    else:
        print("⚠️  .env file already exists, please update it manually")
    
    print("\n🎉 PostgreSQL setup completed!")
    print("\nNext steps:")
    print("1. Install Python dependencies: pip install -r requirements.txt")
    print("2. Run migrations: python manage.py migrate")
    print("3. Create superuser: python manage.py createsuperuser")
    print("4. Start server: python manage.py runserver")
    
    return True

if __name__ == "__main__":
    setup_database()

