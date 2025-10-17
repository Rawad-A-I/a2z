# Migration to add unique constraint after cleanup

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_cart_session_key_simple'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('user', 'is_paid'), ('session_key', 'is_paid')},
        ),
    ]
