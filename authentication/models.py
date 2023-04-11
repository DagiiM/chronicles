from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, MaxLengthValidator
from django.db import models, IntegrityError
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from app.models import Searchable
from notifications.enums import NotificationPreference

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        self.validate_email(email)
        username = self.generate_username(extra_fields.get('first_name'))
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

    def validate_email(self, email):
        if not email:
            raise ErrorResponse(message='The Email field must be set', status_code=400)
        validate_email(email)

    def generate_username(self, first_name):
        username = slugify(first_name)
        i = 1
        while self.filter(username=username).exists():
            username = f"{slugify(first_name)}{i}"
            i += 1
        return username


class User(AbstractBaseUser, PermissionsMixin, Searchable):
    email = models.EmailField(unique=True, validators=[validate_email])
    first_name = models.CharField(max_length=30, validators=[MaxLengthValidator(30)])
    last_name = models.CharField(max_length=30, validators=[MaxLengthValidator(30)])
    username = models.CharField(max_length=30, blank=True)
    notification_preference=models.CharField(max_length=20, choices=NotificationPreference.choices, default=f"{NotificationPreference.DATABASE},{NotificationPreference.EMAIL}"),
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)

    search_fields = ['first_name', 'last_name']
    fields_to_return = ['first_name', 'last_name']

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        # Check if the user has the permission directly
        if self.user_permissions.filter(codename=perm).exists():
            return True

        # Check if the user has the permission through their group
        if self.groups.filter(permissions__codename=perm).exists():
            return True

        return True
    
    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True

        # Check if the user has any permissions for this app label
        user_perms = self.user_permissions.filter(
            content_type__app_label=app_label
        ).values_list('codename', flat=True)
        group_perms = self.groups.filter(
            permissions__content_type__app_label=app_label
        ).values_list('permissions__codename', flat=True)
        return bool(user_perms or group_perms)

    @property
    def groups(self):
        if not hasattr(self, '_groups'):
            self._groups = Group.objects.filter(name=self)
        return self._groups

    @property
    def user_permissions(self):
        if not hasattr(self, '_user_permissions'):
            self._user_permissions = Permission.objects.filter(codename=self)
        return self._user_permissions
    
    class Meta:
        ordering = ['-date_joined']

