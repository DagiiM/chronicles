from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import About

class AboutForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = About
        fields = '__all__'