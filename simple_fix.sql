-- Simple fix: Add missing coupon_id column
-- This is the minimal fix needed to resolve the deployment issue

-- Add the missing coupon_id column to accounts_cart table
ALTER TABLE accounts_cart ADD COLUMN IF NOT EXISTS coupon_id UUID NULL;

-- If the above doesn't work, try this alternative:
-- ALTER TABLE accounts_cart ADD COLUMN coupon_id UUID NULL;
