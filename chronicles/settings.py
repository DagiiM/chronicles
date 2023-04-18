from decouple import config

from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
OPENAI_API_KEY = config('OPENAI_API_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', False)

ALLOWED_HOSTS = ['127.0.0.1','172.105.84.246','localhost','eleso.ltd','www.eleso.ltd']
CSRF_TRUSTED_ORIGINS = ['https://172.105.84.246']

#CORS_REPLACE_HTTPS_REFERER = True

#CORS_ALLOW_CREDENTIALS = True

AUTH_USER_MODEL = 'authentication.User'
# Application definition

INSTALLED_APPS = [
    'app.apps.MyAdminConfig',
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'formtools',
    'authentication',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',
    'clinics',
    'mapwidgets',
    'django_google_maps',
    'django_countries',
    'client',
    'notifications',
    'about',
    'pharmacy',
    'consultations',
    'ckeditor',
    'sslserver',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "corsheaders.middleware.CorsPostCsrfMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'utils.middleware.ErrorHandlerMiddleware',
    #'utils.middleware.my_exception_handler',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    
    'app.middleware.TokenAuthMiddleware',
    
]


CORS_ALLOW_ALL_ORIGINS=False

CORS_ALLOWED_ORIGINS = [
    "https://172.105.84.246:443",
    "https://eleso.ltd:443",
    'https://127.0.0.1:8000',
    'https://127.0.0.1:8005',
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

#CORS_ALLOW_CREDENTIALS=True

#SECURE_SSL_REDIRECT = True
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#HTTPS = True

SECURE_SSL_CERTIFICATE = '/certs/server.crt'
SECURE_SSL_KEY = '/certs/server.key'

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True


ROOT_URLCONF = 'chronicles.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates',],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins':[
               #'my_mapwidgets.templatetags.map_widgets',
            ]
        },
    },
]

WSGI_APPLICATION = 'chronicles.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': f"django.db.backends.{config('DATABASE_ENGINE') or 'sqlite3'}",
        'NAME': config('DATABASE_NAME') or BASE_DIR / 'db.sqlite3',
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST','localhost'),
        'PORT': config('DATABASE_PORT',3306),
    }
}




# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = config('TIME_ZONE', 'UTC')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_URL = 'https://172.105.84.246/static/'
STATIC_ROOT = BASE_DIR /'static'
STATICFILES_DIRS = [
    'chronicles/static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR /'media'

APP_DOMAIN = config('APP_DOMAIN','eleso.ltd') 
APP_NAME = config('APP_NAME','Eleso Ltd')
APP_TAGLINE = config('APP_TAGLINE')

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

PAGE_SIZE =config('PAGE_SIZE')
MAX_PAGE_SIZE = config('MAX_PAGE_SIZE')

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT',587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', True)
#EMAIL_USE_SSL = config('EMAIL_USE_SSL',False)
EMAIL_SUBJECT_PREFIX = config('EMAIL_SUBJECT_PREFIX')
EMAIL_USE_REMEMBER_ME = config('EMAIL_USE_REMEMBER_ME', True)
EMAIL_SUPPORT = config('EMAIL_SUPPORT')

GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        #'rest_framework.authentication.BasicAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
    ],
    #'EXCEPTION_HANDLER': 'app.exceptions.my_exception_handler'
}

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


CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'extraPlugins': 'codesnippet',
        'skin': 'office2013',
        'width': '100%',
    },
}
