
from app.views import BaseViewSet
from .serializers import PrescriptionSerializer,MedicationSerializer
class PrescriptionViewSet(BaseViewSet):
    serializer_class = PrescriptionSerializer
    http_method_names = ['get']

class MedicationViewSet(BaseViewSet):
    serializer_class = MedicationSerializer
    http_method_names = ['get']
