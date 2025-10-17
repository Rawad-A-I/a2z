# Generated manually for BusinessFormSubmission model

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_cart_unique_constraint'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessFormSubmission',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company_name', models.CharField(blank=True, max_length=200, null=True)),
                ('business_type', models.CharField(blank=True, max_length=100, null=True)),
                ('industry', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('primary_color', models.CharField(blank=True, help_text='Hex color code', max_length=7, null=True)),
                ('secondary_color', models.CharField(blank=True, help_text='Hex color code', max_length=7, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='business_logos/')),
                ('main_products', models.TextField(blank=True, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('website_url', models.URLField(blank=True, null=True)),
                ('business_description', models.TextField(blank=True, null=True)),
                ('target_audience', models.TextField(blank=True, null=True)),
                ('special_requirements', models.TextField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('in_progress', 'In Progress')], default='pending', max_length=20)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('processed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_business_forms', to='auth.user')),
            ],
            options={
                'verbose_name': 'Business Form Submission',
                'verbose_name_plural': 'Business Form Submissions',
                'ordering': ['-submitted_at'],
            },
        ),
    ]
