from django.db import models

class NotificationType(models.TextChoices):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    SUCCESS = 'success'
    UPDATE = 'update'


class NotificationPreference(models.TextChoices):
    DATABASE = 'database'
    EMAIL = 'email'
    SMS = 'sms'