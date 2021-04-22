# Generated by Django 3.2 on 2021-04-22 14:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '0007_auto_20210422_1118'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExecutionSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta', models.CharField(blank=True, max_length=100, null=True)),
                ('account_number', models.CharField(blank=True, max_length=100, null=True)),
                ('account_password', models.CharField(blank=True, max_length=100, null=True)),
                ('public_key', models.CharField(blank=True, max_length=150, null=True)),
                ('private_key', models.CharField(blank=True, max_length=150, null=True)),
                ('execution_port', models.IntegerField(blank=True, null=True)),
                ('account_port', models.IntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='execution_sessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
