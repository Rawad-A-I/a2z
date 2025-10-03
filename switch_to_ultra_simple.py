#!/usr/bin/env python
"""
Script to switch to ultra-simple Python server
No Django, no dependencies, just pure Python HTTP server
"""
import shutil
import os

def switch_to_ultra_simple():
    """Switch to ultra-simple Python server"""
    print("🔄 Switching to ultra-simple Python server...")
    
    # Backup current files
    if os.path.exists('Procfile'):
        shutil.copy('Procfile', 'Procfile_minimal_backup')
    if os.path.exists('requirements.txt'):
        shutil.copy('requirements.txt', 'requirements_minimal_backup')
    
    # Replace with ultra-simple versions
    shutil.copy('ultra_simple_procfile.txt', 'Procfile')
    shutil.copy('ultra_simple_requirements.txt', 'requirements.txt')
    
    print("✅ Switched to ultra-simple Python server!")
    print("📁 Files backed up with _minimal_backup suffix")
    print("🚀 Ready to deploy ultra-simple server to Railway")

if __name__ == '__main__':
    switch_to_ultra_simple()
