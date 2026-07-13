# Generated manually for the users app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(blank=True, choices=[('', '-- no role --'), ('data_manager', 'Data Manager'), ('statistician', 'Statistician'), ('readonly', 'Read-only'), ('coordinator', 'Coordinator'), ('investigator', 'Investigator'), ('pathologist', 'Pathologist')], help_text="Determines permissions (seeded by seed_roles).", max_length=30)),
                ('department', models.CharField(blank=True, help_text="e.g. Dept. of Nephrology", max_length=80)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('is_clinician', models.BooleanField(default=False, help_text="Can write prescriptions and sign off on pathology reviews.")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user__last_name', 'user__first_name'],
            },
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('role', models.CharField(blank=True, choices=[('', '-- no role --'), ('data_manager', 'Data Manager'), ('statistician', 'Statistician'), ('readonly', 'Read-only'), ('coordinator', 'Coordinator'), ('investigator', 'Investigator'), ('pathologist', 'Pathologist')], max_length=30)),
                ('token', models.CharField(db_index=True, max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitations_sent', to=settings.AUTH_USER_MODEL)),
                ('used_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invitations_accepted', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
