from typing import List, Type, TypeVar, Union
from django.db.models import Model, QuerySet, Q
from functools import reduce
import operator
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.core.cache import cache
import re
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.response import Response
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.contrib import admin
from django.contrib.auth.models import Group

class CustomPagination(PageNumberPagination):
    page_size = int(settings.PAGE_SIZE)
    page_size_query_param = 'page_size'
    max_page_size = int(settings.MAX_PAGE_SIZE)

    def get_timeout(self, request):
        """
        Returns the cache timeout for the paginated results.
        """
        if request.method == 'GET':
            return 60 * 5  # 5 minutes
        else:
            return 0  # Don't cache non-GET requests

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate the queryset and cache the results.
        """
        self.request = request  # store the request object as an instance variable

        if self.page_size_query_param:
            self.page_size = self.get_page_size(request)

            if self.page_size_query_param in request.query_params:
                try:
                    self.page_size = int(request.query_params[self.page_size_query_param])
                except ValueError:
                    pass

        paginator = self.django_paginator_class(queryset, self.page_size)

        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True

        paginated_queryset = list(page)

        # Cache the paginated queryset
        cache_prefix = f"{self.__class__.__name__}_"
        cache_key = f"{cache_prefix}{request.path}_page{page.number}"
        cache.set(cache_key, paginated_queryset, timeout=self.get_timeout(request))

        self.page = page  # Store the current page for use in get_paginated_response()

        return paginated_queryset

    def get_paginated_response(self, data):
        """
        Return a response object including the paginated results and cache information.
        """
        assert self.page is not None

        # Get the URLs for the previous and next pages
        if self.page.has_previous():
            previous_url = self.get_previous_link()
        else:
            previous_url = None

        if self.page.has_next():
            next_url = self.get_next_link()
        else:
            next_url = None

        # Build the response data
        response_data = {
            'count': self.page.paginator.count,
            'next': next_url,
            'previous': previous_url,
            'results': data
        }

        # Add cache information to the response headers
        cache_prefix = f"{self.__class__.__name__}_"
        cache_key = f"{cache_prefix}{self.request.path}_page{self.page.number}"
        timeout = cache.ttl(cache_key)
        if timeout is None:
            timeout = self.get_timeout(self.request)
        cache_timeout_header = f"max-age={timeout}"
        cache_key_header = f"{cache_prefix}{self.request.path}"
        headers = {
            'Cache-Control': cache_timeout_header,
            'X-Cache-Key': cache_key_header,
        }

        return Response(response_data, headers=headers)

