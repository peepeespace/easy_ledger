# Generated by Django 3.2 on 2021-04-23 18:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('db', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='strategy_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='strategy_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.CreateModel(
            name='Cash',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy_name', models.CharField(blank=True, max_length=150, null=True)),
                ('quote', models.CharField(blank=True, max_length=50, null=True)),
                ('amount', models.FloatField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
