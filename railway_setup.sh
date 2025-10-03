#!/bin/bash

echo "🚀 Setting up Railway Django deployment..."
echo "=========================================="

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if logged in
echo "🔐 Checking Railway login status..."
railway whoami

echo ""
echo "📊 Current Railway project status:"
railway status

echo ""
echo "🔧 Setting up environment variables..."

# Generate SECRET_KEY
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
echo "Generated SECRET_KEY: $SECRET_KEY"

echo ""
echo "📋 Next steps to complete deployment:"
echo "====================================="
echo ""
echo "1. 🌐 Open Railway Dashboard:"
echo "   https://railway.com/project/3015db32-eb36-4f36-85ae-b6bb301d504f"
echo ""
echo "2. 📦 Deploy from GitHub:"
echo "   - Click 'New' → 'GitHub Repo'"
echo "   - Select: Rawad-A-I/a2z"
echo "   - Wait for build (5-10 minutes)"
echo ""
echo "3. 🔗 Link Database (CRITICAL!):"
echo "   - Click on your web service"
echo "   - Go to 'Variables' tab"
echo "   - Click 'New Variable' → 'Add a Service Variable'"
echo "   - Select: Postgres → DATABASE_URL"
echo "   - Click 'Add'"
echo ""
echo "4. ⚙️ Set Environment Variables:"
echo "   SECRET_KEY = $SECRET_KEY"
echo "   DEBUG = False"
echo "   ALLOWED_HOSTS = *.railway.app"
echo "   CSRF_TRUSTED_ORIGINS = https://*.railway.app"
echo ""
echo "5. 🚀 After deployment, run these commands:"
echo "   railway link"
echo "   railway run python manage.py migrate"
echo "   railway run python manage.py createsuperuser"
echo "   railway domain"
echo ""
echo "6. ✅ Test your deployment:"
echo "   curl https://your-app.railway.app/health/"
echo ""
echo "=========================================="
echo "🎯 Your Railway project is ready!"
echo "Project URL: https://railway.com/project/3015db32-eb36-4f36-85ae-b6bb301d504f"
echo "=========================================="
