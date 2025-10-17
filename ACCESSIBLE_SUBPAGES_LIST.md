# 📋 Complete List of Accessible Subpages - A2Z Mart Employee System

## 🏠 **Entry Point**
- **Employee Hub**: `/accounts/employee/hub/` - Main employee dashboard with navigation to all areas

---

## 🛍️ **PRODUCT MANAGEMENT SYSTEM**

### **Main Product Management**
- **Product Management Dashboard**: `/products/employee/manage/` - Main product management interface
- **Add New Product**: `/products/employee/add-product/` - Add new products with full form
- **Product Analytics**: `/products/employee/analytics/` - Product performance analytics

### **Product Operations**
- **Quick Edit Product**: `/products/employee/quick-edit/<uuid:product_id>/` - Quick edit individual products
- **Bulk Product Actions**: `/products/employee/bulk-actions/` - Bulk operations on products

### **Barcode Management**
- **Barcode Management**: `/products/employee/barcode-management/<uuid:product_id>/` - Manage barcodes for specific product
- **Bulk Barcode Upload**: `/products/employee/bulk-barcode/` - Upload multiple barcodes at once
- **Barcode Search**: `/products/employee/barcode-search/` - Search products by barcode
- **Delete Barcode**: `/products/employee/delete-barcode/<uuid:barcode_id>/` - Delete specific barcode

---

## 📦 **ORDER MANAGEMENT SYSTEM**

### **Order Dashboards**
- **Modern Order Dashboard**: `/accounts/orders/modern-dashboard/` - Modern order management interface
- **Classic Order Dashboard**: `/accounts/orders/dashboard/` - Traditional order management
- **Order List**: `/accounts/orders/list/` - List all orders
- **Order Analytics**: `/accounts/orders/analytics/` - Order performance analytics

### **Order Operations**
- **Order Detail**: `/accounts/orders/detail/<str:order_id>/` - View specific order details
- **Fulfillment Center**: `/accounts/orders/fulfillment/` - Order fulfillment management
- **Pick List**: `/accounts/orders/pick-list/<str:order_id>/` - Generate pick list for order
- **Update Fulfillment**: `/accounts/orders/update-fulfillment/<str:order_id>/` - Update fulfillment status
- **Bulk Order Actions**: `/accounts/orders/bulk-actions/` - Bulk operations on orders
- **Order Returns**: `/accounts/orders/returns/` - Handle order returns

### **Employee Order Management**
- **Employee Order Management**: `/accounts/employee/order-management/` - Employee-specific order management
- **Employee Order Detail**: `/accounts/employee/order/<str:order_id>/` - Employee view of order details
- **Assign Order**: `/accounts/employee/order/<str:order_id>/assign/` - Assign order to employee
- **Confirm Order**: `/accounts/employee/order/<str:order_id>/confirm/` - Confirm order
- **Update Order Status**: `/accounts/employee/order/<str:order_id>/update-status/` - Update order status
- **Cancel Order**: `/accounts/employee/order/<str:order_id>/cancel/` - Cancel order

---

## 📊 **ANALYTICS SYSTEM**

### **Main Analytics**
- **Analytics Dashboard**: `/accounts/analytics/dashboard/` - Main analytics overview
- **Sales Analytics**: `/accounts/analytics/sales/` - Sales performance analytics
- **Customer Analytics**: `/accounts/analytics/customers/` - Customer behavior analytics
- **Product Analytics**: `/accounts/analytics/products/` - Product performance analytics
- **Inventory Analytics**: `/accounts/analytics/inventory/` - Inventory analytics

### **Analytics Operations**
- **Export Analytics**: `/accounts/analytics/export/` - Export analytics data
- **Custom Report**: `/accounts/analytics/custom-report/` - Create custom reports
- **Real-time Analytics**: `/accounts/analytics/real-time/` - Real-time analytics dashboard

---

## 📦 **INVENTORY MANAGEMENT SYSTEM**

### **Inventory Dashboard**
- **Inventory Dashboard**: `/accounts/inventory/dashboard/` - Main inventory management
- **Stock Movements**: `/accounts/inventory/movements/` - Track stock movements
- **Stock Alerts**: `/accounts/inventory/alerts/` - Low stock alerts
- **Inventory Reports**: `/accounts/inventory/reports/` - Inventory reports

### **Inventory Operations**
- **Update Stock**: `/accounts/inventory/update-stock/<product_id>/` - Update stock for specific product
- **Bulk Stock Update**: `/accounts/inventory/bulk-update/` - Bulk stock updates
- **Store Locations**: `/accounts/inventory/locations/` - Manage store locations
- **Edit Store Location**: `/accounts/inventory/locations/edit/<location_id>/` - Edit specific location

