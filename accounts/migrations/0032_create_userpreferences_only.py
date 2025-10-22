# Generated manually to create only UserPreferences table safely
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0031_comprehensive_fix'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('phone_verified', models.BooleanField(default=False)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('bio', models.TextField(blank=True, max_length=500, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say')], max_length=20, null=True)),
                ('email_notifications', models.BooleanField(default=True)),
                ('sms_notifications', models.BooleanField(default=False)),
                ('push_notifications', models.BooleanField(default=True)),
                ('order_updates', models.BooleanField(default=True)),
                ('promotional_emails', models.BooleanField(default=True)),
                ('newsletter', models.BooleanField(default=True)),
                ('product_recommendations', models.BooleanField(default=True)),
                ('security_alerts', models.BooleanField(default=True)),
                ('profile_visibility', models.CharField(choices=[('public', 'Public'), ('friends', 'Friends Only'), ('private', 'Private')], default='private', max_length=20)),
                ('show_online_status', models.BooleanField(default=True)),
                ('allow_friend_requests', models.BooleanField(default=True)),
                ('show_last_seen', models.BooleanField(default=True)),
                ('language', models.CharField(choices=[('en', 'English'), ('ar', 'Arabic'), ('fr', 'French'), ('es', 'Spanish')], default='en', max_length=5)),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('date_format', models.CharField(choices=[('MM/DD/YYYY', 'MM/DD/YYYY'), ('DD/MM/YYYY', 'DD/MM/YYYY'), ('YYYY-MM-DD', 'YYYY-MM-DD')], default='MM/DD/YYYY', max_length=10)),
                ('time_format', models.CharField(choices=[('12', '12 Hour'), ('24', '24 Hour')], default='12', max_length=2)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')], default='auto', max_length=10)),
                ('font_size', models.CharField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium', max_length=10)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='preferences', to='auth.user')),
            ],
            options={
                'verbose_name': 'User Preferences',
                'verbose_name_plural': 'User Preferences',
            },
        ),
    ]
