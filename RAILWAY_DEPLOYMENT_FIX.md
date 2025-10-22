# 🚀 Railway Deployment Fix Guide

## 📋 Issues Being Fixed

Your deployment is failing with three critical errors:

1. **Missing `coupon_id` column** in `accounts_cart` table
2. **Duplicate `is_size_variant` column** in `products_product` table
3. **Wrong constraint count** for `accounts_cart` unique constraints

## 🔧 Solution Overview

We've created a comprehensive fix that:
- Adds the missing `coupon_id` column with proper foreign key
- Removes problematic `unique_together` constraints that don't handle NULL properly
- Adds partial unique indexes that work correctly with NULL values
- Marks conflicting product migrations as applied to prevent duplicate column errors

## ⚡ Quick Fix (Recommended)

### Step 1: Run the Fix Script on Railway

```bash
railway run python fix_all_database_issues.py
```

This will:
- ✅ Add missing `coupon_id` column
- ✅ Fix cart constraints
- ✅ Mark problematic migrations as applied
- ✅ Verify all changes

### Step 2: Commit and Deploy

```bash
git add .
git commit -m "Fix database schema issues for deployment"
git push
```

Railway will automatically deploy with the fixed schema.

## 🔍 Detailed Explanation

### Problem 1: Missing `coupon_id` Column

**Error:**
```
psycopg2.errors.UndefinedColumn: column accounts_cart.coupon_id does not exist
```

**Cause:** The `Cart` model has a ForeignKey to `Coupon`, which Django expects as a `coupon_id` column in the database, but it was never created.

**Fix:** 
- Migration `0031_comprehensive_fix.py` adds the column with proper foreign key constraint
- Alternatively, `fix_all_database_issues.py` adds it directly

### Problem 2: Duplicate Column Errors

**Error:**
```
django.db.utils.ProgrammingError: column "is_size_variant" of relation "products_product" already exists
```

**Cause:** Multiple migrations tried to add the same column, and some were already applied in production.

**Fix:** We mark all conflicting migrations as "already applied" so Django skips them:
- `products.0023_add_size_variant_fields`
- `products.0024_make_size_variant_fields_nullable`
- `products.0025_add_size_variant_fields_simple`
- `products.0026_merge_size_variant_migrations`
- `products.0027_add_size_variant_fields_safe`

### Problem 3: Constraint Issues

**Error:**
```
ValueError: Found wrong number (0) of constraints for accounts_cart(session_key, is_paid)
```

**Cause:** Django's `unique_together` doesn't work well when fields can be NULL. PostgreSQL treats each NULL as distinct, causing constraint validation to fail.

**Fix:** We replaced `unique_together` with **partial unique indexes**:
```sql
-- Only enforce uniqueness when user_id is NOT NULL
CREATE UNIQUE INDEX accounts_cart_user_is_paid_unique_idx 
ON accounts_cart (user_id, is_paid) 
WHERE user_id IS NOT NULL;

-- Only enforce uniqueness when session_key is NOT NULL
CREATE UNIQUE INDEX accounts_cart_session_is_paid_unique_idx 
ON accounts_cart (session_key, is_paid) 
WHERE session_key IS NOT NULL;
```

## 🎯 Using Railway CLI

### Method 1: Direct Script Execution (Easiest)

```bash
# Make sure you're in your project directory
cd a2z

# Run the fix script on Railway's database
railway run python fix_all_database_issues.py
```

### Method 2: Manual SQL Fix (If needed)

If the Python script doesn't work, you can run SQL directly:

```bash
# Connect to Railway database
railway run psql

# Then paste these commands:
```

