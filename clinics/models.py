from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Union,Tuple
from geopy.geocoders import Nominatim
from django.db.models import F,Q
from django.contrib.gis.db.models.functions import Distance
from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.db.models.query import QuerySet
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from geopy.distance import distance as geopy_distance
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from typing import Optional
from django.db.models import Count
from about.models import AboutRelationship

from authentication.models import User
from django.contrib.gis.geos import Point
from django_google_maps import fields as map_fields
from django_countries.fields import CountryField
from django.utils import timezone
from django_countries import countries

from .enums import Specialty, Gender, AppointmentStatus,Status,ContractStatus,LeaveType
from app.models import Searchable
from datetime import timedelta
from django.db.models import F, FloatField, ExpressionWrapper
import holidays

class BasicInfo(models.Model):
    """
    Model for storing basic information about a clinic.
    """
    clinic: 'Clinic' = models.OneToOneField('Clinic', on_delete=models.CASCADE, primary_key=True)
    name: str = models.CharField(max_length=255)
    address: str = models.CharField(max_length=255)
    city: str = models.CharField(max_length=255)
    state: str = models.CharField(max_length=2)
    zip_code: str = models.CharField(max_length=10)
    phone_number: str = models.CharField(max_length=20)
    email: str = models.EmailField()
    website: str = models.URLField(blank=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the basic information for the clinic.
        """
        return self.name


class Location(models.Model):
    """
    Model for storing the location of a clinic.
    """
    clinic:'Clinic' = models.OneToOneField('Clinic', on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=255, help_text="Address of the clinic.")
    geolocation = map_fields.GeoLocationField(max_length=100, help_text="Click on the map to select the location of the clinic.")

    def __str__(self):
        return self.clinic.name


class Management(models.Model):
    """
    Management model
    """
    clinic: 'Clinic' = models.OneToOneField('Clinic', on_delete=models.CASCADE, primary_key=True)
    medical_director: str = models.CharField(max_length=255)
    clinic_manager: str = models.CharField(max_length=255)
    hours_of_operation: str = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.clinic.name
 


class Holiday(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE)
    date = models.DateField()
    country = CountryField()

    class Meta:
        unique_together = (('clinic', 'date', 'country'),)

    def __str__(self):
        return f"{self.date} ({self.clinic.name}, {self.country.name})"



class ClinicAvailability(models.Model):
    clinic: 'Clinic' = models.ForeignKey('Clinic', on_delete=models.CASCADE,related_name='clinic_availability')
    appointment_type: 'AppointmentType' = models.ForeignKey('AppointmentType', related_name='caa', on_delete=models.CASCADE)
    date: models.DateField = models.DateField()
    available_slots: int = models.IntegerField(validators=[MinValueValidator(0)])
    max_slots: int = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self) -> str:
        return f"{self.appointment_type} availability for {self.clinic} on {self.date}"

    class Meta:
        unique_together = ('clinic', 'appointment_type', 'date')

    def save(self, *args, **kwargs) -> None:
        # Ensure that available_slots is not greater than max_slots
        self.available_slots = min(self.available_slots, self.max_slots)
        super().save(*args, **kwargs)

    def clean(self) -> None:
        # Ensure that available_slots is not greater than max_slots
        if self.available_slots > self.max_slots:
            raise ValidationError({'available_slots': "Available slots cannot be greater than max slots."})
        # Ensure that max_slots is greater than or equal to available_slots
        if self.max_slots < self.available_slots:
            raise ValidationError({'max_slots': "Max slots must be greater than or equal to available slots."})
    
    def get_available_slots(self):
        """
        Returns the number of available slots for this ClinicAvailability object, accounting for holidays.
        """
        # Get the number of appointments already scheduled for this date
        appointments_count = Appointment.objects.filter(
            clinic=self.clinic,
            appointment_type=self.appointment_type,
            appointment_date=self.date,
        ).count()

        # Get the number of available slots based on the max slots and the number of appointments already scheduled
        available_slots = self.max_slots - appointments_count

        # Subtract the number of holidays for this clinic and country on this date
        holidays_count = Holiday.objects.filter(
            clinic=self.clinic,
            country=self.clinic.country,
            date=self.date,
        ).count()
        available_slots -= holidays_count

        # Return the number of available slots, ensuring it's at least 0
        return max(available_slots, 0)
    
    
    def update_availability(self,days=30):
        """Create or update ClinicAvailability objects for the next `days` days."""
        today = timezone.localdate()
        end_date = today + timedelta(days=days)

        for clinic in Clinic.objects.all():
            # Get list of holidays for the clinic's country
            country_holidays = holidays.CountryHoliday(clinic.country.code)
            for appointment_type in AppointmentType.objects.all():
                for delta in range((end_date - today).days):
                    availability_date = today + timedelta(days=delta)

                    # Skip weekends
                    if availability_date.weekday() >= 5:
                        continue

                    # Skip holidays
                    if availability_date in country_holidays:
                        continue

                    caa, _ = ClinicAvailability.objects.get_or_create(
                        clinic=clinic,
                        appointment_type=appointment_type,
                        date=availability_date,
                        defaults={
                            'available_slots': appointment_type.max_slots,
                            'max_slots': appointment_type.max_slots,
                        }
                    )
                    caa.available_slots = appointment_type.max_slots - Appointment.objects.filter(
                        clinic=clinic,
                        appointment_type=appointment_type,
                        appointment_date=availability_date,
                    ).count()
                    caa.save()
       
    
class Clinic(Searchable):
    name: str = models.CharField(max_length=255)
    country = CountryField()
    is_active: bool = models.BooleanField(default=True)
    created_at:datetime = models.DateTimeField(default=timezone.now)
    updated_at:datetime  = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_created', null=True,blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_approved', null=True,blank=True)
    #search_fields = ['name']
    fields_to_return = ['name']
    
    class Meta:
        unique_together = ('created_by', 'approved_by')
        
    def __str__(self):
        return self.name + ' Clinic'

    def get_location(self) -> Union[None, Location]:
        """
        Retrieves the location of the clinic.

        Returns:
            Location: The location of the clinic if it exists, otherwise None.
        """
        try:
            location = Location.objects.get(clinic=self)
        except Location.DoesNotExist:
            location = None
        return location

    @staticmethod
    def get_nearby_clinics(user_location, radius=10):
        """
        Gets all active clinics within a given radius of a user's location.

        Args:
            user_location: A tuple containing the latitude and longitude of the user's location.
            radius: The search radius in kilometers.

        Returns:
            A queryset containing all active clinics within the search radius.
        """
        clinics = Clinic.objects.filter(is_active=True)

        # Iterate over each clinic and calculate its distance from the user's location
        for clinic in clinics:
            location = clinic.get_location()
            if location is not None:
                clinic_distance = geopy_distance(user_location, (location.geolocation.y, location.geolocation.x)).km
                if clinic_distance > radius:
                    clinics = clinics.exclude(pk=clinic.pk)

        return clinics
    
    def get_basic_info(self) -> Union[None, BasicInfo]:
        """
        Retrieves the basic information for the clinic.

        Returns:
            BasicInfo: The basic information for the clinic if it exists, otherwise None.
        """
        try:
            basic_info = BasicInfo.objects.get(clinic=self)
        except BasicInfo.DoesNotExist:
            basic_info = None
        return basic_info
    
    
    def get_management(self) -> Union[None, Management]:
        """
        Retrieves the management information for the clinic.

        Returns:
            Management: The management information for the clinic if it exists, otherwise None.
        """
        try:
            management = Management.objects.get(clinic=self)
        except Management.DoesNotExist:
            management = None
        return management   


    def get_full_capacity_days(self, appointment_type: 'AppointmentType', days: int=30) -> List[date]:
        # Get all days between today and end_date
        today = timezone.localdate()
        end_date = today + timedelta(days=days)
        all_days = [today + timedelta(days=delta) for delta in range((end_date - today).days)]

        # Get all days in the clinic availability model for the given appointment type
        availability_days = ClinicAvailability.objects.filter(
            clinic=self,
            appointment_type=appointment_type,
            date__gte=today,
            date__lte=end_date,
        ).values_list('date', flat=True)

        # Get the difference between all days and availability days
        full_capacity_days = set(all_days) - set(availability_days)

        # Add holidays to the full capacity days
        holidays = Holiday.objects.filter(
            clinic=self,
            country=self.country,
            date__gte=today,
            date__lte=end_date,
        ).values_list('date', flat=True)
        full_capacity_days |= set(holidays)

        # Add days with zero availability slots to the full capacity days
        zero_slots_days = ClinicAvailability.objects.filter(
            clinic=self,
            appointment_type=appointment_type,
            available_slots=0,
            date__gte=today,
            date__lte=end_date,
        ).values_list('date', flat=True)
        full_capacity_days |= set(zero_slots_days)

        # Add today to the full capacity days
        full_capacity_days.add(today)

        # Convert set to list and return
        return list(full_capacity_days)



class Agreement(models.Model):
    """
    Model representing staff agreements.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class AppointmentType(models.Model):
    """
    Model representing appointment types for staff.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    max_slots: int = models.IntegerField(default=100, validators=[MinValueValidator(0)])


    def __str__(self):
        return self.name
    
    def get_charge(self):
        try:
            return self.appointment_type_charge.get().amount
        except Charge.DoesNotExist:
            return None
        
        
    def get_available(self, clinic):
        # Get all related objects needed to determine availability
        specialties = self.appointment_specialty.all()
        clinic_availability = clinic.clinic_availability.filter(appointment_type=self)
        charges = self.appointment_type_charge.all()

        # Filter specialties by those with a valid contract
        specialties = specialties.filter(contracts__is_active=True)

        # Filter clinics by those with at least one staff member
        clinics = clinic.staff_clinic.filter(staff__is_approved=True)

        # Filter clinics by those with a staff member with the specialty
        clinics = clinics.filter(contract__specialty__in=specialties)

        # Filter charges by those with a non-zero amount
        charges = charges.filter(amount__gte=0)

        # Combine the filtered objects to get available appointment types
        appointment_types = set()
        for charge in charges:
            for clinic in clinics:
                for date in clinic_availability.filter(appointment_type=self):
                    if date.available_slots > 0:
                        appointment_types.add(charge.appointment_type)

        return list(appointment_types)

    
class Specialty(models.Model):
    """
    Model representing staff specialties.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE, related_name='appointment_specialty')

    def __str__(self):
        return self.name
    
    def has_charge(self):
        return self.appointment_type.get_charge() is not None


