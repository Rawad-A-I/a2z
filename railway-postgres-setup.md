# Railway PostgreSQL Setup Guide

## Required Services for Django Deployment:

### 1. **PostgreSQL Database Service**
- Add PostgreSQL service in Railway dashboard
- Railway provides: `DATABASE_URL`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`
- Data persists across deployments

### 2. **Redis Service (Optional but Recommended)**
- For caching and session storage
- Better performance than database sessions
- Required for Celery if using background tasks

### 3. **App Service (Your Django App)**
- Main application service
- Handles HTTP requests
- Connects to PostgreSQL database

## Environment Variables to Set in Railway:

```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=*.railway.app,your-domain.up.railway.app
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port/0
```

## Health Check Configuration:
- Railway will check `/health/` endpoint
- Our current health check setup is correct
- Can configure custom health check path in Railway dashboard
