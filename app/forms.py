from django import forms
from .exceptions import ErrorResponse

class BaseForm(forms.Form):
    """
    A base form that handles errors in a standard format.
    """
    error_css_class = 'error'
    required_css_class = 'required'

    def add_error(self, field, error):
        """
        Adds an error message to the specified field in the standard format.
        """
        if not field:
            field = forms.forms.NON_FIELD_ERRORS

        if field not in self.errors:
            self.errors[field] = []

        # Override the error message
        self.errors[field].append('An error occurred')

    def handle_errors(self):
        """
        Handles errors in the standard format.
        """
        if self.errors:
            errors = []
            for field, field_errors in self.errors.items():
                for field_error in field_errors:
                    errors.append({'message': field_error, 'status': 400})

            raise ErrorResponse.custom_validation_error(errors=errors)
