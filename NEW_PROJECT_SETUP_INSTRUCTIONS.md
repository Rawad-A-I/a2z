# Setting Up Your New Railway Project
## Project: django-ecommerce-new

---

## ✅ What's Been Done

1. ✅ **New Railway project created**: `django-ecommerce-new`
2. ✅ **Project URL**: https://railway.com/project/3015db32-eb36-4f36-85ae-b6bb301d504f
3. ✅ **PostgreSQL database added**: Ready to use

---

## 🚀 Complete Setup Steps

### Step 1: Deploy from GitHub (Recommended)

Since you already have your code on GitHub, let's deploy from there:

1. **Open your Railway project**:
   ```
   https://railway.com/project/3015db32-eb36-4f36-85ae-b6bb301d504f
   ```

2. **Click "New" → "GitHub Repo"**

3. **Select your repository**: `Rawad-A-I/a2z`

4. **Railway will auto-detect Django** and start building

---

### Step 2: Link Database to Web Service

**CRITICAL STEP** (Don't skip this!):

Once your web service is deployed:

1. Click on your **web service** (not Postgres)
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Select **"Add a Service Variable"**
5. Choose:
   - **Service**: `Postgres`
   - **Variable**: `DATABASE_URL`
6. Click **"Add"**

This creates: `DATABASE_URL = ${{Postgres.DATABASE_URL}}`

---

### Step 3: Set Environment Variables

In your web service → Variables tab, add:

#### **SECRET_KEY**
Generate a strong key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy the output and add it as `SECRET_KEY`

#### **Other Required Variables**:
```
DEBUG = False
ALLOWED_HOSTS = *.railway.app
CSRF_TRUSTED_ORIGINS = https://*.railway.app
```

---

### Step 4: Wait for Deployment

Railway will:
1. Build your Docker image (5-10 minutes)
2. Run migrations (from your Dockerfile)
3. Collect static files
4. Start Gunicorn
5. Check health endpoint (`/health/`)
6. Route traffic once healthy

Watch the logs in Railway dashboard.

---

### Step 5: Run Migrations & Create Superuser

Once deployed, use Railway CLI:

```bash
# Make sure you're linked to the right project
railway link

# Select the new project: django-ecommerce-new
# Select service: (your web service)

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files (if needed)
railway run python manage.py collectstatic --noinput
```

---

### Step 6: Get Your App URL

```bash
railway domain
```

Or check in Railway dashboard → Your Service → Settings → Domains

---

### Step 7: Test Your Deployment

```bash
# Test health check
curl https://your-app.railway.app/health/

# Expected response:
# {"status":"healthy","checks":{"database":"ok"}}

# Test admin panel
# Visit: https://your-app.railway.app/admin/
```

---

## 🔧 Alternative: Deploy via Railway Dashboard Only

If you prefer not to use CLI:

1. **Open Railway Dashboard**:
   ```
   https://railway.com/project/3015db32-eb36-4f36-85ae-b6bb301d504f
   ```

2. **Add GitHub Service**:
   - Click "New"
   - Select "GitHub Repo"
   - Choose `Rawad-A-I/a2z`
   - Railway auto-deploys

3. **Add DATABASE_URL Variable**:
   - Click web service → Variables
   - New Variable → Service Variable
   - Postgres → DATABASE_URL

4. **Set Environment Variables**:
   - SECRET_KEY (generate new one)
   - DEBUG = False
   - ALLOWED_HOSTS = *.railway.app
   - CSRF_TRUSTED_ORIGINS = https://*.railway.app

5. **Wait for Deployment**

6. **Access Railway Shell** (for migrations):
   - In dashboard → Service → "Terminal" or "Shell"
   - Run: `python manage.py migrate`
   - Run: `python manage.py createsuperuser`

---

## 📊 Project Structure

Your new Railway project will have:

```
django-ecommerce-new (Project)
├── Postgres (Database Service)
│   └── Provides DATABASE_URL
│
└── Web Service (Django App from GitHub)
    ├── Environment Variables:
    │   ├── DATABASE_URL = ${{Postgres.DATABASE_URL}}
    │   ├── SECRET_KEY
    │   ├── DEBUG = False
    │   └── ALLOWED_HOSTS = *.railway.app
    │
    └── Deployment:
        ├── Build (Dockerfile)
        ├── Migrations (auto via Dockerfile)
        ├── Static Files (auto collected)
        ├── Gunicorn (web server)
        └── Health Check (/health/)
```

---

## ✅ Checklist

Complete these in order:

- [x] Railway project created
- [x] PostgreSQL database added
- [ ] GitHub repo connected
- [ ] Web service deployed
- [ ] DATABASE_URL linked (**CRITICAL**)
- [ ] Environment variables set
- [ ] Migrations run
- [ ] Superuser created
- [ ] Health check passing
- [ ] App accessible

---

## 🎯 Success Indicators

You'll know it's working when:

1. ✅ Railway dashboard shows web service as "Active"
2. ✅ Health indicator is green
3. ✅ Can access: `https://your-app.railway.app`
4. ✅ Health endpoint returns: `{"status":"healthy"}`
5. ✅ Admin panel works
6. ✅ Database queries execute

---

## 🚨 Common Issues

### Build Fails
- Check Railway logs for errors
- Verify `requirements.txt` is complete
- Check `Dockerfile` syntax

### DATABASE_URL Not Found
- **Most Common Issue!**
- Make sure you linked it as a reference variable
- Don't hardcode the URL

### Health Check Fails
- Check DATABASE_URL is set
- Check migrations completed
- View logs for database connection errors

### Can't Run Migrations
```bash
# Make sure you're linked to the right service
railway status

# Should show: Project: django-ecommerce-new
```

---

## 💡 Pro Tips

1. **Use GitHub Deployment** - More reliable than CLI upload
2. **Always use Reference Variables** for DATABASE_URL
3. **Generate Strong SECRET_KEY** (50+ characters)
4. **Monitor Logs** during first deployment
5. **Test Health Endpoint** before accessing main app
6. **Create Superuser** right after successful deployment

---

## 📞 Need Help?

If something doesn't work:

1. **Check Railway Logs**:
   - Dashboard → Service → "Logs" tab

2. **Check Variables**:
   ```bash
   railway variables
   ```
   
3. **Test Database Connection**:
   ```bash
   railway run python manage.py check --database default
   ```

4. **Review Documentation**:
   - RAILWAY_COMPLETE_GUIDE.md
   - QUICK_FIX_GUIDE.md

---

## 🎉 Next Steps After Deployment

Once your app is live:

1. **Test all features**
2. **Add custom domain** (optional)
3. **Set up monitoring**
4. **Configure backups**
5. **Enable CI/CD** (Railway auto-deploys on push)

---

**Your new Railway project is ready!**

**Start here**: Deploy from GitHub using the Railway dashboard! 🚀

---

*Project ID: 3015db32-eb36-4f36-85ae-b6bb301d504f*
*Created: October 3, 2025*

