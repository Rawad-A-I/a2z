# Generated manually for cart session support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_alter_customerloyalty_tier'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='session_key',
            field=models.CharField(blank=True, help_text='Session key for anonymous users', max_length=40, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('user', 'is_paid'), ('session_key', 'is_paid')},
        ),
    ]
