from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Consultation


class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('sender__username', 'recipient__username')
    autocomplete_fields = ('recipient',)


admin.site.register(Consultation, ConsultationAdmin)
