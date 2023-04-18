
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from django_fsm import FSMField, transition, FSMIntegerField
from django_fsm_log.decorators import fsm_log_by
from django.db.models.signals import pre_save
from django.dispatch import receiver
from clinics.models import Appointment,Clinic,Patient,Staff
from authentication.models import User
from typing import Dict, List, Union,Tuple
from datetime import date, datetime
from client.views import appointments

class Medication(models.Model):
    name = models.CharField(max_length=50)
    formulation = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    threshold = models.PositiveIntegerField(default=10, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    manufacturer = models.CharField(max_length=50)
    supplier = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_low_on_stock(self):
        return self.quantity <= self.threshold
    
    def __str__(self):
        return f'{self.name} formulation - {self.formulation}'

class MedicationAvailability(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.medication} is_available: ({self.is_available})'

class Order(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    supplier = models.CharField(max_length=50)
    ordered_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def create_order(cls, clinic, medication_name, quantity):
        medication = Medication.objects.filter(supplier=clinic, name=medication_name).first()

        if medication is None:
            raise ValueError('The medication is not available at the passed clinic.')

        if medication.quantity < quantity:
            raise ValueError('There is not enough medication available to fulfill the order.')

        order = cls.objects.create(
            medication=medication,
            quantity=quantity,
            unit_price=medication.unit_price,
            supplier=medication.supplier
        )

        delivery = Delivery.objects.create(
            medication=medication,
            order=order,
            quantity=order.quantity,
            unit_price=order.unit_price
        )

        medication.quantity -= delivery.quantity
        medication.save()

        return order

class Delivery(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    received_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.medication} order -{self.order} unit price - {self.unit_price}'


class Treatment(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    dosage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE,related_name='staff_treatment')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE,related_name='clinic_treatment')

    def __str__(self):
        return f'{self.medication}  ({self.dosage})'
    
    def get_duration(self):
        return self.end_date - self.start_date

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be greater than start date.")

    def create_prescription(self):
        # Generate a default prescription object for this treatment
        dosage = self.dosage
        duration = self.get_duration()
        prescription = Prescription.objects.create(
            treatment=self,
            dosage=dosage,
            duration=duration,
        )
        return prescription

class Prescription(Treatment):
    appointments = models.ManyToManyField(Appointment, related_name='appointment_prescription')
    medical_records = models.ManyToManyField('MedicalRecord', related_name='medical_records_prescription')
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE,related_name='treatment_prescription')
    duration = models.DurationField()
    refill_quantity = models.PositiveIntegerField(default=0)
    refillable = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.appointments} refillable - ({self.refillable})'


class PrescriptionRefill(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_prescription_refill')
    date_requested = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='PENDING')
    
    def __str__(self):
        return f'{self.prescription} status ({self.status})'
    
    @property
    def remaining_refills(self):
        return self.prescription.refill_quantity - self.prescription.refill_requests.count()

class PrescriptionRefillRequest(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='refill_requests')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,related_name='patient_prescription_refill_requests')
    date_requested = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='PENDING')
    
    def __str__(self):
        return f'{self.prescription} status({self.status})'

class RefillApprovalWorkflow:
    log_models = ['prescriptionrefillrequest']

    @fsm_log_by
    class States:
        PENDING = 1
        APPROVED = 2
        DENIED = 3

    class Meta:
        verbose_name = 'Refill Approval Workflow'

    state = FSMIntegerField(default=States.PENDING, choices=States)
    last_transition_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='+')

    @transition(field=state, source=States.PENDING, target=States.APPROVED)
    def approve(self, user):
        self.last_transition_user = user

    @transition(field=state, source=States.PENDING, target=States.DENIED)
    def deny(self, user):
        self.last_transition_user = user

@receiver(pre_save, sender=Prescription)
def refill_limitations(sender, instance, **kwargs):
    if instance.refill_quantity == 0:
        instance.refillable = False
    elif instance.refill_requests.count() >= instance.refill_quantity:
        instance.refillable = False


    
class MedicalRecord(models.Model):
    """
    Medical record model
    """
    clinic:Clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE, related_name='clinic_medicalrecord', related_query_name='clinic_medicalrecord',blank=True,null=True)
    patient: Union[Patient, User] = models.ForeignKey(Patient, on_delete=models.CASCADE)
    staff: Staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    visit_reason = models.CharField(max_length=100)
    created_at: datetime = models.DateTimeField(default=timezone.now) # auto-populate with creation time
    updated_at: datetime = models.DateTimeField(auto_now=True) # auto-populate with update time

    def __str__(self):
        return f'{self.staff} - {self.patient} - {self.created_at}'

    
    @staticmethod
    def get_records_for_patient(patient: Patient) -> List['MedicalRecord']:
        """
        Retrieve the records for a given patient
        """
        return MedicalRecord.objects.filter(patient=patient).order_by('-created_at')

    @staticmethod
    def get_records_for_staff(staff: Staff) -> List['MedicalRecord']:
        """
        Retrieve the records for a given staff
        """
        return MedicalRecord.objects.filter(staff=staff).order_by('-created_at')

    @staticmethod
    def get_records_for_appointment(appointment: Appointment) -> List['MedicalRecord']:
        """
        Retrieve the records for a given appointment
        """
        return MedicalRecord.objects.filter(appointment=appointment).order_by('-created_at')

    @staticmethod
    def create_new_record(patient: Patient, staff: Staff, clinic: Clinic, appointment : Appointment, visit_reason: str) -> 'MedicalRecord':
        """
        Method to create a new medical record

        Args:
        - patient (Patient): The patient who attended the appointment
        - staff (Staff): The staff who attended the appointment
        - clinic (Clinic): The clinic center,
        - appointment (appointment): The appointment,
        - visit_reason (str): The visit reason
        """
        record = MedicalRecord(
            patient=patient,
            staff=staff,
            clinic=clinic,
            appointment=appointment,
            visit_reason=visit_reason
        )
        record.save()
        return record

    def get_absolute_url(self) -> str:
        """
        Retrieve url
        """
        return reverse('medical-record-detail', kwargs={'pk': self.pk})

    

    def get_medication_list(self) -> List[str]:
        """
        Retrieve the list of medication
        """
        return [med.strip() for med in self.medication.split(',')]


class Escalation(models.Model):
    ESCALATION_TYPES = (
        ('EMERGENCY', 'Emergency'),
        ('URGENT', 'Urgent'),
        ('ROUTINE', 'Routine'),
    )

    ESCALATION_STATUSES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    )

    date = models.DateTimeField(default=timezone.now)
    treating_staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, null=True, blank=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    escalation_type = models.CharField(max_length=50, choices=ESCALATION_TYPES, default='ROUTINE')
    escalation_status = models.CharField(max_length=50, choices=ESCALATION_STATUSES, default='PENDING')
    escalation_reason = models.CharField(max_length=100, default='')

    def __str__(self):
        return f'{self.escalation_type} escalation_status({self.escalation_status})'