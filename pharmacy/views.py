
from app.views import BaseViewSet
from .serializers import PrescriptionSerializer,MedicationSerializer
from rest_framework import permissions

class PrescriptionViewSet(BaseViewSet):
    serializer_class = PrescriptionSerializer
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(patient=self.request.user.pk)
        return queryset

class MedicationViewSet(BaseViewSet):
    serializer_class = MedicationSerializer
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(patient=self.request.user.pk)
        return queryset
