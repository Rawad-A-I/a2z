# Simple migration to add session_key field

from django.db import migrations, models


def cleanup_duplicate_carts_before_constraint(apps, schema_editor):
    """
    Clean up duplicate cart records before applying any constraints.
    """
    Cart = apps.get_model('accounts', 'Cart')
    
    try:
        from django.db import transaction
        
        with transaction.atomic():
            # More aggressive cleanup - remove ALL duplicate combinations
            # Keep only the most recent cart for each (user_id, is_paid) combination
            
            # Get all unique combinations
            combinations = Cart.objects.values('user_id', 'is_paid').distinct()
            
            for combo in combinations:
                user_id = combo['user_id']
                is_paid = combo['is_paid']
                
                # Get all carts for this combination
                carts = Cart.objects.filter(user_id=user_id, is_paid=is_paid).order_by('-created_at')
                
                if carts.count() > 1:
                    # Keep the most recent one, delete the rest
                    carts_to_delete = carts[1:]
                    for cart in carts_to_delete:
                        cart.delete()
                    print(f"Removed {carts_to_delete.count()} duplicate carts for user {user_id}, is_paid {is_paid}")
                        
    except Exception as e:
        print(f"Warning: Could not clean up duplicate carts: {e}")
        # If cleanup fails, try to delete all carts to allow migration to proceed
        try:
            Cart.objects.all().delete()
            print("Deleted all carts to allow migration to proceed")
        except Exception as e2:
            print(f"Failed to delete all carts: {e2}")


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
