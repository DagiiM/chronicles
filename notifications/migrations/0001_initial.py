# Generated by Django 4.1.7 on 2023-03-30 15:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'), ('success', 'Success'), ('update', 'Update')], max_length=20)),
                ('notification_preference', models.JSONField(default=list)),
                ('body', models.TextField()),
                ('subject', models.CharField(max_length=255)),
                ('sender', models.CharField(max_length=255)),
                ('importance_level', models.IntegerField()),
                ('related_object', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_sent', models.DateTimeField(blank=True, null=True)),
                ('date_read', models.DateTimeField(blank=True, null=True)),
                ('expiration_date', models.DateTimeField(blank=True, null=True)),
                ('recipients', models.ManyToManyField(related_name='notifications_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'notifications',
            },
        ),
    ]