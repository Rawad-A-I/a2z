# Generated merge migration to resolve conflicts

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_cart_unique_constraint_final'),
        ('accounts', '0028_businessformsubmission'),
    ]

    operations = [
        # This is a merge migration - no operations needed
        # Django will handle the merge automatically
    ]


