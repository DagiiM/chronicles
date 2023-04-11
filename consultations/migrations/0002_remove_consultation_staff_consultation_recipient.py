# Generated by Django 4.1.7 on 2023-04-09 15:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('consultations', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consultation',
            name='staff',
        ),
        migrations.AddField(
            model_name='consultation',
            name='recipient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='received_consultations', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]