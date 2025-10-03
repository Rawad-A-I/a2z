#!/usr/bin/env python3
"""
Railway-compatible WSGI server
Handles PORT variable expansion properly
"""
import os
import subprocess
import sys

def main():
    # Debug: Print all environment variables
    print("Environment variables:")
    for key, value in os.environ.items():
        if 'PORT' in key:
            print(f"  {key} = {value}")
    
    # Get PORT from environment variable with better handling
    port = os.environ.get('PORT')
    
    if not port or port == '$PORT':
        print("No valid PORT found, using default 8000")
        port_int = 8000
    else:
        try:
            port_int = int(port)
            print(f"Using Railway PORT: {port_int}")
        except ValueError:
            print(f"Invalid PORT value: {port}, using default 8000")
            port_int = 8000
    
    print(f"Starting server on port {port_int}")
    
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
