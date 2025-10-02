#!/usr/bin/env python
"""
Enhanced Features Setup Script for Django eCommerce Website

This script sets up the new enhanced features:
- API Documentation with Django REST Framework
- Redis Caching for performance
- Elasticsearch for advanced search
"""

import os
import sys
import subprocess
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_service(service_name, port):
    """Check if a service is running"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def setup_enhanced_features():
    """Setup enhanced features"""
    print("🚀 Setting up Enhanced Features for Django eCommerce Website")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Install new dependencies
    print("\n📦 Installing new dependencies...")
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Check Redis
    print("\n🔍 Checking Redis...")
    if not check_service('Redis', 6379):
        print("⚠️  Redis is not running on port 6379.")
        print("   Please install and start Redis:")
        print("   - Windows: Download from https://redis.io/download")
        print("   - macOS: brew install redis && brew services start redis")
        print("   - Linux: sudo apt-get install redis-server && sudo systemctl start redis")
        print("   - Docker: docker run -d -p 6379:6379 redis:alpine")
    else:
        print("✅ Redis is running")
    
    # Check Elasticsearch
    print("\n🔍 Checking Elasticsearch...")
    if not check_service('Elasticsearch', 9200):
        print("⚠️  Elasticsearch is not running on port 9200.")
        print("   Please install and start Elasticsearch:")
        print("   - Download from https://www.elastic.co/downloads/elasticsearch")
        print("   - Or use Docker: docker run -d -p 9200:9200 -p 9300:9300 elasticsearch:7.17.0")
        print("   - Or use Elastic Cloud for easier setup")
    else:
        print("✅ Elasticsearch is running")
    
    # Run Django migrations
    print("\n🗄️  Running Django migrations...")
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        print("❌ Failed to create migrations")
        sys.exit(1)
    
    if not run_command("python manage.py migrate", "Applying migrations"):
        print("❌ Failed to apply migrations")
        sys.exit(1)
    
    # Create search indices
    print("\n🔍 Setting up Elasticsearch indices...")
    if check_service('Elasticsearch', 9200):
        if not run_command("python manage.py rebuild_search_index", "Creating search indices"):
            print("⚠️  Failed to create search indices. You can run this manually later.")
    else:
        print("⚠️  Skipping search index creation (Elasticsearch not available)")
    
    # Collect static files
    print("\n📁 Collecting static files...")
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # Create superuser if needed
    print("\n👤 Checking for superuser...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("🔑 No superuser found. Please create one:")
            print("   python manage.py createsuperuser")
        else:
            print("✅ Superuser exists")
    except Exception as e:
        print(f"⚠️  Could not check superuser: {e}")
    
    # Final instructions
    print("\n" + "=" * 60)
    print("🎉 Enhanced Features Setup Complete!")
    print("\n📋 What's New:")
    print("   ✅ REST API with comprehensive endpoints")
    print("   ✅ Redis caching for better performance")
    print("   ✅ Elasticsearch for advanced search")
    print("   ✅ Interactive API documentation")
    print("\n🚀 Next Steps:")
    print("   1. Start your Django server: python manage.py runserver")
    print("   2. Visit the API documentation: http://localhost:8000/api/schema/swagger-ui/")
    print("   3. Test the search functionality: http://localhost:8000/search/products/?q=your-search")
    print("   4. Explore the API endpoints: http://localhost:8000/api/")
    print("\n📚 Documentation:")
    print("   - API Docs: http://localhost:8000/api/schema/swagger-ui/")
    print("   - ReDoc: http://localhost:8000/api/schema/redoc/")
    print("   - Search API: http://localhost:8000/search/")
    print("\n🔧 Management Commands:")
    print("   - Rebuild search index: python manage.py rebuild_search_index")
    print("   - Clear cache: python manage.py clear_cache")
    print("   - Run tests: python tests/run_all_tests.py")

if __name__ == "__main__":
    setup_enhanced_features()
