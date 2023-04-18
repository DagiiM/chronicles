from django.utils import timezone
from app.views import BaseViewSet
from .serializers import NotificationSerializer 
from .models import Notification
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

class NotificationViewSet(BaseViewSet):
    serializer_class = NotificationSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(recipients=self.request.user.pk)
        return queryset

    @action(detail=True, methods=['post'], name='Mark as Read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], name='Mark All as Read')
    def mark_all_as_read(self, request):
        self.get_queryset().filter(date_read=None).update(date_read=timezone.now())
        return Response({'message': 'All notifications marked as read.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], name='Read Notification')
    def read_notifications(self, request):
        notifications = self.get_queryset().filter(date_read__isnull=False)
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = NotificationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], name='Unread Notification')
    def unread_notifications(self, request):
        notifications = self.get_queryset().filter(date_read__isnull=True)
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = NotificationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], name='Mark as Unread')
    def mark_as_unread(self, request, pk=None):
        notification = self.get_object()
        notification.date_read = None
        notification.save()
        return Response({'message': 'Notification marked as unread.'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['get'])
    def is_expired(self, request, pk=None):
        notification = self.get_object()
        is_expired = notification.is_expired()
        return Response({'is_expired': is_expired})

    @action(detail=True, methods=['get'])
    def is_urgent(self, request, pk=None):
        notification = self.get_object()
        is_urgent = notification.is_urgent()
        return Response({'is_urgent': is_urgent})

    @action(detail=False, methods=['post'])
    def notify(self, request):
        """
        Notifies users about a new clinic.

        Args:
            subject (str): The subject.
            body (str): The body.
            recipients (Union[User, List[User]]): A single user or list of users to notify.
            sender (str, optional): The name of the sender. Defaults to 'System'.
            important_level:integer, optional: The level of the message
        """
        subject = request.data.get('subject')
        body = request.data.get('body')
        recipients = request.data.get('recipients')
        sender = request.data.get('sender', 'System')
        important_level = request.data.get('importance_level', 1)

        Notification.notify(subject=subject, body=body, recipients=request.user)
        

        return Response({'message': 'Notification Sent Successfuly.'}, status=status.HTTP_200_OK)