import json
from datetime import timedelta
from django.utils import timezone
from typing import Dict, List, Union
from django.core.mail import send_mail
from django.db import models
from authentication.models import User
from app.models import Searchable
from .enums import NotificationPreference,NotificationType
from .channels import send_email_notification, send_sms_notification


class Notification(Searchable):
    """
    A model for storing notifications and sending them to users based on their notification preferences.

    Attributes:
        notification_type (str): The type of the notification. Should be one of the NotificationType choices.
        notification_preference (List[str]): A list of the user's preferred notification methods.
            Should be a combination of NotificationPreference choices.
        body (str): The main content of the notification message.
        subject (str): A brief summary or title of the notification.
        sender (str): The user or system that initiated the notification.
        recipients (ManyToManyField): The users who should receive the notification.
        importance_level (int): An indication of the urgency or importance of the notification.
        related_object (str): A reference to the object or entity that the notification pertains to.
        date_created (datetime): The date and time when the notification was created.
        date_sent (datetime): The date and time when the notification was sent.
        date_read (datetime): The date and time when the notification was read by the recipient.
        expiration_date (datetime): The date and time when the notification should expire and no longer be relevant.

    Methods:
        send_notification(): Sends the notification to the user based on their preferred notification methods.
        mark_as_read(): Marks the notification as read.
        is_expired(): Checks if the notification has expired.
        is_urgent(): Checks if the notification is considered urgent based on its importance level.
    """

    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    sender = models.CharField(max_length=255)
    recipients = models.ManyToManyField(User, related_name='notifications_received')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    importance_level = models.IntegerField()
    related_object = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_sent = models.DateTimeField(default=timezone.now)
    date_read = models.DateTimeField(null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    #search_fields = ['subject','body']
    fields_to_return = ['subject','body']
    
    def save(self, *args, **kwargs):
        if self.date_sent:
            self.expiration_date = self.date_sent + timedelta(days=30)
        super(Notification, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.subject + '. sender-' + self.sender
    
    class Meta:
        verbose_name_plural = 'notifications'

    def send_database_notification(self, recipient: User) -> None:
        """
        Saves the notification to the database for a specific recipient.
        """
        self.recipients.set([recipient])
        self.save()

    def send_notification(self) -> None:
        """
        Sends the notification to the recipients based on their preferred notification methods.
        """
        for recipient in self.recipients.all():
            for preference in recipient.notification_preference:
                if preference == NotificationPreference.DATABASE:
                    self.send_database_notification(recipient)
                elif preference == NotificationPreference.EMAIL:
                    self.send_email_notification(recipient)
                elif preference == NotificationPreference.SMS:
                    self.send_sms_notification(recipient)
                    
    def notify(subject: str, body: str, recipients: Union[User, List[User]], 
            sender: str = 'System', important_level: int = 1) -> None:
        """
        Notifies users about a new clinic.

        Args:
            subject (str): The subject.
            body (str): The body.
            recipients (Union[User, List[User]]): A single user or list of users to notify.
            sender (str, optional): The name of the sender. Defaults to 'System'.
            important_level (int, optional): The level of the message
        """

        if isinstance(recipients, list):
            preference = [NotificationPreference.EMAIL, NotificationPreference.SMS]
            for recipient in recipients:
                notification = Notification.objects.create(
                    notification_type=NotificationType.INFO,
                    body=body,
                    subject=subject,
                    sender=sender,
                    importance_level=important_level,
                )
                notification.recipients.set([recipient])
                notification.send_notification()
        else:
            preference = recipients.notification_preference
            notification = Notification.objects.create(
                notification_type=NotificationType.INFO,
                body=body,
                subject=subject,
                sender=sender,
                importance_level=important_level,
            )
            notification.recipients.set([recipients])
            notification.send_notification()

            
    def mark_as_read(self) -> None:
        """
        Marks the notification as read.
        """
        self.date_read = timezone.now()
        self.save()

    def is_expired(self) -> bool:
        """
        Checks if the notification has expired.
        """
        if self.expiration_date is not None:
            return timezone.now() > self.expiration_date
        else:
            return False

    def is_urgent(self) -> bool:
        """
        Checks if the notification is considered urgent based on its importance level.
        """
        return self.importance


