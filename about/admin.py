from django.contrib import admin
from .models import About, AboutRelationship
from .forms import AboutForm

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    form = AboutForm
    
admin.site.register(AboutRelationship)
