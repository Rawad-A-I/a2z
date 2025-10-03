#!/usr/bin/env python3
"""
Railway-compatible WSGI server
Handles PORT variable expansion properly
"""
import os
import subprocess
import sys

def main():
    # Get PORT from environment variable
    port = os.environ.get('PORT', '8000')
    
    # Convert to integer to validate
    try:
        port_int = int(port)
        print(f"Starting server on port {port_int}")
    except ValueError:
        print(f"Invalid PORT value: {port}, using default 8000")
        port_int = 8000
    
    # Start Gunicorn with the port
    cmd = [
        'gunicorn',
        'ecomm.wsgi:application',
        f'--bind=0.0.0.0:{port_int}',
        '--workers=3'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
