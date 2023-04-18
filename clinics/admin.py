import json
from django import forms
from django.contrib import admin
from django.contrib.gis.db import models
from django.contrib.admin.widgets import AdminTextInputWidget
from django.urls import reverse
from django.utils.html import format_html
from geopy.geocoders import GoogleV3
from .models import Clinic, Location, Patient, Charge,ClinicStaff, Staff, Appointment, ClinicAvailability, BasicInfo, Management, AppointmentType, Agreement, Specialty, Salary, Contract, Leave
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from .widgets import LocationWidget
from django.contrib.gis.forms import PointField
from .forms import LocationForm
from .enums import ContractStatus
from django.core.validators import MinValueValidator
from .models import Holiday
from django_countries.fields import  LazyTypedChoiceField
from django_countries import countries

class LimitedCountryChoiceField(LazyTypedChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = [(code, name) for code, name in countries if name in ['Kenya', 'Uganda', 'Tanzania', 'South Sudan', 'Rwanda', 'Democratic Republic of the Congo']]

class HolidayAdminForm(forms.ModelForm):
    country = LimitedCountryChoiceField(choices=[])

    class Meta:
        model = Holiday
        fields = '__all__'

class ClinicAdminForm(forms.ModelForm):
    country = LimitedCountryChoiceField(choices=[])

    class Meta:
        model = Holiday
        fields = '__all__'

       
@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    form = HolidayAdminForm
    list_display = ('clinic', 'date', 'country')
    list_filter = ('country',)
    search_fields = ('clinic', 'country')
    ordering = ('-date',)

class LocationInlineForm(forms.ModelForm):
    geolocation = PointField(widget=LocationWidget)

    class Meta:
        model = Location
        fields = '__all__'
 
class LocationInline(admin.StackedInline):
    model = Location
    form = LocationInlineForm
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user_location = self.get_user_location(request)
        if user_location:
            qs = qs.annotate(distance=Distance('location', user_location)).order_by('distance')
        return qs

    def get_user_location(self, request):
        """
        Retrieves the user's location from the request headers or session.
        Assumes that the user's location is stored as a (latitude, longitude) tuple.
        """
        # Check if the user's location is in the request headers
        if 'X-User-Location' in request.headers:
            lat, lon = request.headers['X-User-Location'].split(',')
            return Point(float(lon), float(lat))
        
        # Check if the user's location is in the session
        if 'user_location' in request.session:
            lat, lon = request.session['user_location']
            return Point(float(lon), float(lat))

        # If user's location is not available, return None
        return None


admin.site.register(Location, OSMGeoAdmin)


class ClinicAvailabilityForm(forms.ModelForm):
    max_slots = forms.IntegerField(validators=[MinValueValidator(0)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the clinic instance associated with this ClinicAvailability instance
        clinic_instance = self.instance.clinic
        # Set the maximum value for the max_slots field based on the clinic's configuration
        self.fields['max_slots'].validators.append(MaxValueValidator(clinic_instance.max_appointment_slots_per_day))

    class Meta:
        model = ClinicAvailability
        fields = '__all__'

class ClinicAvailabilityInline(admin.TabularInline):
    model = ClinicAvailability
    extra = 0

class BasicInfoInline(admin.TabularInline):
    model = BasicInfo
    extra = 0


class ManagementInline(admin.TabularInline):
    model = Management
    extra = 0

class SpecialtyInline(admin.TabularInline):
    model = Specialty
    extra = 0

class SalaryInline(admin.TabularInline):
    model = Salary
    extra = 0

class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0

class LeaveInline(admin.TabularInline):
    model = Leave
    extra = 0

# Register each model with its corresponding admin class
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    form = ClinicAdminForm
    list_display = ('name','country', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'country','is_active')
    autocomplete_fields = ()
    inlines = [
        BasicInfoInline,
        LocationInline,
        ManagementInline,
        ClinicAvailabilityInline,
    ]

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    pass

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    inlines = [
        ContractInline,
    ]

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    inlines = [
        ContractInline,
    ]

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('staff', 'start_date', 'end_date', 'type', 'status','is_approved')
    list_filter = ('type', 'status')
    search_fields = ('staff__user__first_name', 'staff__user__last_name')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'specialty', 'start_date', 'end_date', 'agreement', 'salary','is_active')
    list_filter = ('specialty', 'agreement', 'salary')
    search_fields = ('specialty__name', 'agreement__name', 'salary__name')
    
    def get_readonly_fields(self, request, obj=None):
        # make 'status' field read-only for existing objects
        if obj:
            return ('status', )
        return ()
    
    def save_model(self, request, obj, form, change):
        # set status to PENDING when creating a new contract
        if not change:
            pass
            #obj.status = ContractStatus.PENDING
        obj.save()
        

class StaffAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'is_approved','created_by', 'approved_by')
    fields = ('user', 'status','is_approved')
    autocomplete_fields = ('user', 'created_by', 'approved_by')
    search_fields = ('user__first_name', 'user__last_name')
    readonly_fields = ('clinic','created_by', 'approved_by')   

admin.site.register(Staff, StaffAdmin)

@admin.register(ClinicStaff)
class ClinicStaffAdmin(admin.ModelAdmin):
    list_display = ('staff', 'clinic', 'created_by', 'approved_by')
    autocomplete_fields = ('staff', 'clinic', 'created_by', 'approved_by')
    search_fields = ('staff', 'clinic', 'created_by', 'approved_by')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'age', 'gender', 'address')
    list_filter = ('gender', )
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'address')

@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment_type', 'amount')
    list_filter = ('appointment_type', )
    autocomplete_fields = ('appointment_type',)
    search_fields = ('appointment_type__name', )

@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff', 'patient', 'appointment_type', 'appointment_date', 'start_time', 'end_time', 'status', 'rating')
    autocomplete_fields = ['staff', 'patient', 'appointment_type']
    list_filter = ('status', 'appointment_type')
    search_fields = ('staff__user__username', 'staff__user__first_name', 'staff__user__last_name', 'patient__user__username', 'patient__user__first_name', 'patient__user__last_name', 'appointment_type__name')
    readonly_fields = ('weight', 'rating','get_charge', 'get_staff_name', 'get_patient_name')
    ordering = ('-appointment_date', '-start_time')
    date_hierarchy = 'appointment_date'
    raw_id_fields = ('staff','patient','appointment_type')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(staff__user=request.user)

