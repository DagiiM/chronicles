from django.db import models
from typing import List, Type, TypeVar, Union
from django.db.models import QuerySet
from django.db.models import Q
from rest_framework import serializers

M = TypeVar('M', bound='Model')
S = TypeVar('S', bound=serializers.BaseSerializer)

class Searchable(models.Model):
    """
    A model mixin that provides search functionality.
    """
    class Meta:
        abstract = True

    fields_to_return: List[str] = []

    @classmethod
    def search_queryset(cls: Type[M], query: str, fields: List[str] = None, serializer_class_: Type[S] = None) -> Union[QuerySet[M], List[dict]]:
        """
        Search the model queryset for the given query and serialize the results using the specified serializer.
        """
        if not isinstance(query, str):
            raise serializers.ValidationError(f"{cls.__name__}.search_queryset() expected a string query but got {type(query).__name__}")
        if fields and not all(isinstance(field, str) for field in fields):
            raise serializers.ValidationError(f"{cls.__name__}.search_queryset() expected a list of strings for fields but got {type(fields).__name__}")
        if not serializer_class_:
            raise serializers.ValidationError(f"{cls.__name__}.search_queryset() expected a serializer class but none was provided")
        search_fields = getattr(cls.Meta, 'search_fields', None)
        if not search_fields:
            search_fields = cls.get_search_fields()
        if not search_fields:
            raise serializers.ValidationError('No search fields specified.')
        q_objects = Q()
        for field_name in search_fields:
            q_objects |= Q(**{f'{field_name}__icontains': query})
        queryset: QuerySet[M] = cls.objects.filter(q_objects)
        if not isinstance(queryset, QuerySet):
            raise serializers.ValidationError(f"{cls.__name__}.search_queryset() expected a QuerySet but got {type(queryset).__name__}")
        if not issubclass(serializer_class_, serializers.BaseSerializer):
            raise serializers.ValidationError(f"{cls.__name__}.search_queryset() expected a serializer class but got {type(serializer_class_).__name__}")
        serializer_class_.Meta.fields = fields or cls.fields_to_return
        serializer = serializer_class_(queryset, many=True)
        return serializer.data


    @classmethod
    def get_search_fields(cls) -> List[str]:
        """
        Return the list of fields to be searched.
        """
        search_fields = getattr(cls.Meta, 'search_fields', [])
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, str) and attr in cls.__dict__:
                search_fields.append(attr)
        if not search_fields:
            raise AttributeError(f"No search fields specified for {cls.__name__}")
        return search_fields

