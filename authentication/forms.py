from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.core.validators import validate_email
from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from .models import User
from app.forms import BaseForm

from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _



class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user with no privileges, with an email field added to the standard fields.
    """
    email = forms.EmailField(max_length=254, help_text=_('Required. Enter a valid email address.'))

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=_('Your password must contain at least 8 characters.'),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Your password can't be too similar to your other personal information.<br> Your password must contain at least 8 characters. <br> Your password can't be a commonly used password. <br> Your password can't be entirely numeric."),
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ErrorResponse(_("A user with that email address already exists."),status=409)
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        if password2 and len(password2) < 8:
            raise forms.ValidationError(_("Your password must contain at least 8 characters."))
        return password2
    
    def save_m2m(self):
        for field in self._meta.model._meta.many_to_many:
            if field.name in self.cleaned_data:
                field.save_form_data(self.instance, self.cleaned_data[field.name])
                
    def save_related(self, form):
        form.save_m2m()

    def save(self, commit=True):
        """
        Create and save a new User with no permissions.
        """
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            is_staff=False,
            is_active=True,
            is_superuser=False,
        )
        return user


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'email')