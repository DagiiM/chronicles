
from django import forms

from .models import Clinic, BasicInfo, Location, Management, ClinicAvailability

class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ['name', 'is_active']

class BasicInfoForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
        exclude = ['clinic']

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = ['clinic']

class ManagementForm(forms.ModelForm):
    class Meta:
        model = Management
        exclude = ['clinic']

class ClinicAvailabilityForm(forms.ModelForm):
    class Meta:
        model = ClinicAvailability
        exclude = ['clinic']