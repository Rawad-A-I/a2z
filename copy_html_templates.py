#!/usr/bin/env python3
"""
A2Z Mart Frontend Collector Script
Copies all frontend files (HTML, CSS, JS, images, etc.) from the Django project into a single text file.
"""

import os
import glob
from pathlib import Path
import mimetypes

def collect_frontend_files():
    """Collect all frontend files and write them to a single text file."""
    
    # Get the current directory (project root)
    project_root = Path.cwd()
    
    # Define frontend directories to scan
    frontend_dirs = [
        "templates",      # HTML templates
        "static",         # Static files (CSS, JS, images)
        "mediafiles",     # Media files
        "public",         # Public files
    ]
    
    # Define file extensions to include
    frontend_extensions = {
        'html': ['.html', '.htm'],
        'css': ['.css'],
        'javascript': ['.js', '.jsx', '.ts', '.tsx'],
        'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp'],
        'fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
        'other': ['.json', '.xml', '.txt', '.md', '.yml', '.yaml', '.toml']
    }
    
    # Output file
    output_file = "A2Z_MART_FRONTEND_COMPLETE.txt"
    
    print(f"📁 Scanning frontend directories in: {project_root}")
    
    # Collect all frontend files
    all_files = []
    total_size = 0
    
    for dir_name in frontend_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"📂 Scanning {dir_name}/ directory...")
            
            # Find all files in this directory
            for ext_list in frontend_extensions.values():
                for ext in ext_list:
                    files = list(dir_path.rglob(f"*{ext}"))
                    for file in files:
                        all_files.append((file, dir_name))
                        total_size += file.stat().st_size
        else:
            print(f"⚠️  Directory not found: {dir_name}")
    
    if not all_files:
        print("❌ No frontend files found")
        return False
    
    print(f"📄 Found {len(all_files)} frontend files")
    print(f"📏 Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    
    # Sort files for consistent output
    all_files.sort(key=lambda x: (x[1], x[0]))
    
    # Write to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Write header
            outfile.write("# A2Z MART - COMPLETE FRONTEND COLLECTION\n")
            outfile.write("# Complete collection of all frontend files\n")
            outfile.write(f"# Generated on: {os.popen('date').read().strip()}\n")
            outfile.write(f"# Total Files: {len(all_files)} frontend files\n")
            outfile.write(f"# Total Size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)\n\n")
            outfile.write("=" * 80 + "\n\n")
            
            # Group files by type
            files_by_type = {}
            for file_path, dir_name in all_files:
                file_ext = file_path.suffix.lower()
                file_type = "other"
                
                for type_name, extensions in frontend_extensions.items():
                    if file_ext in extensions:
                        file_type = type_name
                        break
                
                if file_type not in files_by_type:
                    files_by_type[file_type] = []
                files_by_type[file_type].append((file_path, dir_name))
            
            # Process files by type
            for file_type, files in files_by_type.items():
                outfile.write(f"# {file_type.upper()} FILES ({len(files)} files)\n")
                outfile.write("=" * 80 + "\n\n")
                
                for i, (file_path, dir_name) in enumerate(files, 1):
                    # Get relative path from project root
                    try:
                        relative_path = file_path.relative_to(project_root)
                    except ValueError:
                        relative_path = file_path
                    
                    print(f"📝 Processing ({i}/{len(files)}) [{file_type}]: {relative_path}")
                    
                    # Write file header
                    outfile.write(f"## {relative_path}\n")
                    outfile.write(f"# File: {file_path}\n")
                    outfile.write(f"# Directory: {dir_name}\n")
                    outfile.write(f"# Type: {file_type}\n")
                    outfile.write(f"# Size: {file_path.stat().st_size} bytes\n")
                    
                    # Get MIME type
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    if mime_type:
                        outfile.write(f"# MIME Type: {mime_type}\n")
                    
                    outfile.write("-" * 80 + "\n")
                    
                    try:
                        # Determine if file is text or binary
                        is_text = file_type in ['html', 'css', 'javascript', 'other']
                        
                        if is_text:
                            # Read as text
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                outfile.write(content)
                        else:
                            # For binary files, write a placeholder
                            outfile.write(f"# BINARY FILE - {file_path.stat().st_size} bytes\n")
                            outfile.write("# Content not displayed (binary file)\n")
                            outfile.write(f"# To view this file, open: {file_path}\n")
                        
                        outfile.write("\n\n")
                        
                    except Exception as e:
                        error_msg = f"# ERROR reading file: {e}\n"
                        outfile.write(error_msg)
                        print(f"⚠️  Error reading {relative_path}: {e}")
                    
                    # Add separator between files
                    outfile.write("=" * 80 + "\n\n")
                
                outfile.write("\n")
        
        print(f"✅ Successfully created {output_file}")
        print(f"📊 Total files processed: {len(all_files)}")
        
        # Show file size
        output_size = os.path.getsize(output_file)
        print(f"📏 Output file size: {output_size:,} bytes ({output_size/1024/1024:.2f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing output file: {e}")
        return False

def main():
    """Main function to run the frontend collector."""
    print("🚀 A2Z Mart Frontend Collector")
    print("=" * 50)
    
    success = collect_frontend_files()
    
    if success:
        print("\n🎉 Frontend collection completed successfully!")
        print("📄 Check 'A2Z_MART_FRONTEND_COMPLETE.txt' for the complete collection.")
    else:
        print("\n❌ Frontend collection failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
