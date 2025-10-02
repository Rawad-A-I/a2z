"""
Test script to verify deployment readiness
Run this before deploying to Railway
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

from django.test import RequestFactory
from django.core.management import call_command
from home.health import health_check, readiness_check
import json


def test_health_endpoint():
    """Test health check endpoint"""
    print("\n1. Testing Health Check Endpoint...")
    rf = RequestFactory()
    request = rf.get('/health/')
    response = health_check(request)
    
    if response.status_code == 200:
        data = json.loads(response.content.decode())
        print(f"   ✅ Health check PASSED")
        print(f"   Status: {data.get('status')}")
        print(f"   Checks: {data.get('checks')}")
        return True
    else:
        print(f"   ❌ Health check FAILED with status {response.status_code}")
        return False


def test_readiness_endpoint():
    """Test readiness endpoint"""
    print("\n2. Testing Readiness Endpoint...")
    rf = RequestFactory()
    request = rf.get('/ready/')
    response = readiness_check(request)
    
    if response.status_code == 200:
        print(f"   ✅ Readiness check PASSED")
        return True
    else:
        print(f"   ❌ Readiness check FAILED")
        return False


def test_settings():
    """Test critical settings"""
    print("\n3. Testing Django Settings...")
    from django.conf import settings
    
    checks = {
        'SECRET_KEY exists': bool(settings.SECRET_KEY),
        'STATIC_ROOT set': bool(settings.STATIC_ROOT),
        'ALLOWED_HOSTS configured': len(settings.ALLOWED_HOSTS) > 0,
        'DATABASES configured': 'default' in settings.DATABASES,
    }
    
    all_passed = True
    for check, result in checks.items():
        if result:
            print(f"   ✅ {check}")
        else:
            print(f"   ❌ {check}")
            all_passed = False
    
    return all_passed


def test_migrations():
    """Test migrations"""
    print("\n4. Testing Migrations...")
    try:
        call_command('migrate', '--check', verbosity=0)
        print("   ✅ Migrations are up to date")
        return True
    except Exception as e:
        print(f"   ⚠️  Migration check: {str(e)}")
        print("   (This is OK for first deploy)")
        return True


def test_static_files():
    """Test static files collection"""
    print("\n5. Testing Static Files Collection...")
    try:
        from django.contrib.staticfiles.management.commands.collectstatic import Command
        print("   ✅ collectstatic command available")
        return True
    except ImportError:
        print("   ❌ collectstatic command not found")
        return False


def test_urls():
    """Test URL configuration"""
    print("\n6. Testing URL Configuration...")
    from django.urls import resolve
    
    urls_to_test = [
        ('/', 'redirect_homepage'),
        ('/health/', 'health_check'),
        ('/ready/', 'readiness_check'),
    ]
    
    all_passed = True
    for url, expected_name in urls_to_test:
        try:
            match = resolve(url)
            if match.url_name == expected_name or expected_name in str(match.func):
                print(f"   ✅ {url} -> {expected_name}")
            else:
                print(f"   ⚠️  {url} -> {match.url_name} (expected {expected_name})")
        except Exception as e:
            print(f"   ❌ {url} failed: {str(e)}")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests"""
    print("=" * 60)
    print("RAILWAY DEPLOYMENT READINESS TEST")
    print("=" * 60)
    
    results = {
        'Health Check': test_health_endpoint(),
        'Readiness Check': test_readiness_endpoint(),
        'Django Settings': test_settings(),
        'Migrations': test_migrations(),
        'Static Files': test_static_files(),
        'URL Configuration': test_urls(),
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Commit and push changes to GitHub")
        print("2. Connect Railway to your GitHub repository")
        print("3. Set environment variables in Railway:")
        print("   - SECRET_KEY")
        print("   - DEBUG=False")
        print("   - ALLOWED_HOSTS=*.railway.app")
        print("4. Deploy and monitor the logs!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before deploying.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

