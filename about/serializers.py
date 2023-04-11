from rest_framework import serializers
from .models import About
from app.serializers import BaseSerializer

class AboutSerializer(BaseSerializer):
    class Meta:
        model = About
        fields = ('content', 'is_verified', 'verified_date')