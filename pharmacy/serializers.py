from app.serializers import BaseSerializer
from rest_framework import serializers
from .models import (Medication, MedicationAvailability, Order, Delivery, Treatment,
                     Prescription, PrescriptionRefill, PrescriptionRefillRequest)


class MedicationSerializer(BaseSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name', 'description','manufacturer','unit_price']


class MedicationAvailabilitySerializer(BaseSerializer):
    medication = MedicationSerializer()

    class Meta:
        model = MedicationAvailability
        fields = ['id', 'medication', 'quantity']


class OrderSerializer(BaseSerializer):
    medication = MedicationSerializer()

    class Meta:
        model = Order
        fields = ['id', 'medication', 'quantity']


class DeliverySerializer(BaseSerializer):
    medication = MedicationSerializer()
    order = OrderSerializer()

    class Meta:
        model = Delivery
        fields = ['id', 'medication', 'order', 'delivery_date']


class TreatmentSerializer(BaseSerializer):
    medication = MedicationSerializer()

    class Meta:
        model = Treatment
        fields = ['id', 'medication', 'start_date', 'end_date']


class PrescriptionSerializer(BaseSerializer):
    medication = MedicationSerializer()
    treatment = TreatmentSerializer()

    class Meta:
        model = Prescription
        fields = ['id', 'medication', 'treatment', 'dosage', 'start_date', 'end_date']


class PrescriptionRefillSerializer(BaseSerializer):
    prescription = PrescriptionSerializer()

    class Meta:
        model = PrescriptionRefill
        fields = ['id', 'prescription', 'remaining_refills']


class PrescriptionRefillRequestSerializer(BaseSerializer):
    prescription = PrescriptionSerializer()

    class Meta:
        model = PrescriptionRefillRequest
        fields = ['id', 'prescription', 'status']
