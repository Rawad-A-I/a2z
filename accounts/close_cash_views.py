"""
Close Cash Excel Management Views
"""
import os
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
import mimetypes


def is_employee(user):
    """Check if user is an employee (staff member)."""
    return user.is_staff


def get_close_cash_directory():
    """Get the Close Cash directory path."""
    return os.path.join(settings.BASE_DIR, 'Close Cash')


def validate_filename(filename):
    """Validate filename to prevent path traversal attacks."""
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        return False
    return filename.endswith('.xlsx') and len(filename) <= 50


def get_user_excel_files(user):
    """Get Excel files available to the user based on their role."""
    close_cash_dir = get_close_cash_directory()
    
    if not os.path.exists(close_cash_dir):
        return []
    
    files = []
    for filename in os.listdir(close_cash_dir):
        if filename.endswith('.xlsx') and validate_filename(filename):
            # Admin can see all files
            if user.is_superuser:
                files.append({
                    'filename': filename,
                    'display_name': filename.replace('.xlsx', ''),
                    'is_master': filename == 'A to Z Format.xlsx',
                    'path': os.path.join(close_cash_dir, filename)
                })
            # Employee can only see their own file
            elif filename.lower() == f"{user.username}.xlsx":
                files.append({
                    'filename': filename,
                    'display_name': filename.replace('.xlsx', ''),
                    'is_master': False,
                    'path': os.path.join(close_cash_dir, filename)
                })
    
    return files


@login_required
def close_cash_dashboard(request):
    """Main dashboard showing available Excel files based on user role."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    files = get_user_excel_files(request.user)
    
    context = {
        'files': files,
        'is_admin': request.user.is_superuser,
        'user': request.user,
    }
    
    return render(request, 'accounts/close_cash_dashboard.html', context)


@login_required
def view_excel_file(request, filename):
    """Display Excel file as editable HTML table."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    if not validate_filename(filename):
        messages.error(request, 'Invalid filename.')
        return redirect('close_cash_dashboard')
    
    # Check if user has access to this file
    user_files = get_user_excel_files(request.user)
    file_info = None
    for f in user_files:
        if f['filename'] == filename:
            file_info = f
            break
    
    if not file_info:
        messages.error(request, 'You do not have access to this file.')
        return redirect('close_cash_dashboard')
    
    file_path = file_info['path']
    
    if not os.path.exists(file_path):
        messages.error(request, 'File not found.')
        return redirect('close_cash_dashboard')
    
    try:
        # Load Excel file
        workbook = load_workbook(file_path, data_only=False)
        worksheet = workbook.active
        
        # Convert to JSON structure
        excel_data = []
        max_row = worksheet.max_row or 1
        max_col = worksheet.max_column or 1
        
        for row in range(1, max_row + 1):
            row_data = []
            for col in range(1, max_col + 1):
                cell = worksheet.cell(row=row, column=col)
                cell_data = {
                    'value': cell.value if cell.value is not None else '',
                    'formula': cell.value if str(cell.value).startswith('=') else None,
                    'row': row,
                    'col': col,
                    'coordinate': cell.coordinate,
                    'data_type': str(cell.data_type),
                }
                row_data.append(cell_data)
            excel_data.append(row_data)
        
        # Get file stats
        file_stats = os.stat(file_path)
        last_modified = timezone.datetime.fromtimestamp(file_stats.st_mtime)
        
        context = {
            'filename': filename,
            'display_name': file_info['display_name'],
            'is_master': file_info['is_master'],
            'excel_data': excel_data,
            'max_row': max_row,
            'max_col': max_col,
            'last_modified': last_modified,
            'file_size': file_stats.st_size,
        }
        
        return render(request, 'accounts/close_cash_editor.html', context)
        
    except Exception as e:
        messages.error(request, f'Error reading Excel file: {str(e)}')
        return redirect('close_cash_dashboard')


@login_required
@require_http_methods(["POST"])
def save_excel_changes(request, filename):
    """Save edited data back to Excel file."""
    if not is_employee(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if not validate_filename(filename):
        return JsonResponse({'error': 'Invalid filename'}, status=400)
    
    # Check if user has access to this file
    user_files = get_user_excel_files(request.user)
    file_info = None
    for f in user_files:
        if f['filename'] == filename:
            file_info = f
            break
    
    if not file_info:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        changes = data.get('changes', [])
        
        if not changes:
            return JsonResponse({'success': True, 'message': 'No changes to save'})
        
        # Load Excel file with optimized settings
        file_path = file_info['path']
        workbook = load_workbook(file_path, data_only=False)  # Preserve formulas
        worksheet = workbook.active
        
        # Apply changes efficiently
        for change in changes:
            row = change.get('row')
            col = change.get('col')
            value = change.get('value')
            
            if row and col and value is not None:
                cell = worksheet.cell(row=row, column=col)
                
                # Smart value conversion
                if value == '':
                    cell.value = None  # Empty cell
                elif isinstance(value, str):
                    # Check if it's a number
                    try:
                        if value.replace('.', '').replace('-', '').replace('+', '').isdigit():
                            cell.value = float(value)
                        else:
                            cell.value = value
                    except:
                        cell.value = value
                else:
                    cell.value = value
        
        # Save with optimized settings
        workbook.save(file_path)
        
        return JsonResponse({
            'success': True, 
            'message': f'Saved {len(changes)} changes to {filename}',
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error saving file: {str(e)}'}, status=500)


@login_required
def download_excel_file(request, filename):
    """Download Excel file."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')
    
    if not validate_filename(filename):
        messages.error(request, 'Invalid filename.')
        return redirect('close_cash_dashboard')
    
    # Check if user has access to this file
    user_files = get_user_excel_files(request.user)
    file_info = None
    for f in user_files:
        if f['filename'] == filename:
            file_info = f
            break
    
    if not file_info:
        messages.error(request, 'You do not have access to this file.')
        return redirect('close_cash_dashboard')
    
    file_path = file_info['path']
    
    if not os.path.exists(file_path):
        messages.error(request, 'File not found.')
        return redirect('close_cash_dashboard')
    
    try:
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('close_cash_dashboard')


@login_required
@require_http_methods(["POST"])
def upload_excel_file(request, filename):
    """Upload modified Excel file."""
    if not is_employee(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if not validate_filename(filename):
        return JsonResponse({'error': 'Invalid filename'}, status=400)
    
    # Check if user has access to this file
    user_files = get_user_excel_files(request.user)
    file_info = None
    for f in user_files:
        if f['filename'] == filename:
            file_info = f
            break
    
    if not file_info:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Validate file type
        if not uploaded_file.name.endswith('.xlsx'):
            return JsonResponse({'error': 'Only .xlsx files are allowed'}, status=400)
        
        # Save uploaded file
        file_path = file_info['path']
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully uploaded {filename}',
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Error uploading file: {str(e)}'}, status=500)
