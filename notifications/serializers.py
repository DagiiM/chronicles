from app.serializers import BaseSerializer
from .models import Notification
from rest_framework import serializers

class NotificationSerializer(BaseSerializer):
    date_created = serializers.DateTimeField(format="%b %d %Y, %I:%M%p")
    date_sent = serializers.DateTimeField(format="%b %d %Y, %I:%M%p")
    date_read = serializers.DateTimeField(format="%b %d %Y, %I:%M%p")
    expiration_date = serializers.DateTimeField(format="%b %d %Y, %I:%M%p")

    class Meta:
        model = Notification
        fields = ['sender', 'recipients', 'subject', 'body', 'date_created', 'date_sent', 'date_read', 'expiration_date']