class Salary(models.Model):
    """
    Model representing staff salaries.
    """
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    description = models.TextField()
    frequency_choices = [
        ('hourly', 'Hourly'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annually', 'Annually')
    ]
    frequency = models.CharField(max_length=10, choices=frequency_choices)
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='salaries')

    def __str__(self):
        return f'{self.amount} {self.frequency}'


class Contract(models.Model):
    """
    Model representing staff contracts.
    """
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='contracts')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='contracts')
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE, related_name='contracts')
    status = models.CharField(max_length=20, choices=[(status.name, status.value) for status in ContractStatus],default=ContractStatus.PENDING.value)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.specialty} contract ({self.status})'
    
    def is_approved(self):
        return self.status == ContractStatus.APPROVED.value

class Charge(models.Model):
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE,related_name='appointment_type_charge')
    amount: Decimal = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'))
       

    def __str__(self):
        return self.appointment_type.name  

class Leave(models.Model):
    type = models.CharField(max_length=20, choices=[(tag.value, tag.value) for tag in LeaveType], default=LeaveType.PERSONAL_LEAVE.value)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveIntegerField(default=30)
    remaining_days = models.PositiveIntegerField(default=30)
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='clinic_staff_leave')
    status = models.CharField(max_length=20, choices=[(tag.value, tag.value) for tag in Status], default=Status.REQUESTED.value)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('self', on_delete=models.CASCADE, related_name='staff_approved', null=True,blank=True)
    
    class Meta:
        unique_together = ('staff', 'approved_by')

    def __str__(self):
        return f'{self.staff} leave'

    def clean(self):
        """
        Check if end date is greater than or equal to start date.
        """
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date must be greater than or equal to start date.')

    def save(self, *args, **kwargs):
        """
        Check remaining_days before saving.
        """
        if self.remaining_days < 0:
            raise ValidationError('Remaining days cannot be negative.')
        user = kwargs.pop('user', None)
        
        if not self.staff:
            self.staff = user
            
        if not self.approved_by:
            self.approved_by = user
        super().save(*args, **kwargs)

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff')
    clinic = models.ManyToManyField('Clinic', through='ClinicStaff')
    status = models.CharField(max_length=20, choices=[(status.name, status.value) for status in ContractStatus],default=ContractStatus.PENDING.value)
    is_approved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_created', null=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_approved', null=True,blank=True)

    class Meta:
        unique_together = ('created_by', 'approved_by')

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
    
    def is_on_leave(self, check_date=None):
        """
        Checks if staff is on leave on the given date or today's date.
        """
        if not check_date:
            check_date = date.today()

        # Get all approved leaves for this staff that overlap with the check_date
        overlapping_leaves = Leave.objects.filter(staff=self, is_approved=True, start_date__lte=check_date, end_date__gte=check_date)

        return overlapping_leaves.exists()
    

    def is_valid_recipient(self):
        """
        Checks if the staff member is a valid recipient for appointments.

        Returns:
            bool: True if the staff member is valid, False otherwise.
        """
        # Check if the staff member is approved.
        if not self.is_approved:
            return False

        # Check if the staff member has an approved contract.
        if not self.clinic_staff.filter(contract__is_active=True).exists():
            return False

        # Check if the staff member has a specialty set.
        if not self.clinic_staff.filter(contract__is_active=True, contract__specialty__isnull=False).exists():
            return False

        # Check if the staff member's specialty has an appointment type that has a charge model attached to it.
        if not self.clinic_staff.filter(
                contract__is_active=True,
                contract__specialty__isnull=False,
                contract__specialty__appointment_type__appointment_type_charge__isnull=False
        ).exists():
            return False

        return True

