from rest_framework import serializers
from .models import Clinic, BasicInfo, Location, Management, ClinicAvailability,AppointmentType
from app.serializers import BaseSerializer
from about.serializers import AboutSerializer
from .models import Charge

class ClinicAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicAvailability
        fields = ('id', 'appointment_type', 'date', 'available_slots')

class ManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Management
        fields = ('id', 'medical_director', 'clinic_manager', 'hours_of_operation')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'address', 'geolocation')

class BasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicInfo
        fields = ('id', 'name', 'address', 'city', 'state', 'zip_code', 'phone_number', 'email', 'website')


class ClinicSerializer(BaseSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        fields = ('id', 'name', 'is_active', 'created_at')

    def get_created_at(self, obj):
        return obj.created_at.strftime("%B %d, %Y")
    
    
from rest_framework import serializers
from django.utils import timezone
from .models import Appointment
'''

class AppointmentSerializer(serializers.ModelSerializer):
    appointment_date = serializers.DateField(input_formats=['%Y-%m-%d'], required=True)

    class Meta:
        model = Appointment
        fields = ['appointment_date']

    def validate_appointment_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError('The appointment date must be in the future.')
        return value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'] = serializers.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S'], required=False)
        self.fields['end_time'] = serializers.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S'], required=False)

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError('The start time must be before the end time.')
        return data
'''


class ChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = ('amount',)

class AppointmentSerializer(BaseSerializer):

    class Meta:
        model = Appointment
        fields = ['id','appointment_date','start_time', 'end_time','status','clinic','patient','staff','appointment_type','rating']
        read_only_fields = ('id', 'weight', 'rating')
        
    
class AppointmentFeedbackSerializer(serializers.Serializer):
    rating = serializers.FloatField(min_value=0, max_value=5)

class AppointmentTypeSerializer(BaseSerializer):
    charge = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentType
        fields = ('id', 'name', 'description', 'charge')

    def get_charge(self, obj):
        return obj.get_charge()
