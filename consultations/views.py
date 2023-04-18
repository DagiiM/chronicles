from app.views import BaseViewSet
from .serializers import ConsultationSerializer
from authentication.models import User
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

class ConsultationViewSet(BaseViewSet):
    serializer_class = ConsultationSerializer
    ordering = 'pk'
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # get the existing queryset
        queryset = super().get_queryset()

        # filter consultations where recipient and sender are the currently logged-in user
        user = self.request.user
        
        queryset = queryset.filter(Q(sender=user)|Q(recipient=user))

        return queryset
    
    def create(self, request, *args, **kwargs):
        sender = self.request.user
        # check if request has bot:true
        if request.data.get('bot') == 'true':
            # retrieve staff user with specified details
            staff_user = self.get_staff_user()
            if not staff_user:
                # handle case when staff user is not found
                return Response({"message": "Staff user not found."}, status=status.HTTP_404_NOT_FOUND)

            # set recipient field of Consultation object to staff user
            consultation_data = request.data.copy()
            consultation_data['recipient'] = staff_user.id
            consultation_data['sender'] = sender.pk
            serializer = self.serializer_class(data=consultation_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            # handle case when request does not have bot:true
            return Response({"message": "Bot not enabled."}, status=status.HTTP_400_BAD_REQUEST)

    def get_staff_user(self):
        try:
            return User.objects.get(
                Q(first_name__icontains='chatgpt') | 
                Q(last_name__icontains='chatgpt') |
                Q(username__icontains='chatgpt'),
                is_staff=True  # filter only staff users
            )
        except User.DoesNotExist:
            return None