class ClinicStaffManager(models.Manager):
    def select_staff(self, clinic: Clinic, appointment_type: AppointmentType,check_date=date.today()) -> QuerySet:
        """
        Select staff based on appointment type, active contract status, and leave status.

        Args:
            clinic: Clinic object to filter staff by.
            appointment_type: AppointmentType object to filter staff by.
            check_date: Date object to filter staff by.

        Returns:
            QuerySet of Staff objects.
        """
        
        staff_available = self.get_available_staff(check_date=check_date)
        
        staff_available = staff_available.filter(
            clinic_staff__clinic=clinic,
            clinic_staff__contract__specialty__appointment_type=appointment_type,
        ).order_by('id').order_by('?')

        # To retrieve the staff with the least number of appointments assigned so far,
        # you can use the annotate method to count the number of appointments for each staff,
        # and then order the results by the number of appointments in ascending order:
        staff_available = staff_available.annotate(
            num_appointments=Count('appointment')
            ).order_by('num_appointments')

        # Finally, you can retrieve the first element from the sorted and shuffled queryset:
        staff = staff_available.first()
        if staff is None:
            raise ValueError('No staff available')
        return staff


    def get_available_staff(self,check_date) -> QuerySet:
        """
        Get staff who are not on leave.
        Retrieve all approved staff
        Retrieve all with active contracts
        Retrieve all staff not on leave

        Returns:
            QuerySet of Staff objects.
        """
        staff_pool = Staff.objects.filter(is_approved=True)
        
        staff_pool = staff_pool.filter(clinic_staff__contract__is_active=True)

        return staff_pool.exclude(
            **self.get_staff_on_leave_filter(check_date=check_date)
        )
    
    def get_staff_on_leave_filter(self,check_date) -> Dict[str, Union[Q, Tuple[Q]]]:
        """
        Get the filter for staff who are on leave.

        Returns:
            Dictionary containing the filter as a Q object or a tuple of Q objects.
        """
        
        return {
            'clinic_staff__staff__clinic_staff_leave__isnull': False,
            'clinic_staff__staff__clinic_staff_leave__is_approved': False,
            'clinic_staff__staff__clinic_staff_leave__start_date__lte': check_date,
            'clinic_staff__staff__clinic_staff_leave__end_date__gte': check_date,
        }
 
        
