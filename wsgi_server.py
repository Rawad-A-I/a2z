#!/usr/bin/env python3
"""
Railway-compatible WSGI server
Simple approach - let Railway handle port binding
"""
import os
import subprocess
import sys

def main():
    print("Starting Django eCommerce server...")
    
    # Use a simple approach - let Railway handle the port
    # Railway will automatically bind to the correct port
    cmd = [
        'gunicorn',
        'ecomm.wsgi:application',
        '--bind=0.0.0.0:8000',  # Use fixed port, Railway will map it
        '--workers=3'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
