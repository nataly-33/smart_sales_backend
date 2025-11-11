# Generated migration for LoginAudit model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAudit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de eliminación')),
                ('ip_address', models.GenericIPAddressField(verbose_name='Dirección IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('success', models.BooleanField(default=True, verbose_name='Login exitoso')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='login_audits', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Auditoría de Login',
                'verbose_name_plural': 'Auditorías de Login',
                'db_table': 'login_audit',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', '-created_at'], name='login_audit_user_created_idx'),
                    models.Index(fields=['-created_at'], name='login_audit_created_idx'),
                ],
            },
        ),
    ]
