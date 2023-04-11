from rest_framework.routers import DefaultRouter

from .views import ClinicViewSet,AppointmentViewSet

router = DefaultRouter()
router.register(r'clinics', ClinicViewSet, basename='clinic')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = router.urls
