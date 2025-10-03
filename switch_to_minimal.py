#!/usr/bin/env python
"""
Script to switch to minimal Django app for Railway deployment
This will temporarily replace the main files with minimal versions
"""
import shutil
import os

def switch_to_minimal():
    """Switch to minimal Django app"""
    print("🔄 Switching to minimal Django app...")
    
    # Backup original files
    if os.path.exists('manage.py'):
        shutil.copy('manage.py', 'manage_original.py')
    if os.path.exists('requirements.txt'):
        shutil.copy('requirements.txt', 'requirements_original.txt')
    if os.path.exists('Procfile'):
        shutil.copy('Procfile', 'Procfile_original')
    
    # Replace with minimal versions
    shutil.copy('minimal_manage.py', 'manage.py')
    shutil.copy('minimal_requirements.txt', 'requirements.txt')
    shutil.copy('minimal_procfile.txt', 'Procfile')
    
    print("✅ Switched to minimal Django app!")
    print("📁 Original files backed up with _original suffix")
    print("🚀 Ready to deploy minimal app to Railway")

def switch_back_to_full():
    """Switch back to full Django app"""
    print("🔄 Switching back to full Django app...")
    
    # Restore original files
    if os.path.exists('manage_original.py'):
        shutil.copy('manage_original.py', 'manage.py')
    if os.path.exists('requirements_original.txt'):
        shutil.copy('requirements_original.txt', 'requirements.txt')
    if os.path.exists('Procfile_original'):
        shutil.copy('Procfile_original', 'Procfile')
    
    print("✅ Switched back to full Django app!")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--restore':
        switch_back_to_full()
    else:
        switch_to_minimal()

