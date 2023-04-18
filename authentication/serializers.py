from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from authentication.models import User
from app.serializers import BaseSerializer
from .forms import CustomUserCreationForm
from app.exceptions import ErrorResponse
from .forms import CustomUserCreationForm
from .models import User

class UserSerializer(BaseSerializer):
    """
    Serializer for User model.
    """
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'password', 'password1', 'password2']
        extra_kwargs = {'password': {'write_only': True,'style': {'input_type': 'password'}}}
        
    def validate(self, data):
        print(data)
        form = CustomUserCreationForm(data)
        if not form.is_valid():
            raise ErrorResponse.custom_validation_error(form.errors,status.HTTP_400_BAD_REQUEST)
        if data['password'] != data['password1']:
            raise ErrorResponse.custom_validation_error('Passwords do not match', status.HTTP_400_BAD_REQUEST)
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password1')
        validated_data.pop('password2')
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)


class DeleteUserProfileSerializer(BaseSerializer):
    email = serializers.EmailField()
    
    class Meta:
        model = User
        fields = ['email']
        
    def delete_user(self):
        logged = self.context['user']
        if logged.email != self.validated_data['email']:
            raise ErrorResponse.custom_validation_error('Invalid email address entered.', status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=self.validated_data['email'])
        except User.DoesNotExist:
            raise ErrorResponse.custom_validation_error("User with provided email address does not exist.", status.HTTP_400_BAD_REQUEST)
        user.delete()
    
        
class PasswordResetSerializer(BaseSerializer):
    email = serializers.EmailField(style={'input_type': 'email'})
    
    class Meta:
        model = User
        fields = ['email']

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except ObjectDoesNotExist:
            raise ErrorResponse.custom_validation_error('User with this email address does not exist.', status.HTTP_409_CONFLICT)
        return value

    def send_reset_email(self,user, request):
        token = PasswordResetTokenGenerator().make_token(user)
        uidb4 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uidb4, 'token': token}))
        subject = 'Password Reset Request'
        plaintext = render_to_string('password_reset_email.txt', {'user': user, 'reset_url': reset_url})
        html = render_to_string('password_reset_email.html', {'user': user, 'reset_url': reset_url})
        from_email = settings.EMAIL_HOST_USER
        to = user.email
        msg = EmailMultiAlternatives(subject, plaintext, from_email, [to])
        msg.attach_alternative(html, "text/html")
        try:
            msg.send()
            return True
        except Exception as e:
            # Log or send a notification to the development team
            return False
    


class PasswordChangeSerializer(UserSerializer):
    old_password = serializers.CharField(style={'input_type': 'password'}, required=False)
    new_password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['old_password', 'new_password']
        
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise ErrorResponse.custom_validation_error('Incorrect old password', status.HTTP_400_BAD_REQUEST)
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        user.password = make_password(validated_data['new_password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['new_password'])
        instance.save()
        return instance



class PasswordResetConfirmSerializer(UserSerializer):
    """
    Serializer for resetting password confirm view.
    """
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['new_password', 'confirm_password','uidb64', 'token']

    def validate_new_password(self, value):
        """
        Validate the new password
        """
        validate_password(value)
        return value

    def validate(self, attrs):
        """
        Check the uid and the token and set the user.
        """
        uidb64 = attrs.get('uidb64')
        token = attrs.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            attrs['user'] = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ErrorResponse.custom_validation_error('Invalid uid', status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(attrs['user'], token):
            raise  ErrorResponse.custom_validation_error('Invalid token', status.HTTP_400_BAD_REQUEST)

        # check if the user is active
        if not attrs['user'].is_active:
            raise  ErrorResponse.custom_validation_error('User account is disabled.', status.HTTP_400_BAD_REQUEST)

        if attrs['new_password'] != attrs['confirm_password']:
            raise  ErrorResponse.custom_validation_error('Passwords do not match.', status.HTTP_400_BAD_REQUEST)

        return attrs

    def save(self, **kwargs):
        """
        Save the new password
        """
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    

class LoginSerializer(UserSerializer):
    email = serializers.EmailField(style={'input_type': 'email'})
    password = serializers.CharField(style={'input_type':'password'})
    
    class Meta:
        model = User
        fields = ['email', 'password']
        
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    raise  ErrorResponse.custom_validation_error('User account is disabled.', status.HTTP_401_UNAUTHORIZED)
                data['user'] = user
            else:
                raise  ErrorResponse.custom_validation_error('Unable to log in with provided credentials.', status.HTTP_401_UNAUTHORIZED)
        else:
            raise  ErrorResponse.custom_validation_error('Must include "email" and "password".', status.HTTP_400_BAD_REQUEST)
        return data
    