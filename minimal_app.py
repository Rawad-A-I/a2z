#!/usr/bin/env python3
"""
Minimal app for Railway - completely separate from Django project
"""
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class MinimalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy'}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/ready/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'ready'}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/live/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'alive'}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy', 'message': 'Minimal app running!'}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'error': 'Not found'}
            self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), MinimalHandler)
    print(f"Starting minimal app on port {port}")
    server.serve_forever()