---

## 👥 **CRM SYSTEM**

### **Customer Management**
- **CRM Dashboard**: `/accounts/crm/dashboard/` - Main CRM dashboard
- **Customer List**: `/accounts/crm/customers/` - List all customers
- **Customer Detail**: `/accounts/crm/customers/<int:user_id>/` - View specific customer
- **Customer Segments**: `/accounts/crm/segments/` - Customer segmentation
- **Customer Analytics**: `/accounts/crm/analytics/` - Customer analytics

### **Support System**
- **Customer Support**: `/accounts/crm/support/` - Support ticket management
- **Support Ticket Detail**: `/accounts/crm/support/ticket/<ticket_id>/` - View specific ticket
- **Create Support Ticket**: `/accounts/crm/support/create/` - Create new support ticket
- **My Support Tickets**: `/accounts/crm/support/my-tickets/` - Employee's assigned tickets

---

## 🛒 **CUSTOMER EXPERIENCE SYSTEM**

### **Wishlist Management**
- **Wishlist**: `/accounts/wishlist/` - Customer wishlist
- **Add to Wishlist**: `/accounts/wishlist/add/<product_id>/` - Add product to wishlist
- **Remove from Wishlist**: `/accounts/wishlist/remove/<product_id>/` - Remove from wishlist
- **Move to Cart**: `/accounts/wishlist/move-to-cart/<product_id>/` - Move wishlist item to cart

### **Customer Features**
- **Recently Viewed**: `/accounts/recently-viewed/` - Recently viewed products
- **Track Product View**: `/accounts/track-view/<product_id>/` - Track product views
- **Product Comparison**: `/accounts/compare/` - Compare products
- **Product Recommendations**: `/accounts/recommendations/` - Product recommendations
- **Quick Reorder**: `/accounts/quick-reorder/<str:order_id>/` - Quick reorder functionality

### **Loyalty System**
- **Customer Loyalty**: `/accounts/loyalty/` - Loyalty program
- **Redeem Points**: `/accounts/loyalty/redeem/` - Redeem loyalty points

### **Product Bundles**
- **Product Bundles**: `/accounts/bundles/` - Product bundles
- **Bundle Detail**: `/accounts/bundles/<bundle_id>/` - View specific bundle
- **Add Bundle to Cart**: `/accounts/bundles/<bundle_id>/add-to-cart/` - Add bundle to cart

### **Social Features**
- **Social Proof**: `/accounts/social-proof/<product_id>/` - Social proof for products
- **Personalized Homepage**: `/accounts/personalized-home/` - Personalized homepage

---

## 🏠 **ADDRESS MANAGEMENT SYSTEM**

### **Address Management**
- **Address Management**: `/accounts/address/` - Main address management
- **Update Address**: `/accounts/address/update/` - Update shipping address
- **Comprehensive Address Management**: `/accounts/addresses/` - Comprehensive address management

### **Address Operations**
- **Geocode Address**: `/accounts/address/geocode/` - Geocode addresses
- **Reverse Geocode**: `/accounts/address/reverse-geocode/` - Reverse geocoding
- **Find Nearby Stores**: `/accounts/address/nearby-stores/` - Find nearby stores
- **Store Locator**: `/accounts/store-locator/` - Store locator
- **Click and Collect**: `/accounts/click-collect/` - Click and collect
- **Delivery Estimate**: `/accounts/delivery-estimate/` - Delivery estimates

### **Address Profile Management**
- **Update Profile Address**: `/accounts/addresses/profile/update/` - Update profile address
- **Add Shipping Address**: `/accounts/addresses/shipping/add/` - Add shipping address
- **Edit Shipping Address**: `/accounts/addresses/shipping/<uuid:address_id>/edit/` - Edit shipping address
- **Delete Shipping Address**: `/accounts/addresses/shipping/<uuid:address_id>/delete/` - Delete shipping address
- **Set Default Address**: `/accounts/addresses/shipping/<uuid:address_id>/set-default/` - Set default address
- **Address Validation**: `/accounts/addresses/validate/` - Validate addresses

---

## ⚙️ **ADMIN SYSTEM**

### **Admin Dashboard**
- **Admin Dashboard**: `/accounts/admin/dashboard/` - Main admin dashboard
- **User Management**: `/accounts/admin/users/` - Manage users
- **User Detail**: `/accounts/admin/users/<int:user_id>/` - View specific user
- **Edit User**: `/accounts/admin/users/<int:user_id>/edit/` - Edit user details

