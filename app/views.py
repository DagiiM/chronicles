from rest_framework import permissions, viewsets
from .pagination import CustomPagination

class BaseViewSet(viewsets.ModelViewSet):
    """
    A base viewset that provides default queryset, serializer_class, and pagination_class.
    """
    serializer_class = None
    pagination_class = CustomPagination
    ordering = '-pk'

    def get_queryset(self):
        """
        Returns the queryset that should be used for list views.
        """
        model = self.serializer_class.Meta.model
        return model.objects.all().order_by(self.ordering)

    def get_serializer_context(self):
        """
        Returns the context dictionary that should be passed to the serializer.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        """
        Returns the serializer class that should be used for the request.
        """
        if self.action == 'list':
            return self.serializer_class
        return self.serializer_class

def allow_any(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.request.method == 'POST':
            self.permission_classes = [permissions.AllowAny]
        return func(*args, **kwargs)
    return wrapper

