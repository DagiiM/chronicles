from django.http import JsonResponse
from rest_framework.views import exception_handler
import json

class ErrorResponse(Exception):
    """
    A standard error response format.
    """
    def __init__(self, message, status_code):
        self.errors = [{"message": message, "status": status_code}]
        self.status_code = status_code

    @classmethod
    def custom_validation_error(cls, message:str,status_code:int):
        return cls(message=message, status_code=status_code)

    def to_dict(self):
        return {"errors": self.errors}

    def to_json(self):
        return json.dumps(self.to_dict())

def my_exception_handler(exc, context):
    if isinstance(exc, ErrorResponse):
        return JsonResponse(exc.to_dict(), status=exc.status_code)
    else:
        # Call REST framework's default exception handler
        response = exception_handler(exc, context)

        if response is not None:
            return response

        # Handle other exceptions here
        # ...

        # Return a default error response
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
