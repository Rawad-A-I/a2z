from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
import json
import os
from django.conf import settings
from datetime import datetime
from .models import BusinessFormSubmission

def business_form(request):
    """
    Display the business customization form
    """
    return render(request, 'business_form.html')

@csrf_exempt
@require_http_methods(["POST"])
def submit_business_form(request):
    """
    Handle business form submission and save data to database
    """
    try:
        print(f"Business form submission received")
        print(f"POST data: {dict(request.POST)}")
        print(f"FILES data: {dict(request.FILES)}")
        
        # Get client IP and user agent
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create BusinessFormSubmission instance
        with transaction.atomic():
            submission = BusinessFormSubmission(
                # Basic Information
                company_name=request.POST.get('company_name', ''),
                business_type=request.POST.get('business_type', ''),
                industry=request.POST.get('industry', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                
                # Branding
                primary_color=request.POST.get('primary_color', ''),
                secondary_color=request.POST.get('secondary_color', ''),
                logo=request.FILES.get('logo') if 'logo' in request.FILES else None,
                
                # Business Details
                main_products=request.POST.get('main_products', ''),
                currency=request.POST.get('currency', ''),
                website_url=request.POST.get('website_url', ''),
                
                # Additional Information
                business_description=request.POST.get('business_description', ''),
                target_audience=request.POST.get('target_audience', ''),
                special_requirements=request.POST.get('special_requirements', ''),
                
                # Metadata
                ip_address=ip_address,
                user_agent=user_agent,
                status='pending'
            )
            
            submission.save()
            print(f"Successfully saved business form submission: {submission.uid}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Business information submitted successfully!',
            'data_id': str(submission.uid)
        })
        
    except Exception as e:
        print(f"Error in submit_business_form: {e}")
        import traceback
        traceback.print_exc()
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
        
        print(f"Saving business data to: {filepath}")
        print(f"Data keys: {list(data.keys())}")
        
        # Save data to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved business data to {filepath}")
        
        # Also save images if any
        if 'files_data' in data and data['files_data']:
            for file_key, file_info in data['files_data'].items():
                image_filename = f'{file_key}_{timestamp}_{file_info["name"]}'
                image_path = os.path.join(data_dir, image_filename)
                
                with open(image_path, 'wb') as img_file:
                    img_file.write(file_info['data'])
                print(f"Saved image: {image_path}")
        
        return filepath
        
    except Exception as e:
        print(f"Error saving business data: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_business_data(request):
    """
    Retrieve all business form submissions from database
    """
    try:
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Get all submissions from database
        submissions = BusinessFormSubmission.objects.all()
        
        # Paginate results
        paginator = Paginator(submissions, per_page)
        page_obj = paginator.get_page(page)
        
        # Convert to JSON format
        all_data = []
        for submission in page_obj:
            data = {
                'uid': str(submission.uid),
                'company_name': submission.company_name,
                'business_type': submission.business_type,
                'industry': submission.industry,
                'email': submission.email,
                'phone': submission.phone,
                'primary_color': submission.primary_color,
                'secondary_color': submission.secondary_color,
                'main_products': submission.main_products,
                'currency': submission.currency,
                'website_url': submission.website_url,
                'business_description': submission.business_description,
                'target_audience': submission.target_audience,
                'special_requirements': submission.special_requirements,
                'status': submission.status,
                'submitted_at': submission.submitted_at.isoformat(),
                'ip_address': submission.ip_address,
                'days_since_submission': submission.days_since_submission,
                'logo_url': submission.logo.url if submission.logo else None,
            }
            all_data.append(data)
        
        print(f"Returning {len(all_data)} business form submissions from database")
        return JsonResponse({
            'data': all_data,
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
        
    except Exception as e:
        print(f"Error in get_business_data: {e}")
        # Return empty data if table doesn't exist yet
        return JsonResponse({
            'data': [],
            'count': 0,
            'total_pages': 0,
            'current_page': 1,
            'has_next': False,
            'has_previous': False,
        })

@login_required
@user_passes_test(lambda u: u.is_staff)
def business_form_admin(request):
    """
    Display admin interface for viewing business form submissions
    """
    try:
        # Get basic stats
        total_submissions = BusinessFormSubmission.objects.count()
        pending_submissions = BusinessFormSubmission.objects.filter(status='pending').count()
        approved_submissions = BusinessFormSubmission.objects.filter(status='approved').count()
        
        context = {
            'total_submissions': total_submissions,
            'pending_submissions': pending_submissions,
            'approved_submissions': approved_submissions,
        }
    except Exception as e:
        # Handle case where table doesn't exist yet
        print(f"Error accessing BusinessFormSubmission table: {e}")
        context = {
            'total_submissions': 0,
            'pending_submissions': 0,
            'approved_submissions': 0,
        }
    
    return render(request, 'business_form_admin.html', context)
