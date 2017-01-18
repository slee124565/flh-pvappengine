"""
Django settings for pvappengine project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os, sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r^ek_^swu&o*_28a%gwn*1x5de8*o^kwhzl^yfv!1qu@6_sz_='

# SECURITY WARNING: don't run with debug turned on in production!
if sys.platform == 'darwin':
    DEBUG = True
else:
    DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'dbconfig.apps.DbconfigConfig',
    'pvi.apps.PviConfig',
    'accuweather.apps.AccuweatherConfig',
    'wordpress.apps.WordpressConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pvappengine.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR,'templates'),
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pvappengine.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

if sys.platform == 'darwin':
    # on MAC
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'pvs',
            'HOST': 'localhost',
            'USER': 'root',
            'PASSWORD': '',
        }
    }
else: # linux
    # on Pi
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'raspi',
            'HOST': 'localhost',
            'USER': 'raspi',
            'PASSWORD': 'WeKtqjUtGExPnDYt',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static/')
STATICFILES_DIRS = [
                    ("bower_components", os.path.join(BASE_DIR,"ngapp","bower_components")),
                    ("styles", os.path.join(BASE_DIR,"ngapp","app","styles")),
                    ("scripts", os.path.join(BASE_DIR,"ngapp","app","scripts")),
                    ("images", os.path.join(BASE_DIR,"ngapp","app","images")),
                    ]

LOGGING = {
    'version': 1,              
    'disable_existing_loggers': False,  # this fixes the problem

    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR,'logs/pvappengine.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },  
        'request_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR,'logs/django_request.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
    },
    'root': {
        'handlers': ['default'],
        'level': 'DEBUG'
    },
    'loggers': {
        'pvi': {
            'handlers': ['console','default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'accuweather': {
            'handlers': ['console','default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'pvappengine': {
            'handlers': ['console','default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

import serial
PVS_CONFIG = {
              'pvs' : [
                       {
                        'name': 'H5',
                        'type': 'DELTA_PRI_H5', #-> refer to pvi.PVI_TYPE_LIST
                        'modbus_id': 2, #-> pvi modbus address
                        'serial': {
                                   'port': '/dev/ttyUSB0',
                                   'baudrate': 9600,
                                   'bytesize': 8,
                                   'parity': serial.PARITY_NONE,
                                   'stopbits': 1,
                                   'timeout': 0.1,
                                   }
                        },
                       ],
              'kWh_carbon_save_unit_kg': 0.637,
              'kWh_income_unit_ntd': 6.8633,
              'accuweather': {
                              'apikey': 'ff1b463d98fb47af848ea2843ec5c925',
                              #-> get location key by geo 
                              #-> http://127.0.0.1:8000/appeng/accu/key_geo_search/?q=25.1058006,121.5198715
                              'locationkey': '2516626', 
                              #'locationkey': '701769', #-> Taipei
                              },
              }


