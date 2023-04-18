from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from .models import NotificationModel


class Command(BaseCommand):
    help = 'Deletes expired notifications'

    def handle(self, *args, **options):
        # Calculate the current datetime
        now = datetime.now()

        # Find all notifications that have an expiration date less than or equal to the current datetime
        expired_notifications = NotificationModel.objects.filter(expiration_date__lte=now)

        # Delete the expired notifications
        expired_notifications.delete()

        # Print a message indicating how many notifications were deleted
        num_deleted = len(expired_notifications)
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {num_deleted} expired notifications.'))


"""
set the following in the configuration, crontab file to run at midnight every day
0 0 * * * /path/to/python /path/to/manage.py delete_expired_notifications
"""