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
from django.views.decorators.http import require_POST
from django.db import transaction

from .models import CloseCashSchema, CloseCashEntry, A2ZSnapshot
from .close_cash_excel import (
    get_close_cash_directory,
    build_workbook_schema_and_data,
    write_values_to_workbook,
)


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

    # Show Rawad entrypoint for Rawad/admin, blank for others
    context = {}
    if is_rawad_or_admin(request.user):
        context['show_rawad_entry'] = True
    
    return render(request, 'accounts/close_cash_dashboard.html', context)


@login_required
def view_excel_file(request, filename):
    """Display Excel file as editable HTML table."""
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')

    # Restrict legacy grid editor entirely by redirecting to blank page
    messages.info(request, 'Close Cash editor is currently unavailable.')
    return redirect('close_cash_dashboard')
    
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
        # Load workbook with data_only=True to get calculated values
        workbook_data = load_workbook(file_path, data_only=True)  # For values
        workbook_formulas = load_workbook(file_path, data_only=False)  # For formulas
        
        # Get all sheet names
        sheet_names = workbook_data.sheetnames
        
        # Load data for all sheets
        all_sheets_data = {}
        for sheet_name in sheet_names:
            ws_data = workbook_data[sheet_name]
            ws_formulas = workbook_formulas[sheet_name]
            
            sheet_data = []
            max_row = ws_data.max_row or 1
            max_col = ws_data.max_column or 1
            
            for row in range(1, max_row + 1):
                row_data = []
                for col in range(1, max_col + 1):
                    cell_data = ws_data.cell(row=row, column=col)
                    cell_formula = ws_formulas.cell(row=row, column=col)
                    
                    # Show calculated value, but track if it's a formula
                    value = cell_data.value if cell_data.value is not None else ''
                    has_formula = str(cell_formula.value).startswith('=') if cell_formula.value else False
                    
                    row_data.append({
                        'value': value,
                        'hasFormula': has_formula
                    })
                sheet_data.append(row_data)
            
            # Ensure data has valid structure - add empty row if sheet is completely empty
            if not sheet_data or len(sheet_data) == 0:
                # Add at least one empty row if sheet is completely empty
                sheet_data = [[{'value': '', 'hasFormula': False}] * 10]
            
            all_sheets_data[sheet_name] = sheet_data
        
        # Get file stats
        file_stats = os.stat(file_path)
        last_modified = timezone.datetime.fromtimestamp(file_stats.st_mtime)
        
        context = {
            'filename': filename,
            'display_name': file_info['display_name'],
            'is_master': file_info['is_master'],
            'all_sheets_data': json.dumps(all_sheets_data),
            'sheet_names': json.dumps(sheet_names),  # ADD JSON SERIALIZATION
            'active_sheet': sheet_names[0],
            'last_modified': last_modified,
            'file_size': file_stats.st_size,
        }
        
        return render(request, 'accounts/close_cash_editor.html', context)
        
    except Exception as e:
        messages.error(request, f'Error reading Excel file: {str(e)}')
        return redirect('close_cash_dashboard')


# =====================
# DB-backed Forms (New)
# =====================

@login_required
def close_cash_form_dashboard(request):
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')

    # Determine employee workbook name by username.xlsx
    employee_filename = f"{request.user.username}.xlsx".lower()
    schemas = CloseCashSchema.objects.filter(workbook__iexact=employee_filename).order_by('sheet_name')
    entries = CloseCashEntry.objects.filter(user=request.user, workbook__iexact=employee_filename)
    latest_by_sheet = {e.sheet_name: e for e in entries}

    context = {
        'schemas': schemas,
        'latest_by_sheet': latest_by_sheet,
        'employee_filename': employee_filename,
    }
    return render(request, 'accounts/close_cash_form_dashboard.html', context)


@login_required
def edit_close_cash_form(request, sheet_name):
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')

    employee_filename = f"{request.user.username}.xlsx".lower()
    try:
        schema_obj = CloseCashSchema.objects.get(workbook__iexact=employee_filename, sheet_name=sheet_name, version='v1')
    except CloseCashSchema.DoesNotExist:
        messages.error(request, 'Form schema not found for this sheet.')
        return redirect('close_cash_forms_dashboard')

    # Load latest entry for prefill
    entry = CloseCashEntry.objects.filter(
        user=request.user,
        workbook__iexact=employee_filename,
        sheet_name=sheet_name,
        source_version='v1'
    ).order_by('-created_at').first()

    context = {
        'sheet_name': sheet_name,
        'schema': schema_obj.schema_json,
        'values': entry.data_json if entry else {},
    }
    return render(request, 'accounts/close_cash_form_edit.html', context)


