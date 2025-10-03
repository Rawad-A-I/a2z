#!/usr/bin/env python3
"""
Railway-compatible WSGI server
Handles Railway's dynamic PORT properly
"""
import os
import subprocess
import sys

def main():
    print("Starting Django eCommerce server...")
    
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
    
    # Start Gunicorn
    cmd = [
        'gunicorn',
        'ecomm.wsgi:application',
        f'--bind=0.0.0.0:{port_int}',
        '--workers=3',
        '--timeout=120',
        '--keep-alive=2'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
