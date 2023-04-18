from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pharmacy.views import PrescriptionViewSet, MedicationViewSet
from clinics.views import ClinicViewSet,AppointmentViewSet
from authentication.views import UserViewSet
from notifications.views import NotificationViewSet
from consultations.views import ConsultationViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'clinics', ClinicViewSet, basename='clinic')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'consultations', ConsultationViewSet,basename='consultation')

urlpatterns = [
    path('api/', include(router.urls)),
]