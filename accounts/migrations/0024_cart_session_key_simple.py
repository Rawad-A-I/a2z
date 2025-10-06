# Simple migration to add session_key field

from django.db import migrations, models


def cleanup_duplicate_carts_before_constraint(apps, schema_editor):
    """
    Clean up duplicate cart records before applying any constraints.
    """
    Cart = apps.get_model('accounts', 'Cart')
    
    try:
        from django.db.models import Count
        from django.db import transaction
        
        with transaction.atomic():
            # Handle duplicate carts for authenticated users
            duplicate_users = Cart.objects.filter(
                user__isnull=False,
                is_paid=False
            ).values('user').annotate(
                count=Count('id')
            ).filter(count__gt=1)
            
            for user_data in duplicate_users:
                user_id = user_data['user']
                user_carts = Cart.objects.filter(
                    user_id=user_id,
                    is_paid=False
                ).order_by('-created_at')
                
                if user_carts.count() > 1:
                    # Keep the newest cart, mark others as paid
                    carts_to_mark = user_carts[1:]
                    for cart in carts_to_mark:
                        cart.is_paid = True
                        cart.save()
                        
    except Exception as e:
        print(f"Warning: Could not clean up duplicate carts: {e}")


def reverse_cleanup(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_profile_phone_country_code'),
    ]

    operations = [
        # Clean up duplicates first
        migrations.RunPython(
            cleanup_duplicate_carts_before_constraint,
            reverse_cleanup,
        ),
        # Add the session_key field
        migrations.AddField(
            model_name='cart',
            name='session_key',
            field=models.CharField(blank=True, help_text='Session key for anonymous users', max_length=40, null=True),
        ),
    ]
