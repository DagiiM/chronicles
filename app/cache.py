import json
from typing import Callable, Optional
from django.core.cache import cache
from django.conf import settings
from rest_framework import serializers
redis_host = settings.CACHES['default']['LOCATION']
redis_port = settings.CACHES['default'].get('PORT', 6379)
redis_db = settings.CACHES['default'].get('OPTIONS', {}).get('DB', 0)
cache_timeout = settings.CACHE_TTL

def cache_data(redis_key: str, cache_timeout: Optional[int] = None) -> Callable:
    """
    A decorator function to cache the results of a function using Redis.
    """
    def cache_decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Generate a cache key based on the function name, app name, and its arguments
            cache_key = f"{settings.APP_NAME}-{func.__name__}-{json.dumps(args)}-{json.dumps(kwargs)}-{redis_key}"

            # Check if the cache key exists in Redis
            cached_data = cache.get(cache_key)

            if cached_data:
                # Return the cached data if it exists
                return cached_data
            else:
                # Call the function if the data is not cached
                try:
                    result = func(*args, **kwargs)
                except serializers.ValidationError as e:
                    raise e

                # Store the result in Redis
                cache.set(cache_key, result, timeout=cache_timeout)

                return result
        return wrapper
    return cache_decorator(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db, cache_timeout=cache_timeout)





