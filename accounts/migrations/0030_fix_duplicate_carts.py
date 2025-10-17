# Data migration to fix duplicate cart constraint issue

from django.db import migrations


def fix_duplicate_carts(apps, schema_editor):
    """Remove duplicate carts before applying unique constraint"""
    Cart = apps.get_model('accounts', 'Cart')
    
    # Find and remove duplicate carts
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


def reverse_fix_duplicate_carts(apps, schema_editor):
    """Reverse operation - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_merge_migration'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_carts, reverse_fix_duplicate_carts),
    ]

