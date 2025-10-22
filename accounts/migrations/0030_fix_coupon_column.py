from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Initial attempt to fix coupon_id column.
    Note: This is superseded by 0031_comprehensive_fix which handles
    all issues including constraints and product migrations.
    """

    dependencies = [
        ('accounts', '0029_merge_migration'),
    ]

    operations = [
        # Attempt to add coupon_id column (will be fully handled by 0031)
        migrations.RunSQL(
            sql="ALTER TABLE accounts_cart ADD COLUMN coupon_id INTEGER NULL;",
            reverse_sql=migrations.RunSQL.noop
        ),
    ]
