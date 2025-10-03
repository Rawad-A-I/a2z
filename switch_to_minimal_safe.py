#!/usr/bin/env python
"""
Safely switch to minimal app without deleting Django project
"""
import shutil
import os

def switch_to_minimal_safe():
    """Switch to minimal app while preserving Django project"""
    print("🔄 Switching to minimal app (preserving Django project)...")
    
    # Backup current files
    if os.path.exists('Procfile'):
        shutil.copy('Procfile', 'Procfile_django_backup')
    if os.path.exists('requirements.txt'):
        shutil.copy('requirements.txt', 'requirements_django_backup')
    
    # Switch to minimal versions
    shutil.copy('minimal_procfile.txt', 'Procfile')
    shutil.copy('minimal_requirements.txt', 'requirements.txt')
    
    print("✅ Switched to minimal app!")
    print("📁 Django files preserved with _django_backup suffix")
    print("🚀 Ready to deploy minimal app to Railway")
    print("💡 Your Django project is safe and untouched!")

if __name__ == '__main__':
    switch_to_minimal_safe()
