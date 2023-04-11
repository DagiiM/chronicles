from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrescriptionViewSet, MedicationViewSet

router = DefaultRouter()
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'medications', MedicationViewSet, basename='medication')

urlpatterns = [
    path('', include(router.urls)),
]
