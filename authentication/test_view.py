from django.contrib.auth import login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (UserSerializer,
                          DeleteUserProfileSerializer,
                          PasswordResetSerializer,
                          PasswordChangeSerializer,
                          LoginSerializer,
                          PasswordResetConfirmSerializer)
from authentication.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from utils.serializers import SearchSerializer, BaseSerializer
from rest_framework import generics
from utils.mixins import BaseViewSet

class UserViewSet(BaseViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'reset_password':
            return PasswordResetSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        elif self.action == 'password_reset_confirm':
            return PasswordResetConfirmSerializer
        elif self.action == 'destroy':
            return DeleteUserProfileSerializer
            
        else:
            return UserSerializer
        
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data,context={'request': request,'user': user})
        serializer.is_valid(raise_exception=True)
        try:
            serializer.delete_user()
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    '''

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
    '''
    @action(detail=False, methods=['post'], serializer_class=PasswordResetSerializer)
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return Response({'detail': 'User with this email address does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        serializer.send_reset_email(user, request)
        return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], serializer_class=PasswordChangeSerializer)
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def password_reset_confirm(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'detail': 'Password reset complete.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)


class EmailAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if email is None or password is None:
            return Response({'error': 'Please provide both email and password'},
                            status=HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        
        if not user:
            return Response({'error': 'Invalid email or password'},
                            status=HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key})
    

class SearchView(generics.GenericAPIView):
    serializer_class = SearchSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = serializer.save()
        return Response(results)