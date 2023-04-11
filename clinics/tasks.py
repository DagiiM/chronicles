from datetime import date, timedelta
from django.utils import timezone



def create_clinic_availability(start_date: date, end_date: date) -> None:
    """
    Create ClinicAvailability objects for each day between start_date and end_date, for each clinic and appointment type.
    """
    clinics = Clinic.objects.all()
    appointment_types = AppointmentType.objects.all()
    for clinic in clinics:
        for appointment_type in appointment_types:
            for delta in range((end_date - start_date).days + 1):
                current_date = start_date + timedelta(days=delta)
                # Skip if the current date is a holiday
                if Holiday.objects.filter(clinic=clinic, country=clinic.country, date=current_date).exists():
                    continue
                ca, created = ClinicAvailability.objects.get_or_create(
                    clinic=clinic,
                    appointment_type=appointment_type,
                    date=current_date,
                    defaults={'max_slots': 100, 'available_slots': 100},
                )
                if not created:
                    ca.max_slots = 100
                    ca.available_slots = ca.get_available_slots()
                    ca.save()


# Call the function to create ClinicAvailability objects for the next 30 days
today = timezone.now().date()
create_clinic_availability(today, today + timedelta(days=29))
