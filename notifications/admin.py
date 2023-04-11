from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'notification_type', 'date_created', 'date_sent', 'date_read')
    list_filter = ('notification_type', 'importance_level', 'date_created', 'date_sent', 'date_read')
    search_fields = ('subject', 'body', 'related_object')
    autocomplete_fields = ('recipients',)
    raw_id_fields = ('recipients',)
    readonly_fields = ('id','sender', 'recipients','notification_type','subject','body', 'related_object','importance_level','date_created','date_sent', 'date_read','expiration_date')