### **Admin Operations**
- **Product Management**: `/accounts/admin/products/` - Admin product management
- **Product Detail Admin**: `/accounts/admin/products/<product_id>/` - Admin view of product
- **Order Management Admin**: `/accounts/admin/orders/` - Admin order management
- **System Settings**: `/accounts/admin/settings/` - System settings
- **Store Locations Admin**: `/accounts/admin/locations/` - Admin store locations
- **Employee Management**: `/accounts/admin/employees/` - Manage employees
- **System Reports**: `/accounts/admin/reports/` - System reports
- **Backup Restore**: `/accounts/admin/backup/` - Backup and restore
- **System Logs**: `/accounts/admin/logs/` - System logs

---

## 🛒 **SHOPPING SYSTEM**

### **Cart & Checkout**
- **Shopping Cart**: `/accounts/cart/` - Shopping cart
- **Add to Cart**: `/accounts/add-to-cart/<uid>/` - Add product to cart
- **Update Cart Item**: `/accounts/update_cart_item/` - Update cart item
- **Update Cart**: `/accounts/update_cart/<uuid:cart_item_id>/` - Update cart
- **Remove from Cart**: `/accounts/remove-cart/<uid>/` - Remove from cart
- **Remove Cart Item**: `/accounts/remove_from_cart/<uuid:cart_item_id>/` - Remove cart item
- **Remove Coupon**: `/accounts/remove-coupon/<cart_id>/` - Remove coupon
- **Checkout**: `/accounts/checkout/` - Checkout process

### **Order History**
- **Order History**: `/accounts/order-history/` - Customer order history
- **Order Details**: `/accounts/order-details/<str:order_id>/` - Order details
- **Order Tracking**: `/accounts/order-tracking/<str:order_id>/` - Track order
- **Download Invoice**: `/accounts/order-details/<str:order_id>/download/` - Download invoice

---

## 👤 **ACCOUNT MANAGEMENT**

### **Authentication**
- **Login**: `/accounts/login/` - User login
- **Account Login**: `/accounts/account-login/` - Employee login
- **Register**: `/accounts/register/` - User registration
- **Logout**: `/accounts/logout/` - User logout

### **Password Management**
- **Change Password**: `/accounts/change-password/` - Change password
- **Password Reset**: `/accounts/password_reset/` - Password reset
- **Password Reset Done**: `/accounts/password_reset/done/` - Password reset confirmation
- **Password Reset Confirm**: `/accounts/reset/<uidb64>/<token>/` - Confirm password reset
- **Password Reset Complete**: `/accounts/reset/done/` - Password reset complete

### **Profile Management**
- **Profile View**: `/accounts/profile/<str:username>/` - View user profile
- **Shipping Address**: `/accounts/shipping-address/` - Update shipping address
- **Delete Account**: `/accounts/delete-account/` - Delete user account

### **Account Settings**
- **Account Settings**: `/accounts/settings/` - Main account settings
- **Personal Information**: `/accounts/settings/personal-information/` - Personal info settings
- **Login Security**: `/accounts/settings/login-security/` - Security settings
- **Change Password Settings**: `/accounts/settings/change-password/` - Change password
- **Revoke Session**: `/accounts/settings/revoke-session/<int:session_id>/` - Revoke session
- **Notification Preferences**: `/accounts/settings/notifications/` - Notification settings
- **Update Notification Preference**: `/accounts/settings/update-notification-preference/` - Update notifications
- **Connected Accounts**: `/accounts/settings/connected-accounts/` - Connected accounts
- **Disconnect Account**: `/accounts/settings/disconnect-account/<int:account_id>/` - Disconnect account
- **Two Factor Setup**: `/accounts/settings/two-factor-setup/` - 2FA setup
- **Verify Phone 2FA**: `/accounts/settings/verify-phone-2fa/` - Verify phone 2FA
- **Danger Zone**: `/accounts/settings/danger-zone/` - Account deletion
- **Upload Profile Picture**: `/accounts/settings/upload-profile-picture/` - Upload profile picture
- **Delete Profile Picture**: `/accounts/settings/delete-profile-picture/` - Delete profile picture
- **Test Settings**: `/accounts/settings/test/` - Test settings page
- **Modern Account Page**: `/accounts/modern/` - Modern account page

---

## 🏢 **BUSINESS SYSTEM**

### **Business Forms**
- **Business Form**: `/accounts/business-form/` - Business form submission
- **Submit Business Form**: `/accounts/business-form/submit/` - Submit business form
- **Get Business Data**: `/accounts/business-form/data/` - Get business data
- **Business Form Admin**: `/accounts/business-form/admin/` - Business form admin

