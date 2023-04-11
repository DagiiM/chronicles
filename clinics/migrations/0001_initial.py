# Generated by Django 4.1.7 on 2023-04-02 16:14

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import django_google_maps.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('appointment_date', models.DateField(verbose_name=models.DateTimeField())),
                ('weight', models.IntegerField(default=1)),
                ('rating', models.FloatField(blank=True, default=None, null=True)),
                ('status', models.CharField(choices=[('confirmed', 'CONFIRMED'), ('canceled', 'CANCELED'), ('completed', 'COMPLETED'), ('rescheduled', 'RESCHEDULED')], default='confirmed', max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AppointmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_approved', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('created_by', 'approved_by')},
            },
        ),
        migrations.CreateModel(
            name='ClinicStaff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_clinic_approved', to=settings.AUTH_USER_MODEL)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clinics', to='clinics.clinic')),
            ],
        ),
        migrations.CreateModel(
            name='BasicInfo',
            fields=[
                ('clinic', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='clinics.clinic')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=2)),
                ('zip_code', models.CharField(max_length=10)),
                ('phone_number', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('website', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('clinic', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='clinics.clinic')),
                ('address', models.CharField(help_text='Address of the clinic.', max_length=255)),
                ('geolocation', django_google_maps.fields.GeoLocationField(help_text='Click on the map to select the location of the clinic.', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Management',
            fields=[
                ('clinic', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='clinics.clinic')),
                ('medical_director', models.CharField(max_length=255)),
                ('clinic_manager', models.CharField(max_length=255)),
                ('hours_of_operation', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('PENDING', 'Pending'), ('EXPIRED', 'Expired'), ('TERMINATED', 'Terminated')], default='Pending', max_length=20)),
                ('is_approved', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_approved', to=settings.AUTH_USER_MODEL)),
                ('clinic', models.ManyToManyField(through='clinics.ClinicStaff', to='clinics.clinic')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_created', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='staff', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('created_by', 'approved_by')},
            },
        ),
        migrations.CreateModel(
            name='Specialty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('appointment_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specialties', to='clinics.appointmenttype')),
            ],
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('description', models.TextField()),
                ('frequency', models.CharField(choices=[('hourly', 'Hourly'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('annually', 'Annually')], max_length=10)),
                ('agreement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salaries', to='clinics.agreement')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')], max_length=10)),
                ('address', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patient', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diagnosis', models.TextField()),
                ('treatment', models.TextField()),
                ('medication', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clinics.appointment')),
                ('clinic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clinic_medicalrecord', related_query_name='clinic_medicalrecord', to='clinics.clinic')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clinics.patient')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clinics.staff')),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('PENDING', 'Pending'), ('EXPIRED', 'Expired'), ('TERMINATED', 'Terminated')], default='Pending', max_length=20)),
                ('is_active', models.BooleanField(default=False)),
                ('agreement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='clinics.agreement')),
                ('salary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='clinics.salary')),
                ('specialty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='clinics.specialty')),
            ],
        ),
        migrations.AddField(
            model_name='clinicstaff',
            name='contract',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clinic_staff', to='clinics.contract'),
        ),
        migrations.AddField(
            model_name='clinicstaff',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_clinic_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='clinicstaff',
            name='permission_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clinic_staff', to='auth.group'),
        ),
        migrations.AddField(
            model_name='clinicstaff',
            name='staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clinic_staff', to='clinics.staff'),
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('appointment_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_type', to='clinics.appointmenttype')),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='appointment_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_appointment_type', to='clinics.appointmenttype'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='clinic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clinic', related_query_name='clinic_appointments', to='clinics.clinic'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', related_query_name='appointment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='appointment',
            name='staff',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', related_query_name='appointment', to='clinics.staff'),
        ),
        migrations.CreateModel(
            name='Leave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Sick leave', 'Sick leave'), ('Maternity leave', 'Maternity leave'), ('Paternity leave', 'Paternity leave'), ('Annual leave', 'Annual leave'), ('Compassionate leave', 'Compassionate leave'), ('Study leave', 'Study leave'), ('Jury duty leave', 'Jury duty leave'), ('Public holiday leave', 'Public holiday leave'), ('Unpaid leave', 'Unpaid leave'), ('Personal leave', 'Personal leave')], default='Personal leave', max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_days', models.PositiveIntegerField(default=30)),
                ('remaining_days', models.PositiveIntegerField(default=30)),
                ('status', models.CharField(choices=[('Requested', 'Requested'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Requested', max_length=20)),
                ('is_approved', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_approved', to='clinics.leave')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clinic_staff_leave', to='clinics.staff')),
            ],
            options={
                'unique_together': {('staff', 'approved_by')},
            },
        ),
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clinics.clinic')),
            ],
            options={
                'unique_together': {('clinic', 'date', 'country')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='clinicstaff',
            unique_together={('created_by', 'approved_by', 'clinic', 'staff', 'contract')},
        ),
        migrations.CreateModel(
            name='ClinicAvailability',
            fields=[
                ('appointment_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='caa', serialize=False, to='clinics.appointmenttype')),
                ('date', models.DateField()),
                ('available_slots', models.IntegerField(default=3, validators=[django.core.validators.MinValueValidator(0)])),
                ('max_slots', models.IntegerField(default=3, validators=[django.core.validators.MinValueValidator(0)])),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clinics.clinic')),
            ],
            options={
                'unique_together': {('clinic', 'appointment_type', 'date')},
            },
        ),
    ]
