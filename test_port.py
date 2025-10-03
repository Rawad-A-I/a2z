#!/usr/bin/env python3
import os

# Test PORT environment variable handling
port = os.environ.get('PORT', '8000')
print(f"PORT environment variable: {port}")
print(f"PORT type: {type(port)}")

# Test if it's a valid port number
try:
    port_int = int(port)
    if 1 <= port_int <= 65535:
        print(f"✅ PORT {port_int} is valid")
    else:
        print(f"❌ PORT {port_int} is out of range")
except ValueError:
    print(f"❌ PORT '{port}' is not a valid number")
