#!/usr/bin/env python3
"""
Railway Deployment Setup Script
Prepares your Django eCommerce project for Railway deployment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_git_repo():
    """Check if this is a git repository."""
    if not Path('.git').exists():
        print("📦 Initializing Git repository...")
        run_command("git init", "Initializing Git")
        return False
    return True

def setup_git():
    """Set up Git repository for Railway deployment."""
    print("🚀 Setting up Git repository for Railway deployment")
    print("=" * 50)
    
    # Check if git is installed
    if not run_command("git --version", "Checking Git installation"):
        print("❌ Git is not installed. Please install Git first:")
        print("Download from: https://git-scm.com/downloads")
        return False
    
    # Initialize git if needed
    if not check_git_repo():
        run_command("git init", "Initializing Git repository")
    
    # Add all files
    run_command("git add .", "Adding files to Git")
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        run_command('git commit -m "Initial commit for Railway deployment"', "Creating initial commit")
        print("✅ Git repository ready for Railway")
    else:
        print("✅ Git repository already up to date")
    
    print("\n🎉 Git setup completed!")
    print("\nNext steps:")
    print("1. Create GitHub repository:")
    print("   - Go to https://github.com/new")
    print("   - Create a new repository")
    print("   - Don't initialize with README (we already have files)")
    print()
    print("2. Connect to GitHub:")
    print("   git remote add origin https://github.com/yourusername/your-repo.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("3. Deploy to Railway:")
    print("   - Go to https://railway.app")
    print("   - Sign up with GitHub")
    print("   - Click 'New Project'")
    print("   - Select 'Deploy from GitHub repo'")
    print("   - Choose your repository")
    print("   - Add PostgreSQL database")
    print("   - Set environment variables")
    print()
    print("📖 See RAILWAY_DEPLOYMENT.md for detailed instructions")
    
    return True

def check_requirements():
    """Check if all required files are present."""
    required_files = [
        'railway.json',
        'railway.toml', 
        'Procfile',
        'requirements.txt',
        'runtime.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

if __name__ == "__main__":
    print("🚀 Railway Deployment Setup")
    print("=" * 30)
    
    # Check required files
    if not check_requirements():
        print("Please ensure all required files are present before running this script")
        sys.exit(1)
    
    # Setup Git
    setup_git()
