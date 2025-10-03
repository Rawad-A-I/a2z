# Create Brand New Django Railway Project From Scratch
## Complete Step-by-Step Guide

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Setup](#local-setup)
3. [Railway Deployment](#railway-deployment)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools:
- ✅ Python 3.10 or 3.11 installed
- ✅ Git installed
- ✅ GitHub account
- ✅ Railway account (https://railway.app)
- ✅ Text editor (VS Code recommended)

### Install Railway CLI:
```bash
npm install -g @railway/cli
```

Or download from: https://docs.railway.app/develop/cli

---

## Local Setup

### Step 1: Create New Django Project

```bash
# Create project directory
mkdir my-django-railway-app
cd my-django-railway-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Django and dependencies
pip install django gunicorn whitenoise dj-database-url psycopg2-binary python-decouple
```

### Step 2: Create Django Project

```bash
# Create project
django-admin startproject myproject .

# Create an app (optional)
python manage.py startapp myapp
```

### Step 3: Configure Settings

Edit `myproject/settings.py`:

```python
import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,127.0.0.1,*.railway.app',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your apps here
    # 'myapp',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# DATABASE
if config('DATABASE_URL', default=None):
    # Use PostgreSQL on Railway
    DATABASES = {
        'default': dj_database_url.parse(config('DATABASE_URL'))
    }
else:
    # Use SQLite locally
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []  # Add your static directories here

# WhiteNoise configuration
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# SECURITY SETTINGS (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# CSRF
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.railway.app',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
```

### Step 4: Create Health Check

Create `myapp/health.py`:

```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Health check endpoint for Railway"""
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        return JsonResponse({'status': 'healthy'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)

def readiness_check(request):
    """Readiness check"""
    return JsonResponse({'status': 'ready'}, status=200)
```

Create `myapp/urls.py`:

```python
from django.urls import path
from .health import health_check, readiness_check

urlpatterns = [
    path('health/', health_check, name='health'),
    path('ready/', readiness_check, name='ready'),
]
```

Update `myproject/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  # Add this
]
```

### Step 5: Create Deployment Files

**Create `Procfile`:**
```
web: gunicorn myproject.wsgi --log-file -
```

**Create `runtime.txt`:**
```
python-3.11.6
```

**Create `railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "healthcheckPath": "/health/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Create `.gitignore`:**
```
*.pyc
__pycache__/
db.sqlite3
/venv
/env
.env
*.log
staticfiles/
mediafiles/
.DS_Store
```

**Create `requirements.txt`:**
```bash
pip freeze > requirements.txt
```

### Step 6: Test Locally

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run server
python manage.py runserver

# Test health check
# Visit: http://localhost:8000/health/
```

---

## Railway Deployment

### Step 1: Initialize Git and Push to GitHub

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit - Django Railway app"

# Create GitHub repo and push
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Login to Railway

```bash
railway login
```

This opens a browser for authentication.

### Step 3: Create Railway Project

```bash
# Create new project
railway init

# Or link existing project
railway link
```

### Step 4: Add PostgreSQL Database

**Option A: Via CLI**
```bash
railway add --database postgresql
```

**Option B: Via Dashboard**
1. Go to https://railway.app/dashboard
2. Click your project
3. Click "New" → "Database" → "PostgreSQL"

### Step 5: Deploy from GitHub

**Via Dashboard (Recommended):**
1. Go to Railway Dashboard
2. Click "New" → "GitHub Repo"
3. Select your repository
4. Railway auto-detects Django and starts building

**Via CLI:**
```bash
railway up
```

### Step 6: Link Database to Web Service

**CRITICAL STEP:**

1. In Railway Dashboard → Your Project
2. Click on your web service
3. Go to "Variables" tab
4. Click "New Variable"
5. Select "Add a Service Variable"
6. Service: `Postgres`
7. Variable: `DATABASE_URL`
8. Click "Add"

Railway creates: `DATABASE_URL = ${{Postgres.DATABASE_URL}}`

### Step 7: Set Environment Variables

In Railway web service → Variables, add:

```bash
SECRET_KEY=<generate-with-python-secrets>
DEBUG=False
ALLOWED_HOSTS=*.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Step 8: Deploy and Migrate

```bash
# Link to your Railway project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files (if not done in build)
railway run python manage.py collectstatic --noinput
```

### Step 9: Get Your URL

```bash
railway domain
```

Or check Railway Dashboard → Your Service → Settings → Domains

---

## Verification

### Check Deployment Status

```bash
railway status
```

### View Logs

```bash
railway logs
```

### Test Health Check

```bash
curl https://your-app.railway.app/health/
```

Expected response:
```json
{"status":"healthy"}
```

### Test Admin Panel

Visit: `https://your-app.railway.app/admin/`

Login with your superuser credentials.

---

## Troubleshooting

### Build Fails

**Check:**
- `requirements.txt` has all dependencies
- `runtime.txt` has supported Python version
- Check Railway logs for errors

**Common Fix:**
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### App Crashes

**Most Common: Missing DATABASE_URL**

Verify:
```bash
railway variables
```

DATABASE_URL should be present. If not, add it (see Step 6).

### Health Check Fails

**Check:**
1. Health endpoint returns 200 status
2. Database is connected
3. Migrations completed

**Test:**
```bash
railway run python manage.py check --database default
```

### Static Files Not Loading

**Verify WhiteNoise:**
```python
# In settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be here
    # ... rest
]
```

**Collect static:**
```bash
railway run python manage.py collectstatic --noinput
```

### Database Connection Errors

**Check:**
1. PostgreSQL service is running
2. DATABASE_URL is set correctly
3. psycopg2-binary is in requirements.txt

**Test connection:**
```bash
railway run python manage.py dbshell
```

---

## 🎯 Success Checklist

Before deploying:
- [ ] `requirements.txt` created and up-to-date
- [ ] `Procfile` with gunicorn command
- [ ] `runtime.txt` with Python version
- [ ] `railway.json` with health check config
- [ ] WhiteNoise installed and configured
- [ ] Settings use environment variables
- [ ] Health check endpoint created
- [ ] `.gitignore` excludes sensitive files
- [ ] Code pushed to GitHub

On Railway:
- [ ] PostgreSQL database added
- [ ] DATABASE_URL linked to web service ✅ **CRITICAL**
- [ ] SECRET_KEY set
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS includes *.railway.app
- [ ] Migrations run successfully
- [ ] Superuser created
- [ ] Health check passing

Verification:
- [ ] App accessible at Railway URL
- [ ] Admin panel works
- [ ] Health endpoint returns 200 OK
- [ ] Database queries work
- [ ] Static files load

---

## 📊 Minimal Working Example

Here's the absolute minimum files needed:

```
my-django-app/
├── myproject/
│   ├── __init__.py
│   ├── settings.py      # Configured as shown above
│   ├── urls.py
│   └── wsgi.py
├── Procfile             # web: gunicorn myproject.wsgi
├── runtime.txt          # python-3.11.6
├── railway.json         # Health check config
├── requirements.txt     # All dependencies
└── .gitignore
```

---

## 🚀 Quick Start Command Reference

```bash
# Local setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install django gunicorn whitenoise dj-database-url psycopg2-binary python-decouple
django-admin startproject myproject .
pip freeze > requirements.txt

# Git setup
git init
git add .
git commit -m "Initial commit"
git push -u origin main

# Railway setup
railway login
railway init
railway add --database postgresql

# Deploy and configure
railway up
railway run python manage.py migrate
railway run python manage.py createsuperuser

# Verify
railway logs
railway domain
curl https://your-app.railway.app/health/
```

---

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Railway CLI: https://docs.railway.app/develop/cli
- WhiteNoise: http://whitenoise.evans.io/

---

*Last Updated: October 3, 2025*
*Tested with: Django 5.1, Python 3.11, Railway v4*

