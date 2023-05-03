from django.contrib.auth import login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, mixins, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import User
from .serializers import (UserSerializer, DeleteUserProfileSerializer,
                          PasswordResetSerializer, PasswordChangeSerializer,
                          LoginSerializer, PasswordResetConfirmSerializer)
from app.views import BaseViewSet,allow_any
from app.serializers import BaseSerializer, SearchSerializer
from clinics.models import Clinic
from clinics.serializers import ClinicSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

class GetUserIDView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        user_id = request.user.id
        response = Response({'user_id': user_id})
        response["Access-Control-Allow-Headers"] = "Authorization"
        return response

class UserViewSet(BaseViewSet):
    """
    A viewset for managing users.
    """
    serializer_class = UserSerializer
    lookup_field = 'pk'
    #permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(pk=self.request.user.pk)
        return queryset
    
    @allow_any
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        serializer_class = DeleteUserProfileSerializer
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request, 'user': user})
        serializer.is_valid(raise_exception=True)
        try:
            serializer.delete_user()
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({'detail': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)

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
    
    @action(detail=False, methods=["post"],serializer_class=PasswordResetConfirmSerializer)
    def password_reset_confirm(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None:
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if PasswordResetTokenGenerator().check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"detail": "Password reset complete."}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"], serializer_class=ClinicSerializer)
    def clinics_near_me(self, request, pk=None):
        # Get user location from the request data
        user_location = request.data.get("user_location")

        # Check if user location is provided
        if not user_location:
            return Response({"error": "User location not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse user location from string to float tuple
        try:
            lat, lon = map(float, user_location.split(","))
        except ValueError:
            return Response({"error": "Invalid user location provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Get all active clinics within 10km of the user location
        nearby_clinics = Clinic.get_nearby_clinics((lat, lon), radius=10)

        # Serialize the nearby clinics and return as response
        serializer = ClinicSerializer(nearby_clinics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EmailAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if email is None or password is None:
            return Response({'detail': 'Please provide both email and password'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        
        if not user:
            return Response({'detail': 'Invalid email or password'},
                            status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key})
    
class SearchView(generics.GenericAPIView):
    serializer_class = SearchSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = serializer.save()
        return Response(results)