class ClinicStaff(models.Model):
    """
    Model representing the relationship between a clinic and its staff.
    """
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='staff_clinic')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='clinic_staff')
    permission_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='clinic_staff')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='clinic_staff')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_clinic_created', null=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_clinic_approved', null=True,blank=True)

    def __str__(self):
        return f"{self.staff.user.first_name} {self.staff.user.last_name}"
    
    class Meta:
        unique_together = ('created_by', 'approved_by','clinic', 'staff','contract')
        
    def is_approved(self):
        return self.contract.is_approved()

    def has_specialty(self):
        return self.contract.specialty is not None

    def has_charge(self):
        return self.contract.specialty.has_charge()

    def process_salary(self) -> None:
        """
        Process salary for the given staff.
        """
        salary = Salary.objects.filter(agreement=self.contract.agreement).first()
        if not salary:
            raise ValueError(f"No salary found for agreement '{self.contract.agreement.name}'.")
        # Salary processing logic here
        pass

    objects = ClinicStaffManager()

    @staticmethod
    def group_staff_by_status() -> Dict[str, QuerySet]:
        """
        Group staff into various groups based on leave, appointment types, contract types, and permission groups.

        Returns:
            Dictionary with group names as keys and QuerySets of Staff objects as values.
        """
        staff_on_leave = User.objects.filter(clinic_staff__leave__isnull=False)
        staff_on_leave_and_not_selected = Staff.objects.filter(is_on_leave(check_date=date.today()), False)
        groups = {
            'staff_on_leave': staff_on_leave,
            'staff_with_contract': User.objects.filter(clinic_staff__contract__isnull=False, staff__in=staff_on_leave_and_not_selected),
            'staff_with_permission': User.objects.filter(clinic_staff__permission_group__isnull=False, staff__in=staff_on_leave_and_not_selected),
        }
        return groups
    
    
