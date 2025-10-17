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
            # Find all duplicate combinations of (user_id, is_paid)
            seen_combinations = set()
            duplicates_to_remove = []
            
            for cart in Cart.objects.all():
                key = (cart.user_id, cart.is_paid)
                if key in seen_combinations:
                    duplicates_to_remove.append(cart.id)
                else:
                    seen_combinations.add(key)
            
            # Remove duplicates
            if duplicates_to_remove:
                Cart.objects.filter(id__in=duplicates_to_remove).delete()
                print(f"Removed {len(duplicates_to_remove)} duplicate carts")
            else:
                print("No duplicate carts found")
                        
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
