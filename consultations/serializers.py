from rest_framework import serializers
from .models import Consultation
from app.serializers import BaseSerializer

class ConsultationSerializer(BaseSerializer):
    class Meta:
        model = Consultation
        fields = ['id', 'sender', 'recipient', 'content', 'created_at', 'is_read', 'status']

    def create(self, validated_data):
        validated_data.pop('id', None)
        return super().create(validated_data)