```sql
-- Add coupon_id column
ALTER TABLE accounts_cart ADD COLUMN IF NOT EXISTS coupon_id UUID NULL;
ALTER TABLE accounts_cart 
ADD CONSTRAINT accounts_cart_coupon_id_fkey 
FOREIGN KEY (coupon_id) 
REFERENCES accounts_coupon(uid) 
ON DELETE SET NULL;

-- Drop old constraints
ALTER TABLE accounts_cart DROP CONSTRAINT IF EXISTS accounts_cart_user_id_is_paid_17a17a19_uniq;
ALTER TABLE accounts_cart DROP CONSTRAINT IF EXISTS accounts_cart_session_key_is_paid_f1b0e6e5_uniq;

-- Add partial unique indexes
DROP INDEX IF EXISTS accounts_cart_user_is_paid_unique_idx;
CREATE UNIQUE INDEX accounts_cart_user_is_paid_unique_idx 
ON accounts_cart (user_id, is_paid) 
WHERE user_id IS NOT NULL;

DROP INDEX IF EXISTS accounts_cart_session_is_paid_unique_idx;
CREATE UNIQUE INDEX accounts_cart_session_is_paid_unique_idx 
ON accounts_cart (session_key, is_paid) 
WHERE session_key IS NOT NULL;

-- Mark migrations as applied
INSERT INTO django_migrations (app, name, applied)
SELECT 'products', '0023_add_size_variant_fields', NOW()
WHERE NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='products' AND name='0023_add_size_variant_fields');

INSERT INTO django_migrations (app, name, applied)
SELECT 'products', '0024_make_size_variant_fields_nullable', NOW()
WHERE NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='products' AND name='0024_make_size_variant_fields_nullable');

INSERT INTO django_migrations (app, name, applied)
SELECT 'products', '0025_add_size_variant_fields_simple', NOW()
WHERE NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='products' AND name='0025_add_size_variant_fields_simple');

INSERT INTO django_migrations (app, name, applied)
SELECT 'products', '0026_merge_size_variant_migrations', NOW()
WHERE NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='products' AND name='0026_merge_size_variant_migrations');

INSERT INTO django_migrations (app, name, applied)
SELECT 'products', '0027_add_size_variant_fields_safe', NOW()
WHERE NOT EXISTS (SELECT 1 FROM django_migrations WHERE app='products' AND name='0027_add_size_variant_fields_safe');

-- Exit psql
\q
```

## 📊 Verification

After running the fix, verify everything works:

```bash
# Check if coupon_id exists
railway run psql -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='accounts_cart' AND column_name='coupon_id';"

# Check indexes
railway run psql -c "SELECT indexname FROM pg_indexes WHERE tablename='accounts_cart';"

# Check migrations
railway run psql -c "SELECT app, name FROM django_migrations WHERE app='products' AND name LIKE '%size_variant%';"
```

## 🚨 Troubleshooting

### If the script fails:

1. **Check Railway connection:**
   ```bash
   railway status
   ```

2. **Try running migrations manually:**
   ```bash
   railway run python manage.py migrate accounts 0031_comprehensive_fix
   ```

3. **Check database logs:**
   ```bash
   railway logs
   ```

### If you see "relation does not exist" errors:

This means tables haven't been created yet. Run:
```bash
railway run python manage.py migrate
```

Then run the fix script again.

## ✅ Final Checklist

- [ ] Run `railway run python fix_all_database_issues.py`
- [ ] Verify all checks pass (green checkmarks)
- [ ] Commit changes: `git add . && git commit -m "Fix database schema"`
- [ ] Push to Railway: `git push`
- [ ] Monitor deployment: `railway logs`
- [ ] Test the application

## 🎉 Success Indicators

You'll know it worked when:
- ✅ No more "coupon_id does not exist" errors
- ✅ No more "is_size_variant already exists" errors
- ✅ No more "wrong number of constraints" errors
- ✅ Your application starts successfully
- ✅ Cart functionality works (both authenticated and guest users)

## 📞 Still Having Issues?

If problems persist, check:
1. Railway service logs: `railway logs --tail`
2. Database connection: `railway run python manage.py dbshell`
3. Migration status: `railway run python manage.py showmigrations`

The fix script is idempotent - you can run it multiple times safely!

