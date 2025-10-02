# 🛒 Django eCommerce Website - Complete User Manual

## 📋 **Table of Contents**

1. [Quick Start Guide](#quick-start-guide)
2. [System Overview](#system-overview)
3. [Customer Features](#customer-features)
4. [Employee Features](#employee-features)
5. [Admin Features](#admin-features)
6. [Technical Setup](#technical-setup)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [API Documentation](#api-documentation)

---

## 🚀 **Quick Start Guide**

### **Step 1: Setup**
```bash
# Navigate to project directory
cd Django-eCommerce-Website-main

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### **Step 2: Access the Website**
- **Main Website**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Admin Dashboard**: http://localhost:8000/user/admin/dashboard/

---

## 🏪 **System Overview**

### **What This System Provides**
Your Django eCommerce website is now a **complete, professional online store** with:

- 🏪 **Multi-location support** for physical stores
- 📦 **Advanced inventory management** with real-time tracking
- 👥 **Comprehensive CRM** with loyalty program
- 📊 **Professional analytics** and reporting
- 🗺️ **OpenStreetMap integration** for location services
- 🎯 **Enhanced customer experience** with personalization
- ⚙️ **Complete admin system** for full control

### **Key Features**
- ✅ **Real-time inventory tracking** with low stock alerts
- ✅ **Product variants** (size, color, material combinations)
- ✅ **Product bundles** for "buy together" offers
- ✅ **Customer loyalty program** with points and tiers
- ✅ **Order fulfillment workflow** (pending → shipped → delivered)
- ✅ **Multi-location store management** with Google Maps
- ✅ **Advanced analytics** and reporting
- ✅ **Customer support** ticket system
- ✅ **Mobile responsive** design

---

## 👥 **Customer Features**

### **Shopping Experience**
- **Product Browsing**: Browse products by category with advanced filtering
- **Product Details**: View detailed product information with variants
- **Product Comparison**: Compare up to 4 products side-by-side
- **Product Recommendations**: AI-powered personalized recommendations
- **Recently Viewed**: Track recently viewed products
- **Wishlist**: Save products for later purchase

### **Account Management**
- **User Registration**: Create account with email verification
- **Profile Management**: Update personal information and preferences
- **Address Management**: Manage shipping addresses with OpenStreetMap integration
- **Order History**: View past orders and track current orders
- **Loyalty Program**: Earn points and unlock tier benefits

### **Shopping Cart & Checkout**
- **Add to Cart**: Add products with variants to cart
- **Cart Management**: Update quantities, remove items
- **Coupon Codes**: Apply discount coupons
- **Checkout Process**: Secure checkout with multiple payment options
- **Order Tracking**: Track order status and delivery

### **Customer Support**
- **Support Tickets**: Create and track support requests
- **Live Chat**: Real-time customer support
- **FAQ Section**: Self-service help center
- **Return Management**: Easy return and refund process

---

## 👨‍💼 **Employee Features**

### **Order Management**
- **Order Dashboard**: View all orders with filtering options
- **Order Assignment**: Assign orders to specific employees
- **Order Fulfillment**: Track order through fulfillment process
- **Pick Lists**: Generate warehouse pick lists
- **Order Status Updates**: Update order status and tracking

### **Inventory Management**
- **Stock Tracking**: Real-time inventory levels
- **Stock Movements**: Track all stock movements
- **Low Stock Alerts**: Automatic alerts for low stock
- **Bulk Updates**: Update multiple products at once
- **Inventory Reports**: Detailed inventory analytics

### **Customer Management**
- **Customer Profiles**: View detailed customer information
- **Customer Support**: Handle support tickets
- **Customer Analytics**: Customer behavior insights
- **Loyalty Management**: Manage loyalty program

### **Store Operations**
- **Store Locations**: Manage multiple store locations
- **Store Locator**: Help customers find nearby stores
- **Click & Collect**: Manage in-store pickup orders
- **Delivery Management**: Coordinate deliveries

---

## ⚙️ **Admin Features**

### **System Management**
- **Admin Dashboard**: Comprehensive system overview
- **User Management**: Manage customers and employees
- **Product Management**: Add, edit, and manage products
- **Order Management**: Oversee all orders and fulfillment
- **System Settings**: Configure system parameters

### **Analytics & Reporting**
- **Sales Analytics**: Revenue, orders, and performance metrics
- **Customer Analytics**: Customer behavior and segmentation
- **Product Analytics**: Product performance and trends
- **Inventory Analytics**: Stock levels and movement analysis
- **Custom Reports**: Generate custom reports
- **Data Export**: Export data to CSV/Excel

### **Store Management**
- **Multi-Location Support**: Manage multiple store locations
- **Store Configuration**: Set store hours, contact info
- **Employee Management**: Manage staff and permissions
- **System Monitoring**: Monitor system health and logs

### **Advanced Features**
- **Backup & Restore**: System backup and recovery
- **Security Management**: User permissions and access control
- **Integration Management**: Third-party service integrations
- **Performance Monitoring**: System performance tracking

---

## 🔧 **Technical Setup**

### **System Requirements**
- Python 3.8+
- Django 5.0+
- SQLite (default) or PostgreSQL
- Virtual environment

### **Installation**
```bash
# Navigate to project directory
cd Django-eCommerce-Website-main

# Activate virtual environment
venv\Scripts\activate

# Install dependencies (simplified - no PostgreSQL needed)
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

**Note**: The project uses SQLite by default (no additional database setup needed). For production with PostgreSQL, use `requirements-production.txt`.

### **Configuration**
1. **Database**: Configure database settings in `ecomm/settings.py`
2. **Email**: Set up email configuration for notifications
3. **Maps**: OpenStreetMap is pre-configured (no API key needed)
4. **Storage**: Configure media and static file storage

### **Production Deployment**
```bash
# Set production settings
export DJANGO_SETTINGS_MODULE=ecomm.settings

# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Start production server
gunicorn ecomm.wsgi:application
```

---

## 🧪 **Testing**

### **Run All Tests**
```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test suite
python tests/run_all_tests.py test_authentication
python tests/run_all_tests.py test_products
python tests/run_all_tests.py test_orders
python tests/run_all_tests.py test_inventory
python tests/run_all_tests.py test_crm
python tests/run_all_tests.py test_analytics
python tests/run_all_tests.py test_address_maps
python tests/run_all_tests.py test_customer_experience
python tests/run_all_tests.py test_admin
```

### **Test Coverage**
- ✅ **Authentication**: User registration, login, logout
- ✅ **Products**: Product management, variants, bundles
- ✅ **Orders**: Order creation, fulfillment, tracking
- ✅ **Inventory**: Stock management, alerts, movements
- ✅ **CRM**: Customer management, loyalty program
- ✅ **Analytics**: Reporting, data export
- ✅ **Address/Maps**: Location services, store locator
- ✅ **Customer Experience**: Wishlist, recommendations
- ✅ **Admin**: System management, user management

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Database Migration Errors**
```bash
# Reset migrations
python manage.py migrate --fake-initial
python manage.py migrate
```

#### **2. Static Files Not Loading**
```bash
# Collect static files
python manage.py collectstatic
```

#### **3. Permission Errors**
```bash
# Check file permissions
chmod 755 manage.py
```

#### **4. Import Errors**
```bash
# Check virtual environment
which python
pip list
```

### **Debug Mode**
```python
# In settings.py
DEBUG = True
```

### **Logging**
```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

---

## 📚 **API Documentation**

### **Authentication Endpoints**
- `POST /user/register/` - User registration
- `POST /user/login/` - User login
- `GET /user/logout/` - User logout

### **Product Endpoints**
- `GET /products/` - List products
- `GET /products/<id>/` - Product details
- `POST /user/wishlist/add/<id>/` - Add to wishlist
- `POST /user/compare/` - Product comparison

### **Cart Endpoints**
- `GET /user/cart/` - View cart
- `POST /user/add-to-cart/<id>/` - Add to cart
- `POST /user/update_cart_item/` - Update cart item
- `POST /user/remove-cart/<id>/` - Remove from cart

### **Order Endpoints**
- `GET /user/order-history/` - Order history
- `GET /user/order-details/<id>/` - Order details
- `POST /user/orders/` - Create order

### **Address/Maps Endpoints**
- `GET /user/address/` - Address management
- `POST /user/address/geocode/` - Geocode address
- `POST /user/address/reverse-geocode/` - Reverse geocode
- `POST /user/address/nearby-stores/` - Find nearby stores

### **Admin Endpoints**
- `GET /user/admin/dashboard/` - Admin dashboard
- `GET /user/admin/users/` - User management
- `GET /user/admin/products/` - Product management
- `GET /user/admin/orders/` - Order management

---

## 🎯 **Getting Started Checklist**

### **For Customers**
- [ ] Create user account
- [ ] Complete profile setup
- [ ] Add shipping address
- [ ] Browse products
- [ ] Add items to cart
- [ ] Complete checkout
- [ ] Track order status

### **For Employees**
- [ ] Access employee dashboard
- [ ] Review assigned orders
- [ ] Update order status
- [ ] Manage inventory
- [ ] Handle customer support

### **For Admins**
- [ ] Access admin dashboard
- [ ] Configure store locations
- [ ] Set up inventory alerts
- [ ] Configure loyalty program
- [ ] Review analytics
- [ ] Manage users

---

## 📞 **Support**

### **Documentation**
- This user manual
- Code comments and docstrings
- Test files for examples

### **Community**
- GitHub repository
- Issue tracker
- Discussion forums

### **Professional Support**
- Contact system administrator
- Technical support team
- Custom development services

---

## 🎉 **Congratulations!**

Your Django eCommerce website is now a **complete, professional online store** that can compete with major retailers while maintaining the personal touch of a physical store!

**Key Benefits:**
- 🏪 **Multi-location support** for physical stores
- 📦 **Real-time inventory management**
- 👥 **Customer relationship management**
- 📊 **Advanced analytics and reporting**
- 🗺️ **Location services with OpenStreetMap**
- 🎯 **Personalized customer experience**
- ⚙️ **Complete admin control**

**Ready to launch your online store!** 🚀✨
