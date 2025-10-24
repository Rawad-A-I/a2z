# Generated manually for Close Cash models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_create_userpreferences_only'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CloseCashSchema',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workbook', models.CharField(max_length=100)),
                ('sheet_name', models.CharField(max_length=100)),
                ('schema_json', models.JSONField(default=dict)),
                ('version', models.CharField(default='v1', max_length=20)),
            ],
            options={
                'unique_together': {('workbook', 'sheet_name', 'version')},
                'indexes': [
                    models.Index(fields=['workbook', 'sheet_name'], name='accounts_cl_workboo_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='CloseCashEntry',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workbook', models.CharField(max_length=100)),
                ('sheet_name', models.CharField(max_length=100)),
                ('entry_date', models.DateField()),
                ('data_json', models.JSONField(default=dict)),
                ('source_version', models.CharField(default='v1', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='close_cash_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'workbook', 'sheet_name', 'entry_date', 'source_version')},
                'indexes': [
                    models.Index(fields=['user', 'entry_date'], name='accounts_cl_user_id_idx'),
                    models.Index(fields=['workbook', 'sheet_name'], name='accounts_cl_workboo_2_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='A2ZSnapshot',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('snapshot_at', models.DateTimeField(auto_now_add=True)),
                ('data_json', models.JSONField(default=dict)),
                ('note', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'ordering': ['-snapshot_at'],
            },
        ),
    ]

