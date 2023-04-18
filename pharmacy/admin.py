from django.contrib import admin
from .models import Medication, MedicationAvailability, Order, Delivery, Treatment, Prescription, \
    PrescriptionRefill, PrescriptionRefillRequest, Escalation, MedicalRecord


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'formulation', 'quantity', 'threshold', 'unit_price', 'manufacturer', 'supplier')
    list_filter = ('manufacturer', 'supplier')
    search_fields = ('name', 'formulation', 'description')


@admin.register(MedicationAvailability)
class MedicationAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('medication', 'clinic', 'is_available')
    list_filter = ('clinic', 'is_available')
    search_fields = ('medication__name', 'medication__formulation', 'medication__description')
    raw_id_fields = ('medication',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('medication', 'quantity', 'unit_price', 'supplier', 'ordered_at')
    list_filter = ('supplier', 'ordered_at')
    search_fields = ('medication__name', 'medication__formulation', 'medication__description')
    raw_id_fields = ('medication',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('medication', 'order', 'quantity', 'unit_price', 'received_at')
    list_filter = ('received_at',)
    search_fields = ('medication__name', 'medication__formulation', 'medication__description')
    raw_id_fields = ('medication', 'order')


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('medication', 'dosage', 'start_date', 'end_date', 'staff', 'clinic')
    list_filter = ('start_date', 'staff', 'clinic')
    search_fields = ('medication__name', 'medication__formulation', 'medication__description')
    raw_id_fields = ('medication', 'staff', 'clinic')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medication', 'dosage', 'start_date', 'end_date', 'staff', 'clinic', 'duration', 'refillable', 'refill_quantity')
    list_filter = ('start_date', 'staff', 'clinic', 'refillable')
    search_fields = ('medication__name', 'medication__formulation', 'medication__description')
    raw_id_fields = ('medication', 'staff', 'clinic')


@admin.register(PrescriptionRefill)
class PrescriptionRefillAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'patient', 'date_requested', 'status', 'remaining_refills')
    list_filter = ('status',)
    search_fields = ('prescription__medication__name', 'patient__username', 'patient__email')
    raw_id_fields = ('prescription', 'patient')


@admin.register(PrescriptionRefillRequest)
class PrescriptionRefillRequestAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'patient', 'date_requested', 'status')
    list_filter = ('status',)
    search_fields = ('prescription__medication__name', 'patient__username', 'patient__email')
    raw_id_fields = ('prescription', 'patient')

@admin.register(Escalation)
class EscalationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'treatment', 'date')
    list_filter = ('date',)
    search_fields = ('patient__username', 'patient__email', 'treatment__medication__name')
    raw_id_fields = ('patient', 'treatment')


admin.site.register(MedicalRecord)
'''
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'staff', 'appointment', 'created_at', 'updated_at')
    search_fields = ('patient__user__username', 'patient__user__first_name', 'patient__user__last_name', 'staff__user__username', 'staff__user__first_name', 'staff__user__last_name', 'appointment__id')
    ordering = ('-created_at', '-updated_at')
    raw_id_fields = ('patient', 'staff', 'appointment')
    '''