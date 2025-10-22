# Fix Missing coupon_id Column Issue

## Problem Summary

Your deployment is failing with the error:
```
django.db.utils.ProgrammingError: column accounts_cart.coupon_id does not exist
```

This happens because:
1. Your Cart model has a ForeignKey to Coupon
2. Django automatically creates a `coupon_id` column for ForeignKey fields
3. The column is missing from your database table
4. Migration conflicts prevent proper schema updates

## Solution Implemented

### 1. Created Migration File
- **File**: `accounts/migrations/0030_fix_coupon_column.py`
- **Purpose**: Safely adds the missing `coupon_id` column
- **Features**: 
  - Checks if column exists before adding (safe for re-runs)
  - Marks problematic migrations as applied to prevent conflicts
  - Uses PostgreSQL-specific SQL for reliability

### 2. Updated Model Reference
- **File**: `accounts/models.py` line 143
- **Change**: Updated `coupon = models.ForeignKey(Coupon, ...)` to `coupon = models.ForeignKey('accounts.Coupon', ...)`
- **Purpose**: Makes the reference explicit and prevents import issues

### 3. Created Test Script
- **File**: `test_coupon_fix.py`
- **Purpose**: Verifies the fix works correctly

## How to Deploy the Fix

### Option 1: Automatic Deployment
The migration will be applied automatically during your next deployment.

### Option 2: Manual Application
If you want to test locally first:

```bash
# Apply the migration
python manage.py migrate accounts 0030_fix_coupon_column

# Test the fix
python test_coupon_fix.py
```

### Option 3: Direct Database Fix (Emergency)
If migrations continue to fail, you can run this SQL directly:

```sql
ALTER TABLE accounts_cart ADD COLUMN IF NOT EXISTS coupon_id UUID NULL;
```

## Expected Results

After the fix:
- ✅ `accounts_cart` table will have the `coupon_id` column
- ✅ No more "column does not exist" errors
- ✅ Profile pages will load without errors
- ✅ Cart functionality will work properly
- ✅ Deployment will succeed

## Verification

To verify the fix worked:

1. **Check the column exists**:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name='accounts_cart' AND column_name='coupon_id';
   ```

2. **Test your application**:
   - Login to your application
   - Navigate to profile pages
   - Check that no database errors occur

3. **Run the test script**:
   ```bash
   python test_coupon_fix.py
   ```

## Troubleshooting

### If the migration still fails:
1. Check that the migration file exists: `accounts/migrations/0030_fix_coupon_column.py`
2. Verify the migration dependencies are correct
3. Try running migrations manually: `python manage.py migrate accounts`

### If the column still doesn't exist:
1. Run the direct SQL fix: `ALTER TABLE accounts_cart ADD COLUMN coupon_id UUID NULL;`
2. Check database permissions
3. Verify you're connected to the correct database

### If you get import errors:
1. Make sure the Coupon model is properly defined in `accounts/models.py`
2. Check that the model reference is correct: `'accounts.Coupon'`

## Files Modified

1. **`accounts/migrations/0030_fix_coupon_column.py`** - New migration file
2. **`accounts/models.py`** - Updated Cart model reference
3. **`test_coupon_fix.py`** - Test script for verification
4. **`COUPON_ID_FIX_GUIDE.md`** - This guide

## Next Steps

1. **Deploy the changes** to your production environment
2. **Monitor the deployment logs** for any remaining errors
3. **Test the application** to ensure everything works
4. **Remove temporary files** if desired (test_coupon_fix.py, etc.)

---

**🎉 This fix should resolve your deployment issues and get your application working properly!**
