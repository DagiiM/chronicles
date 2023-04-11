from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Prefetch
from django.utils import timezone
from django.db import models
from app.models import Searchable
from authentication.models import User
from clinics.models import Clinic, AppointmentType, Staff
from .chatgpt import generate_text
from clinics.enums import Status
from django.db.models.signals import post_save
from django.dispatch import receiver


class ConsultationManager(models.Manager):
    def create_consultation(self, sender, content, staff=3, appointment_type='Virtual Consultation'):
        # validate clinic and appointment type exist in the database
        appointment_type_obj = AppointmentType.objects.get(name=appointment_type)
        if appointment_type_obj.name.lower() != 'virtual consultation':
            raise ValueError('Appointment type must be virtual consultation')

        # check if sender and recipient are the same user
        if sender == staff.user:
            raise ValueError('Sender and staff cannot be the same user')

        # check if recipient is valid
        recipient = staff.user
        if ('chatgpt' in recipient.first_name.lower() or 'chatgpt' in recipient.last_name.lower() or 'chatgpt' in recipient.username.lower()) and staff.is_valid_recipient():
            # create consultation
            notification = self.create(sender=sender, recipient=recipient, content=content, status='pending')
        else:
            raise ValueError('Recipient is not valid')

        return notification


class Consultation(Searchable):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_consultations')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_consultations')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')), default='pending')

    objects = ConsultationManager()

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


@receiver(post_save, sender=Consultation)
def send_request_to_chatgpt(sender, instance, created, **kwargs):
    if created and ('chatgpt' in instance.recipient.first_name.lower() or 'chatgpt' in instance.recipient.last_name.lower() or 'chatgpt' in instance.recipient.username.lower()):
        # set content as prompt and send request to chatgpt
        prompt = instance.content
        # code to send request to chatgpt with prompt as input and get response as output
        response = generate_text(prompt)
        content = response
        # save consultation response
        Consultation.objects.create(sender=instance.recipient, recipient=instance.sender, content=content, status='pending')
