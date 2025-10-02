# 🛒 Django eCommerce Website

A complete, professional eCommerce solution for physical stores with multi-location support, advanced inventory management, CRM, analytics, and OpenStreetMap integration.

## 🚀 **Quick Start**

### **Option 1: SQLite (Default - No Setup Required)**
   ```bash
# Setup (simplified - no PostgreSQL needed)
cd Django-eCommerce-Website-main
venv\Scripts\activate
   pip install -r requirements.txt
python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

### **Option 2: PostgreSQL (Production Ready)**
   ```bash
# Setup with PostgreSQL
cd Django-eCommerce-Website-main
venv\Scripts\activate
   pip install -r requirements.txt
   
# Setup PostgreSQL database
python setup_postgresql.py
   
# Run migrations
python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

### **Option 3: Docker (Full Stack)**
   ```bash
# Run with Docker (includes PostgreSQL, Redis, Celery)
docker-compose up --build
   ```

**Access:** http://localhost:8000

## ✨ **Key Features**

- 🏪 **Multi-location store support** with OpenStreetMap integration
- 📦 **Real-time inventory management** with low stock alerts
- 👥 **Customer relationship management** with loyalty program
- 📊 **Advanced analytics** and reporting dashboard
- 🎯 **Personalized customer experience** with recommendations
- ⚙️ **Complete admin system** for full control
- 📱 **Mobile responsive** design
- 🛒 **Advanced shopping cart** with variants and bundles
- 📋 **Order fulfillment workflow** with tracking
- 🎁 **Product bundles** and comparison features

## 🎯 **For Different Users**

### **Customers**
- Browse products with advanced filtering
- Product comparison and recommendations
- Wishlist and recently viewed products
- Loyalty program with points and tiers
- Address management with maps
- Order tracking and history

### **Employees**
- Order management and fulfillment
- Inventory tracking and alerts
- Customer support tickets
- Store operations management
- Analytics and reporting

### **Admins**
- Complete system administration
- User and employee management
- Product and inventory management
- Analytics and reporting
- System configuration and monitoring

## 🧪 **Testing**

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific tests
python tests/run_all_tests.py test_authentication
python tests/run_all_tests.py test_products
python tests/run_all_tests.py test_orders
```

## 📚 **Documentation**

- **[Complete User Manual](USER_MANUAL.md)** - Comprehensive guide for all users
- **Test Suite** - Full test coverage for all features
- **API Documentation** - RESTful API endpoints

## 🛠️ **Technical Stack**

- **Backend**: Django 5.0+ with Python 3.8+
- **Database**: SQLite (default) or PostgreSQL
- **Frontend**: Bootstrap 4, HTML5, CSS3, JavaScript
- **Maps**: OpenStreetMap with Leaflet.js
- **Testing**: Django Test Framework
- **Deployment**: Docker support included

## 🎉 **What You Get**

Your Django eCommerce website is now a **complete, professional online store** that can compete with major retailers while maintaining the personal touch of a physical store!

**Ready to launch your online store!** 🚀✨

---

**For detailed documentation, see [USER_MANUAL.md](USER_MANUAL.md)**