@login_required
@require_POST
@transaction.atomic
def submit_close_cash_form(request, sheet_name):
    if not is_employee(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    data = payload.get('data', {})
    entry_date = payload.get('entry_date')  # ISO date string optional
    employee_filename = f"{request.user.username}.xlsx".lower()

    try:
        schema_obj = CloseCashSchema.objects.get(workbook__iexact=employee_filename, sheet_name=sheet_name, version='v1')
    except CloseCashSchema.DoesNotExist:
        return JsonResponse({'error': 'Form schema not found'}, status=404)

    # Convert entry_date
    from django.utils import timezone
    if entry_date:
        try:
            from datetime import date
            entry_date_obj = timezone.datetime.fromisoformat(entry_date).date()
        except Exception:
            return JsonResponse({'error': 'Invalid entry_date'}, status=400)
    else:
        entry_date_obj = timezone.now().date()

    # Persist DB entry
    entry = CloseCashEntry.objects.create(
        user=request.user,
        workbook=employee_filename,
        sheet_name=sheet_name,
        entry_date=entry_date_obj,
        data_json=data,
        source_version='v1',
    )

    # Sync back to employee workbook
    try:
        employee_workbook_path = os.path.join(get_close_cash_directory(), employee_filename)
        write_values_to_workbook(employee_workbook_path, sheet_name, schema_obj.schema_json, data)
    except Exception as e:
        # Do not rollback DB write; report sync failure
        return JsonResponse({'success': True, 'warning': f'Data saved but Excel sync failed: {str(e)}'})

    return JsonResponse({'success': True, 'message': 'Form saved successfully'})


# =====================
# A to Z Master Editor
# =====================

@login_required
def a2z_master_editor(request):
    if not is_employee(request.user):
        messages.error(request, 'You do not have employee access.')
        return redirect('index')

    master_filename = 'A to Z Format.xlsx'
    master_path = os.path.join(get_close_cash_directory(), master_filename)
    if not os.path.exists(master_path):
        if request.method == 'POST':
            return JsonResponse({'error': 'Master A to Z workbook not found.'}, status=404)
        else:
            messages.error(request, 'Master A to Z workbook not found.')
            return redirect('close_cash_dashboard')

    if request.method == 'POST':
        # Save edits back to master workbook
        try:
            payload = json.loads(request.body.decode('utf-8'))
            sheet_name = payload.get('sheet_name')
            data = payload.get('data') or {}
            if not sheet_name:
                return JsonResponse({'error': 'sheet_name is required'}, status=400)

            # Rebuild schema for the target sheet, then write values
            mapping = build_workbook_schema_and_data(master_path)
            sheet_payload = mapping.get(sheet_name)
            if not sheet_payload or 'schema' not in sheet_payload:
                return JsonResponse({'error': 'Schema not found for sheet'}, status=404)

            schema = sheet_payload['schema']
            write_values_to_workbook(master_path, sheet_name, schema, data)

            # Optional: snapshot full workbook after save
            try:
                updated_mapping = build_workbook_schema_and_data(master_path)
                A2ZSnapshot.objects.create(data_json=updated_mapping, note=f"Edited by {request.user.username}")
            except Exception:
                # Snapshot failure should not block save
                pass

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': f'Failed to save: {str(e)}'}, status=500)

    # GET: render editor
    try:
        mapping = build_workbook_schema_and_data(master_path)
        return render(request, 'accounts/close_cash_a2z_editor.html', {
            'master_filename': master_filename,
            'mapping_json': json.dumps(mapping),
        })
    except Exception as e:
        messages.error(request, f'Error reading A to Z workbook: {str(e)}')
        return redirect('close_cash_dashboard')


# =====================
# Rawad-only Forms
# =====================

def is_rawad_or_admin(user):
    """Check if user is Rawad (case-insensitive) or admin."""
    return user.is_superuser or user.username.lower() == 'rawad'


@login_required
def rawad_forms_dashboard(request):
    """Rawad-only forms dashboard showing available submissions."""
    if not is_rawad_or_admin(request.user):
        messages.error(request, 'You do not have access to this page.')
        return redirect('index')
    
    # Get existing entries from DB
    entries = CloseCashEntry.objects.filter(
        user=request.user, 
        workbook__iexact='Rawad.xlsx'
    ).order_by('-entry_date')
    
    # Group by entry date for display
    submissions_by_date = {}
    for entry in entries:
        date_key = entry.entry_date.strftime('%Y-%m-%d')
        if date_key not in submissions_by_date:
            submissions_by_date[date_key] = entry
    
    context = {
        'submissions': list(submissions_by_date.values()),
        'workbook_name': 'Rawad.xlsx',
        'is_admin': request.user.is_superuser,
    }
    return render(request, 'accounts/close_cash_rawad_dashboard.html', context)


@login_required
def rawad_edit_close_cash_form(request, sheet_name):
    """Edit Rawad form for specific date sheet."""
    if not is_rawad_or_admin(request.user):
        messages.error(request, 'You do not have access to this page.')
        return redirect('index')
    
    # Import hardcoded schema
    from .rawad_form_schema import RAWAD_FORM_SCHEMA
    
    # Handle "new" sheet name for creating new submissions
    if sheet_name == 'new':
        sheet_name = 'new_submission'
        form_values = {}
    else:
        # Load existing entry from DB for prefill (if exists)
        entry = CloseCashEntry.objects.filter(
            user=request.user,
            workbook__iexact='Rawad.xlsx',
            sheet_name=sheet_name,
            source_version='v1'
        ).order_by('-created_at').first()
        
        # Use DB values if available, otherwise empty
        form_values = entry.data_json if entry else {}
    
    context = {
        'sheet_name': sheet_name,
        'schema': RAWAD_FORM_SCHEMA,
        'values': form_values,
        'workbook_name': 'Rawad.xlsx',
    }
    return render(request, 'accounts/close_cash_rawad_form.html', context)


@login_required
@require_POST
@transaction.atomic
def rawad_submit_close_cash_form(request, sheet_name):
    """Submit Rawad form data."""
    if not is_rawad_or_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    
    data = payload.get('data', {})
    entry_date = payload.get('entry_date')
    
    # Convert entry_date
    from django.utils import timezone
    if entry_date:
        try:
            from datetime import date
            entry_date_obj = timezone.datetime.fromisoformat(entry_date).date()
        except Exception:
            return JsonResponse({'error': 'Invalid entry_date'}, status=400)
    else:
        entry_date_obj = timezone.now().date()
    
    # Persist DB entry
    entry = CloseCashEntry.objects.create(
        user=request.user,
        workbook='Rawad.xlsx',
        sheet_name=sheet_name,
        entry_date=entry_date_obj,
        data_json=data,
        source_version='v1',
    )
    
    return JsonResponse({'success': True, 'message': 'Form saved successfully'})


@login_required
def rawad_export_excel(request):
    """Admin-only export of Rawad submissions as Excel file."""
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can export Excel files.')
        return redirect('index')
    
    try:
        from openpyxl import Workbook
        from .rawad_form_schema import RAWAD_FORM_SCHEMA
        
        # Get all Rawad submissions from DB
        entries = CloseCashEntry.objects.filter(
            workbook__iexact='Rawad.xlsx'
        ).order_by('entry_date')
        
        if not entries.exists():
            messages.error(request, 'No submissions found to export.')
            return redirect('rawad_forms_dashboard')
        
        # Create new workbook
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        # For each submission, create a sheet
        for entry in entries:
            # Create sheet with date as name
            sheet_name = entry.entry_date.strftime('%d-%m-%Y')
            ws = wb.create_sheet(title=sheet_name)
            
            # Write section headers and field values in A/B columns
            row = 1
            for section in RAWAD_FORM_SCHEMA['sections']:
                # Section header
                ws.cell(row, 1, section['title'])
                row += 1
                
                # Section fields
                for field in section['fields']:
                    ws.cell(row, 1, field['label'])
                    value = entry.data_json.get(field['key'], '')
                    ws.cell(row, 2, value)
                    row += 1
                
                # Blank row between sections
                row += 1
        
        # Convert to bytes
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Return as download
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="Rawad_Close_Cash_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating Excel: {str(e)}')
        return redirect('rawad_forms_dashboard')


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
            sheet_name = change.get('sheet', workbook.sheetnames[0])
            
            if row and col and value is not None:
                # Get the specific worksheet
                worksheet = workbook[sheet_name]
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
