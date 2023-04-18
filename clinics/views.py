import datetime
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Clinic,ClinicAvailability
from app.views import BaseViewSet
from .serializers import ClinicSerializer,AppointmentTypeSerializer, ManagementSerializer, LocationSerializer, BasicInfoSerializer
from rest_framework import viewsets, permissions
from .models import Appointment,AppointmentType
from .serializers import AppointmentSerializer
from django.utils import timezone
from datetime import datetime, timedelta
from about.serializers import AboutSerializer
from django.contrib.contenttypes.models import ContentType
from about.models import About
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


class ClinicViewSet(BaseViewSet):
    serializer_class = ClinicSerializer

    @action(detail=True, methods=['get'], name='Clinic Info')
    def clinic_info(self, request, pk=None):
        clinic = self.get_object()
        location = clinic.get_location()
        basic_info = clinic.get_basic_info()
        management = clinic.get_management()

        if not all([location, basic_info, management]):
            return Response({'message': 'Some data not found.'}, status=status.HTTP_404_NOT_FOUND)

        location_serializer = LocationSerializer(location)
        basic_info_serializer = BasicInfoSerializer(basic_info)
        management_serializer = ManagementSerializer(management)

        data = {
            'location': location_serializer.data,
            'basic_info': basic_info_serializer.data,
            'management': management_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def appointment_types(self, request, pk=None):
        clinic = self.get_object()
        appointment_types = AppointmentType.objects.filter(
            caa__clinic=clinic
        ).distinct()

        available_appointment_types = []
        for appointment_type in appointment_types:
            if appointment_type.get_available(clinic):
                available_appointment_types.append(appointment_type)

        serializer = AppointmentTypeSerializer(available_appointment_types, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def full_capacity_days(self, request, pk=None):
        clinic = self.get_object()
        appointment_type_id = request.data.get('appointment_type')
        appointment_type = get_object_or_404(AppointmentType, id=appointment_type_id)
        full_capacity_days = clinic.get_full_capacity_days(appointment_type=appointment_type)

        # Paginate the queryset
        page = self.paginate_queryset(full_capacity_days)
        if page is not None:
            return self.get_paginated_response(page)

        return Response({'full_capacity_days': full_capacity_days})
    
    @action(detail=False, methods=['get'], name='Clinics Near Me')
    def clinics_near_me(self, request):
        """
        Returns a paginated list of active clinics within a certain radius of the user's location.

        Required GET parameters:
            - latitude: The user's latitude.
            - longitude: The user's longitude.
            - radius: The search radius in kilometers (optional, defaults to 10).

        Returns:
            A paginated list of clinics within the search radius.
        """
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        radius = request.GET.get('radius', 10)

        if not all([latitude, longitude]):
            return Response({'error': 'Please provide a latitude and longitude.'}, status=400)

        try:
            user_location = (float(latitude), float(longitude))
        except ValueError:
            return Response({'error': 'Invalid latitude and/or longitude.'}, status=400)

        try:
            radius = float(radius)
        except ValueError:
            return Response({'error': 'Invalid radius.'}, status=400)

        clinics = Clinic.get_nearby_clinics(user_location, radius)
        page = self.paginate_queryset(clinics)
        if page is not None:
            serializer = ClinicSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ClinicSerializer(clinics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'], name='New Clinics')
    def new_clinics(self, request):
        """
        Gets all clinics created within the last month.

        Returns:
            A list of dictionaries containing the details of each clinic.
        """
        now = timezone.now()
        one_month_ago = now - timedelta(days=30)
        new_clinics = self.get_queryset().filter(created_at__gte=one_month_ago, is_active=True)
        page = self.paginate_queryset(new_clinics)
        if page is not None:
            serializer = ClinicSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ClinicSerializer(new_clinics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentViewSet(BaseViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # get the existing queryset
        queryset = super().get_queryset()

        # filter appointments for logged-in user
        user = self.request.user
        queryset = queryset.filter(patient=user)

        return queryset


    def perform_create(self, serializer):
        """
        Set the patient based on the authenticated user
        """
        user = self.request.user
        
        serializer.save(patient=user)
        
    @action(detail=False, methods=['get'])
    def about_appointment(self, request):
        """
        Returns the latest verified about for all appointments
        """
        about_type = ContentType.objects.get_for_model(Appointment)
        
        about = About.objects.filter(
            content_type=about_type,
            is_verified=True,
        ).order_by('-verified_date')[:1]
        
        serializer = AboutSerializer(about,many=True)

        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_appointments(self, request):
        """
        Returns a list of recent appointments for the authenticated user
        """
        user = self.request.user
        appointments = self.get_queryset().filter(
            patient=user,
            appointment_date__gte=timezone.now() - timedelta(days=30)
        )
        page = self.paginate_queryset(appointments)
        if page is not None:
            serializer = AppointmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response({'message':'No Recent Appointments'},status=404)
    
    @action(detail=False, methods=['get'])
    def not_rated_appointments(self, request):
        """
        Returns a list of recent appointments for the authenticated user
        """
        user = self.request.user
        appointments = self.get_queryset().filter(
            patient=user,
            rating__isnull=True
        )
        page = self.paginate_queryset(appointments)
        if page is not None:
            serializer = AppointmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response({'message':'No Unrated Appointments'},status=404)


    @action(detail=True, methods=['get', 'post'])
    def appointment_feedback(self, request, pk=None):
        """
        Endpoint to get or post feedback (rating) for a specific appointment
        """
        appointment = self.get_object()

        if appointment.rating is not None:
            return Response({'error': 'This appointment has already been rated'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data)
        elif request.method == 'POST':
            if appointment.patient != request.user:
                return Response({'error': 'You can only rate your own appointments'}, status=status.HTTP_403_FORBIDDEN)
            rating = request.data.get('rating')
            if rating is None:
                return Response({'error': 'Please provide a rating'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                appointment.rate(request.user, float(rating))
                appointment.save()
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data)

    
