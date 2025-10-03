# Complete Railway Django Deployment Guide
## Based on Official Railway Documentation & Best Practices 2024-2025

---

## 📚 Research Summary

### What Railway Needs for Django Apps:

1. **Build System**: Railway auto-detects Django and uses Nixpacks (or Dockerfile)
2. **Web Server**: Gunicorn (not Django's development server)
3. **Static Files**: WhiteNoise (Railway doesn't serve Django static files)
4. **Database**: PostgreSQL service with DATABASE_URL environment variable
5. **Configuration Files**:
   - `requirements.txt` - Python dependencies
   - `Procfile` - How to start the app
   - `runtime.txt` - Python version (optional)
   - `railway.json` or `railway.toml` - Railway config (optional)

---

## ✅ Current App Issues & Fixes

### Issue 1: Database Not Connected ❌
**Problem**: `brave-rebirth` service missing `DATABASE_URL`

**Solution**: 
1. Go to Railway Dashboard → Project `a2z`
2. Click on `brave-rebirth` service
3. Click "Variables" tab
4. Click "New Variable" or "Add Reference"
5. Add: `DATABASE_URL` → Reference from `Postgres` service
6. Service will auto-redeploy

### Issue 2: Health Check Configuration ✅ (Already Fixed)
**Status**: Your health check endpoints are working:
- `/health/` - Returns 200 OK when DB is connected
- `/ready/` - Always returns 200 OK
- `/live/` - Liveness probe

**Current Config** (`railway.json`):
```json
{
  "healthcheckPath": "/health/",
  "healthcheckTimeout": 300
}
```
✅ This is correct!

### Issue 3: Procfile Check
**What Railway Expects**:
```
web: gunicorn ecomm.wsgi --log-file -
```

Let me check your current Procfile...

---

## 🚀 Step-by-Step: Create New Railway Project From Scratch

### Phase 1: Prepare Your Django App Locally

#### 1. Install Required Packages
```bash
pip install gunicorn whitenoise dj-database-url psycopg2-binary python-decouple
```

#### 2. Update `settings.py`
```python
import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='your-dev-secret-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*.railway.app', 
                        cast=lambda v: [s.strip() for s in v.split(',')])

# Database - Railway provides DATABASE_URL
if config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.parse(config('DATABASE_URL'))
    }
else:
    # Fallback to SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files with WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'public/media'] if (BASE_DIR / 'public/media').exists() else []

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this right after SecurityMiddleware
    # ... rest of your middleware
]

# WhiteNoise configuration
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
```

#### 3. Create/Update `Procfile`
```
web: gunicorn ecomm.wsgi --log-file - --workers 3
```

#### 4. Create/Update `runtime.txt`
```
python-3.11.6
```

#### 5. Update `requirements.txt`
```bash
pip freeze > requirements.txt
```

Ensure these are in your requirements.txt:
```
Django>=5.0
gunicorn>=21.0
whitenoise>=6.6
dj-database-url>=2.0
psycopg2-binary>=2.9
python-decouple>=3.8
```

#### 6. Create `.gitignore`
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
```

### Phase 2: Deploy to Railway

#### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Railway deployment"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

#### Step 2: Create Railway Project
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Django and start building

#### Step 3: Add PostgreSQL Database
1. In Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. PostgreSQL service will be created

#### Step 4: Connect Database to Web Service
**CRITICAL STEP** (This is what's missing in your current setup!)

1. Click on your web service (brave-rebirth)
2. Go to "Variables" tab
3. Click "New Variable"
4. Select "Add Reference Variable"
5. Choose: `Postgres` service → `DATABASE_URL`
6. Click "Add Variable"

Railway will automatically create:
```
DATABASE_URL = ${{Postgres.DATABASE_URL}}
```

#### Step 5: Set Other Environment Variables
Add these in your web service Variables:

```
SECRET_KEY = <generate-with-python-secrets>
DEBUG = False
ALLOWED_HOSTS = *.railway.app
CSRF_TRUSTED_ORIGINS = https://*.railway.app
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

#### Step 6: Deploy and Migrate
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files (if not done in build)
railway run python manage.py collectstatic --noinput
```

#### Step 7: Verify Deployment
1. Check Railway logs for any errors
2. Visit your Railway URL: `https://your-app.railway.app`
3. Test health check: `https://your-app.railway.app/health/`

---

## 🔧 Troubleshooting Railway Deployments

### Build Fails
- Check `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt` is supported
- Check Railway logs for specific error

### App Crashes After Deploy
- **Most Common**: Missing `DATABASE_URL`
  - Solution: Link PostgreSQL service to web service
- Check environment variables are set
- Check `Procfile` syntax is correct
- Review Railway logs

### Static Files Not Loading
- Ensure WhiteNoise is installed
- Verify STATIC_ROOT is set correctly
- Run `collectstatic` after deployment
- Check STATICFILES_STORAGE setting

### Database Connection Errors
- Verify DATABASE_URL is set as reference variable
- Check PostgreSQL service is running
- Ensure psycopg2-binary is in requirements.txt
- Check database migrations ran successfully

### Health Check Fails
- Ensure endpoint returns 200 status code
- Check DATABASE_URL is accessible
- Verify migrations completed
- Check healthcheckTimeout is sufficient (300 seconds recommended)

---

## 📋 Deployment Checklist

### Before Deployment:
- [ ] `requirements.txt` updated with all dependencies
- [ ] `Procfile` created with correct gunicorn command
- [ ] `runtime.txt` specifies Python version
- [ ] WhiteNoise installed and configured
- [ ] `settings.py` uses environment variables
- [ ] Database configuration uses DATABASE_URL
- [ ] `.gitignore` excludes sensitive files
- [ ] Code pushed to GitHub

### On Railway:
- [ ] Web service created from GitHub repo
- [ ] PostgreSQL database service added
- [ ] DATABASE_URL linked to web service (**CRITICAL**)
- [ ] SECRET_KEY environment variable set
- [ ] DEBUG set to False
- [ ] ALLOWED_HOSTS includes *.railway.app
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Superuser created

### Verification:
- [ ] App loads at Railway URL
- [ ] Admin panel accessible
- [ ] Database queries work
- [ ] Static files load correctly
- [ ] Health check returns 200 OK

---

## 🎯 Your Current App - Quick Fix Steps

### Immediate Actions to Fix brave-rebirth:

1. **Connect Database** (TOP PRIORITY):
   ```
   Railway Dashboard → brave-rebirth → Variables → New Variable
   → Add Reference → Postgres.DATABASE_URL
   ```

2. **Verify Procfile**:
   ```
   web: gunicorn ecomm.wsgi --log-file -
   ```

3. **Add Missing Variables**:
   ```
   CSRF_TRUSTED_ORIGINS = https://*.railway.app
   ```

4. **Trigger Redeploy**:
   - Railway will auto-redeploy when you add DATABASE_URL
   - Or click "Redeploy" in Railway dashboard

5. **Run Migrations**:
   ```bash
   railway link  # Select brave-rebirth
   railway run python manage.py migrate
   ```

6. **Test Health Check**:
   ```bash
   curl https://your-railway-url/health/
   # Should return: {"status":"healthy","checks":{"database":"ok"}}
   ```

---

## 📊 Why Your Current Setup Isn't Working

### Problem Analysis:
```
brave-rebirth service variables:
✅ ALLOWED_HOSTS
✅ DEBUG  
✅ SECRET_KEY
❌ DATABASE_URL ← MISSING!
```

**Root Cause**: The database variable was never linked to brave-rebirth.

**Why This Matters**: 
- Django can't connect to PostgreSQL without DATABASE_URL
- Health check fails because DB query fails
- App crashes on any database operation

**Solution**: Add DATABASE_URL reference variable (see steps above)

---

## 🚀 Best Practices for Railway + Django

1. **Always use environment variables** for configuration
2. **Use WhiteNoise** for static files (Railway doesn't serve Django static)
3. **Link PostgreSQL with reference variables** (not hardcoded URLs)
4. **Set DEBUG=False** in production
5. **Use Gunicorn** with multiple workers for production
6. **Implement health checks** for monitoring
7. **Run migrations** as part of deployment process
8. **Use .env file locally**, environment variables in Railway
9. **Keep secrets out of version control**
10. **Test locally with PostgreSQL** before deploying

---

## 📖 Additional Resources

- Railway Official Docs: https://docs.railway.app
- Railway Django Guide: https://docs.railway.app/guides/django
- Railway CLI: https://docs.railway.app/develop/cli
- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

---

*Last Updated: October 3, 2025*
*Status: Comprehensive guide based on Railway official documentation and best practices*

