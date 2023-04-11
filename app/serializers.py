from typing import List, Union
from django.db.models import Q
from rest_framework import serializers
from django.apps import apps
from .models import Searchable
from django.core.exceptions import ObjectDoesNotExist
import logging
from .exceptions import ErrorResponse
from rest_framework import serializers, status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
)

class BaseSerializer(serializers.ModelSerializer):
    """
    A more robust base serializer that handles exceptions and errors more gracefully.
    """

    logger = logging.getLogger(__name__)

    def to_representation(self, instance):
        try:
            return super().to_representation(instance)
        except ErrorResponse as e:
            message = e.message
            status_code = e.status_code
            error_data = {"errors": [{"message": message, "status": status_code}]}
            raise serializers.ValidationError(error_data, code=status_code)
        except ObjectDoesNotExist as e:
            message = str(e)
            status_code = status.HTTP_409_CONFLICT
            error_data = ErrorResponse(message, status_code)
            raise serializers.ValidationError(error_data.errors, code=status_code)
        except ValueError as e:
            message = str(e)
            status_code = status.HTTP_400_BAD_REQUEST
            error_data = ErrorResponse(message, status_code)
            raise serializers.ValidationError(error_data.errors, code=status_code)
        except TypeError as e:
            message = str(e)
            status_code = status.HTTP_400_BAD_REQUEST
            error_data = ErrorResponse(message, status_code)
            raise serializers.ValidationError(error_data.errors, code=status_code)
        except AuthenticationFailed as e:
            message = str(e)
            status_code = status.HTTP_401_UNAUTHORIZED
            error_data = ErrorResponse(message, status_code)
            raise serializers.ValidationError(error_data, code=status_code)
        except PermissionDenied as e:
            message = str(e)
            status_code = status.HTTP_403_FORBIDDEN
            error_data = ErrorResponse(message, status_code)
            raise serializers.ValidationError(error_data, code=status_code)
        except NotFound as e:
            message = str(e)
            status_code = status.HTTP_404_NOT_FOUND
            error_data = ErrorResponse(message, status_code)
            raise serializers.ValidationError(error_data, code=status_code)
        except APIException as e:
            message = str(e)
            status_code = e.status_code
            error_data = ErrorResponse(message, status_code)
            raise serializers.ValidationError(error_data.errors, code=status_code)
        except Exception as e:
            message = 'An unexpected error occurred during serialization'
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            error_data = ErrorResponse(message, status_code)
            self.logger.exception(message)
            raise serializers.ValidationError(error_data.errors, code=status_code)


class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()

    def create(self, validated_data):
        query = validated_data['query']
        models = self.get_searchable_models()
        results = self.search_models(query, models)
        return results
    
    def search_models(self, query, models):
        results = {}
        for model in models:
            queryset = model.search_queryset(query, serializer_class_=self.get_serializer_class(model))
            if queryset:
                serializer_class = self.get_serializer_class(model)
                if not serializer_class:
                    continue
                serializer = serializer_class(queryset, many=True, context={'query': query})
                results[model.__name__] = serializer.data
        return results


    def get_searchable_models(self):
        """
        Get a list of models that have a `search_queryset` method and inherit from `SearchableMixin`.
        """
        searchable_models = []
        for model in apps.get_models():
            if issubclass(model, Searchable) and hasattr(model, 'search_fields') and hasattr(model, 'fields_to_return'):
                searchable_models.append(model)
        return searchable_models

    def get_serializer_class(self, model):
        fields_to_return = getattr(model, 'fields_to_return', [])
        if fields_to_return:
            class_name = f'{model.__name__}Serializer'
            meta_attrs = {
                'model': model,
                'fields': fields_to_return
            }
            Meta = type('Meta', (object,), meta_attrs)
            attrs = {'Meta': Meta}
            serializer_class = type(class_name, (serializers.ModelSerializer,), attrs)
            return serializer_class

    def to_representation(self, instance):
        return self.search_models(instance['query'], self.get_searchable_models())