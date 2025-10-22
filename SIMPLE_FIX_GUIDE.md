# 🚨 SIMPLE FIX GUIDE

## The Issue
Your Cart model has a `coupon` field:
```python
coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
```

Django automatically creates a `coupon_id` column in the database for this ForeignKey, but the column is missing from your database table.

## 🚀 SIMPLE FIX

**Option 1: Direct SQL (Recommended)**
```sql
-- Connect to your PostgreSQL database and run:
ALTER TABLE accounts_cart ADD COLUMN IF NOT EXISTS coupon_id UUID NULL;
```

**Option 2: If IF NOT EXISTS doesn't work:**
```sql
-- Connect to your PostgreSQL database and run:
ALTER TABLE accounts_cart ADD COLUMN coupon_id UUID NULL;
```

## 📋 What This Does
- ✅ Adds the missing `coupon_id` column to `accounts_cart` table
- ✅ Resolves the deployment error
- ✅ Allows your application to work normally
- ✅ Minimal change with maximum impact

## 🧪 After Fix
Your application should work without the database errors. The `coupon_id` column will allow Django to properly handle the coupon relationship in your Cart model.

## 🎯 Why You Need This
- Your Cart model references coupons
- Django expects a `coupon_id` column for the ForeignKey
- Without it, the application crashes when accessing cart data
- This is a required column for your current model structure

---

**🎉 This simple fix will resolve your deployment issues immediately!**