class Patient(models.Model):
    """
    Patient model
    """
    user:User = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    age:int = models.IntegerField(validators=[MinValueValidator(0)])
    gender:str = models.CharField(max_length=10, choices=[(tag.name, tag.value[1]) for tag in Gender])
    address:str = models.CharField(max_length=255)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' ' + self.user.email
      
    
       
class Appointment(Searchable):
    """
    Appointment model
    """
    clinic:Clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE, related_name='clinic_appointments', related_query_name='clinic_appointments',blank=True,null=True)
    staff:Staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name='staff_appointments', related_query_name='appointment',blank=True)
    patient: Union[Patient, User] = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='patient_appointments', related_query_name='patient_appointment')
    start_time: datetime = models.TimeField()
    end_time: datetime = models.TimeField()
    appointment_date: datetime = models.DateField(start_time)
    weight: int = models.IntegerField(default=1)
    rating: float = models.FloatField(default=None,blank=True,null=True)
    status: AppointmentStatus = models.CharField(max_length=20, 
                                                 choices=[(status.value, status.name) for status in AppointmentStatus],
                                                 default=AppointmentStatus.CONFIRMED.value
                                                 )
    appointment_type:AppointmentType = models.ForeignKey(AppointmentType,related_name='patient_appointment_type', on_delete=models.CASCADE)
    appointment_reason = models.TextField(blank=True, null=True)
    about = GenericRelation(AboutRelationship, related_query_name='appointment')

    def latest_verified_about(self):
        about_type = ContentType.objects.get_for_model(self.__class__)
        about_qs = About.objects.filter(content_type=about_type, object_id=self.id, is_verified=True).order_by('-id')
        if about_qs.exists():
            return about_qs.first()
        return None
    
        

    def __str__(self):
        return f'{self.staff} - {self.patient} - {self.appointment_date}'
    
  
    def get_charge(self)->Decimal:
        if self.appointment_type:
            return self.appointment_type.charge.amount
        else:
            return None
        
    @staticmethod
    def get_appointments_for_staff(staff: Staff) -> models.QuerySet:
        """
        Retrieve Appointments for a given staff
        """
        return Appointment.objects.filter(staff=staff)

    @staticmethod
    def get_appointments_for_patient(patient: Union[Patient, User]) -> models.QuerySet:
        """
        Retrieve Appointments for a given patient
        """
        return Appointment.objects.filter(patient=patient)

    @staticmethod
    def get_upcoming_appointments_for_staff(staff: Staff, days: int = 7) -> models.QuerySet:
        """
        Retrieve Upcoming Appointments for a given staff
        """
        return Appointment.objects.filter(
            staff=staff, appointment_date__range=[timezone.localtime(timezone.now()), timezone.localtime(timezone.now()) + timezone.timedelta(days=days)]
        )

    @staticmethod
    def get_upcoming_appointments_for_patient(patient: Union[Patient, User], days: int = 7) -> models.QuerySet:
        """
        Retrieve Upcoming Appointments for a given patient
        """
        return Appointment.objects.filter(
            patient=patient, appointment_date__range=[timezone.localtime(timezone.now()),timezone.localtime(timezone.now()) + timezone.timedelta(days=days)]
        )
        
    def rate(self: 'Appointment', patient: Union[Patient, User], rating: float) -> None:
        """
        Method to rate the appointment

        Args:
        - rating (float): The rating given to the appointment (between 0 and 5)
        """
        if self.patient != patient:
            raise ValidationError('Only the patient who attended the appointment can rate it')

        if rating < 0 or rating > 5:
            raise ValidationError("Rating should be between 0 and 5")

        if self.rating is not None:
            raise ValidationError("You have already rated this appointment")

        # Use F() function to update the weight and rating fields in the database
        print(f"Update...{rating}")
        # Use F() function to update the weight and rating fields in the database
        Appointment.objects.filter(id=self.id).update(
            weight=F('weight') + 1,
                rating=rating
        )
        # Save the changes to the object
        self.refresh_from_db()


    def get_absolute_url(self) -> str:
        """
        Retrieve url
        """
        return reverse('appointment_detail', args=[str(self.id)])

    
    def get_staff_name(self) -> str:
        """
        Retrieve Staff name
        """
        if self.staff and hasattr(self.staff, 'user'):
            return self.staff.user.get_full_name()
        elif self.staff:
            return str(self.staff)
        else:
            return ''

    def get_patient_name(self) -> str:
        """
        Retrieve Patient name
        """
        if isinstance(self.patient, User):
            return self.patient.get_full_name()
        elif isinstance(self.patient, Patient):
            return self.patient.user.get_full_name()
        else:
            return str(self.patient)
        
    def save(self, *args, **kwargs):
        staff_queryset = ClinicStaff.objects.select_staff(clinic=self.clinic,appointment_type=self.appointment_type)
        self.staff = staff_queryset
        
        # Check if the appointment date is in the future
        if self.appointment_date > timezone.localdate():
            # Check if the appointment date is within the next 30 days
            if (self.appointment_date - timezone.localdate()).days <= 30:
                # Update the availability for the next 30 days
                ClinicAvailability.update_availability(3)
            # Get the ClinicAvailability object for the appointment type and date
            caa = self.clinic.clinic_availability.filter(date=self.appointment_date).first()
            if not caa:
                raise ValidationError(f"No Clinic Available for appointment type '{self.appointment_type}' and date '{self.appointment_date}'.")
            # Update the available_slots of the ClinicAvailability object
            if caa.available_slots == 0:
                raise ValidationError("No available slots")
            elif caa.available_slots > 0:
                caa.available_slots -= 1
                caa.save()
            else:
                raise ValidationError("No available slots")
        else:
            raise ValidationError("Appointment Date has to be a future date")
        
        super().save(*args, **kwargs)