---

## 🍺 **BAR SYSTEM**

### **Bar Section**
- **Bar Home**: `/products/bar/` - Bar section homepage
- **Bar Products**: `/products/bar/products/` - Bar products
- **Bar Product Detail**: `/products/bar/product/<slug>/` - Bar product details
- **Bar Categories**: `/products/bar/categories/` - Bar categories
- **Add to Bar Cart**: `/products/bar/add-to-cart/<uuid:product_id>/` - Add to bar cart

---

## 🛍️ **PRODUCT SYSTEM**

### **Product Operations**
- **Product List**: `/products/` - All products
- **Product Detail**: `/products/<slug>/` - Product details
- **Product Reviews**: `/products/product-reviews/` - Product reviews
- **Edit Review**: `/products/product-reviews/edit/<uuid:review_uid>/` - Edit review
- **Like Review**: `/products/like-review/<review_uid>/` - Like review
- **Dislike Review**: `/products/dislike-review/<review_uid>/` - Dislike review
- **Add Review**: `/products/add-review/<slug>/` - Add review
- **Delete Review**: `/products/<slug>/<review_uid>/delete/` - Delete review

### **Product Wishlist**
- **Wishlist View**: `/products/wishlist/` - Product wishlist
- **Add to Wishlist**: `/products/wishlist/add/<uid>/` - Add to wishlist
- **Move to Cart**: `/products/wishlist/move_to_cart/<uid>/` - Move to cart
- **Remove from Wishlist**: `/products/wishlist/remove/<uid>/` - Remove from wishlist

---

## 🏠 **HOME SYSTEM**

### **Main Pages**
- **Homepage Redirect**: `/` - Main homepage redirect
- **A2Z Mart**: `/a2z-mart/` - Main e-commerce homepage
- **Products Only**: `/a2z-mart/products/` - Products only view
- **A2Z Bar Redirect**: `/a2z-bar/` - Redirect to bar system
- **Rayan Brayan**: `/rayan-brayan/` - Community page

### **Other Pages**
- **Product Search**: `/search/` - Search products
- **Contact**: `/contact/` - Contact page
- **About**: `/about/` - About page
- **Terms**: `/terms/` - Terms and conditions
- **Privacy**: `/privacy/` - Privacy policy
- **Demo Design System**: `/demo/` - Design system demo

---

## 🔍 **SEARCH SYSTEM**

### **Search Operations**
- **Product Search**: `/search/products/` - Search products
- **Category Search**: `/search/categories/` - Search categories
- **Search Suggestions**: `/search/suggestions/` - Search suggestions
- **Advanced Search**: `/search/advanced/` - Advanced search

---

## 🏥 **SYSTEM HEALTH**

### **Health Checks**
- **Health Check**: `/health/` - System health check
- **Readiness Check**: `/ready/` - System readiness
- **Liveness Check**: `/live/` - System liveness

---

## 🔧 **ADMIN PANEL**
- **Django Admin**: `/admin/` - Django admin panel

---

## 📊 **SUMMARY**

### **Total Accessible Pages: 150+**

**By Category:**
- 🛍️ **Product Management**: 9 pages
- 📦 **Order Management**: 15 pages
- 📊 **Analytics**: 8 pages
- 📦 **Inventory Management**: 8 pages
- 👥 **CRM System**: 9 pages
- 🛒 **Customer Experience**: 15 pages
- 🏠 **Address Management**: 12 pages
- ⚙️ **Admin System**: 12 pages
- 🛒 **Shopping System**: 8 pages
- 👤 **Account Management**: 20 pages
- 🏢 **Business System**: 4 pages
- 🍺 **Bar System**: 5 pages
- 🛍️ **Product System**: 8 pages
- 🏠 **Home System**: 8 pages
- 🔍 **Search System**: 4 pages
- 🏥 **System Health**: 3 pages
- 🔧 **Admin Panel**: 1 page

### **Key Entry Points:**
1. **Employee Hub**: `/accounts/employee/hub/` - Main employee dashboard
2. **Product Management**: `/products/employee/manage/` - Product management
3. **Order Management**: `/accounts/orders/modern-dashboard/` - Order management
4. **Analytics**: `/accounts/analytics/dashboard/` - Analytics dashboard
5. **Admin Dashboard**: `/accounts/admin/dashboard/` - Admin dashboard

---

*This list represents all accessible subpages in the A2Z Mart employee system. Each page has been tested and styled for proper functionality and visual consistency.*
