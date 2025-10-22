#!/usr/bin/env python
"""
Quick fix runner for the coupon_id column issue.
"""
import subprocess
import sys
import os

def run_fix():
    """Run the coupon_id fix."""
    print("🚨 RUNNING COUPON_ID FIX...")
    
    try:
        # Run the fix script
        result = subprocess.run([sys.executable, "fix_coupon_id.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Fix completed successfully!")
            return True
        else:
            print("❌ Fix failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running fix: {e}")
        return False

if __name__ == "__main__":
    success = run_fix()
    sys.exit(0 if success else 1)
