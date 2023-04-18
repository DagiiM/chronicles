from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['127.0.0.1']
CSRF_TRUSTED_ORIGINS = []
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_SUBJECT_PREFIX = config('EMAIL_SUBJECT_PREFIX')
EMAIL_USE_REMEMBER_ME = config('EMAIL_USE_REMEMBER_ME', default=True, cast=bool)
EMAIL_SUPPORT = config('EMAIL_SUPPORT')

APP_DOMAIN = config('APP_DOMAIN', default='eleso.ltd') 
APP_NAME = config('APP_NAME', default='Eleso Ltd')
APP_TAGLINE = config('APP_TAGLINE')

# GOOGLE_API_MAP
GDAL_LIBRARY_PATH = '/usr/lib/libgdal.so'

# Redis configuration
REDIS_HOST = config('REDIS_HOST', default='127.0.0.1')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
REDIS_DB = config('REDIS_DB', default=0, cast=int)

# Cache configuration
CACHE_TTL = config('CACHE_TTL', default=300, cast=int)


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.cache': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

CACHE_TTL = 60 * 5  # cache for 5 minutes


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR /'static'
STATICFILES_DIRS = [
    'app/static',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
