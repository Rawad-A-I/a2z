from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from django.conf import settings
from datetime import datetime

def business_form(request):
    """
    Display the business customization form
    """
    return render(request, 'business_form.html')

@csrf_exempt
@require_http_methods(["POST"])
def submit_business_form(request):
    """
    Handle business form submission and save data
    """
    try:
        # Get form data
        form_data = {}
        files_data = {}
        
        # Process regular form fields
        for key, value in request.POST.items():
            form_data[key] = value
        
        # Process uploaded files
        for key, file in request.FILES.items():
            files_data[key] = {
                'name': file.name,
                'size': file.size,
                'type': file.content_type,
                'data': file.read()  # Store file content as bytes
            }
        
        # Create response data
        response_data = {
            'form_data': form_data,
            'files_data': files_data,
            'submitted_at': datetime.now().isoformat(),
            'status': 'success'
        }
        
        # Save to JSON file
        save_business_data(response_data)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Business information submitted successfully!',
            'data_id': datetime.now().strftime('%Y%m%d_%H%M%S')
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error submitting form: {str(e)}'
        }, status=500)

def save_business_data(data):
    """
    Save business form data to JSON file
    """
    try:
        # Create data directory if it doesn't exist
        data_dir = os.path.join(settings.BASE_DIR, 'business_data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'business_form_{timestamp}.json'
        filepath = os.path.join(data_dir, filename)
        
        # Save data to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Also save images if any
        if 'files_data' in data and data['files_data']:
            for file_key, file_info in data['files_data'].items():
                image_filename = f'{file_key}_{timestamp}_{file_info["name"]}'
                image_path = os.path.join(data_dir, image_filename)
                
                with open(image_path, 'wb') as img_file:
                    img_file.write(file_info['data'])
        
        return filepath
        
    except Exception as e:
        print(f"Error saving business data: {e}")
        return None

def get_business_data(request):
    """
    Retrieve all business form submissions
    """
    try:
        data_dir = os.path.join(settings.BASE_DIR, 'business_data')
        
        if not os.path.exists(data_dir):
            return JsonResponse({'data': [], 'count': 0})
        
        # Get all JSON files
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        all_data = []
        
        for filename in json_files:
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.append({
                        'filename': filename,
                        'data': data,
                        'created_at': data.get('submitted_at', 'Unknown')
                    })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue
        
        # Sort by creation date (newest first)
        all_data.sort(key=lambda x: x['created_at'], reverse=True)
        
        return JsonResponse({
            'data': all_data,
            'count': len(all_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error retrieving data: {str(e)}'
        }, status=500)

def business_form_admin(request):
    """
    Display admin interface for viewing business form submissions
    """
    return render(request, 'business_form_admin.html')
