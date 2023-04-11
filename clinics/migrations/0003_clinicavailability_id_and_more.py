# Generated by Django 4.1.7 on 2023-04-02 18:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinics', '0002_appointmenttype_max_slots_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicavailability',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clinicavailability',
            name='appointment_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='caa', to='clinics.appointmenttype'),
        ),
    ]