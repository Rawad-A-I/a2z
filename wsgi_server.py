#!/usr/bin/env python3
"""
Railway-compatible WSGI server
Handles Railway's dynamic PORT properly
Successfully deployed with PostgreSQL database integration
"""
import os
import subprocess
import sys

def main():
    print("Starting Django eCommerce server...")
    
    # Run database migrations first
    print("Running database migrations...")
    try:
        subprocess.run(['python', 'manage.py', 'migrate'], check=True)
        print("Database migrations completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Migration failed: {e}")
        print("Continuing anyway...")
    
    # Collect static files
    print("Collecting static files...")
    try:
        subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=True)
        print("Static files collected successfully")
    except subprocess.CalledProcessError as e:
        print(f"Static files collection failed: {e}")
        print("Continuing anyway...")
    
    # Get PORT from Railway environment
    port = os.environ.get('PORT', '8000')
    
    # Debug: Print what we got
    print(f"PORT environment variable: {port}")
    print(f"PORT type: {type(port)}")
    
    # Handle the case where Railway might pass the literal string '$PORT'
    if port == '$PORT' or not port:
        print("Railway didn't provide a valid PORT, using 8000")
        port = '8000'
    
    # Ensure port is a valid integer
    try:
        port_int = int(port)
        print(f"Using port: {port_int}")
    except (ValueError, TypeError):
        print("Invalid port, using default 8000")
        port_int = 8000
    
    # Start Gunicorn with better connection handling
    cmd = [
        'gunicorn',
        'ecomm.wsgi:application',
        f'--bind=0.0.0.0:{port_int}',
        '--workers=3',
        '--timeout=120',
        '--keep-alive=2',
        '--max-requests=1000',
        '--max-requests-jitter=100',
        '--preload',
        '--worker-class=sync',
        '--worker-connections=1000'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
