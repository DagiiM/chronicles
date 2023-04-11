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

ALLOWED_HOSTS = ['127.0.0.1','eebd-102-212-236-175.ngrok-free.app']
CSRF_TRUSTED_ORIGINS = ['https://eebd-102-212-236-175.ngrok-free.app']

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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'utils.middleware.ErrorHandlerMiddleware',
    #'utils.middleware.my_exception_handler',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'utils.exceptions.CustomValidationErrorHandler',
    #'corsheaders.middleware.CorsMiddleware',
    #'rest_framework_simplejwt.middleware.JWTAuthenticationMiddleware',
    
]

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
