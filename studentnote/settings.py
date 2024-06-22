"""
Django settings for studentnote project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import dj_database_url
from django.contrib.messages import constants as messages
from pathlib import Path
import environ

import os

#from decouple import config

#import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


env = environ.Env()
environ.Env.read_env(env_file=str(BASE_DIR / "studentnote" / ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG=env.bool("DEBUG")
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')
YOUTUBE_API_KEY = env('YOUTUBE_API_KEY')

# CSRF_TRUSTED_ORIGINS = [
#     'https://6faa-2c0f-f0f8-65a-9940-1e-8360-7c5e-9c83.ngrok-free.app',
# ]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',
    'login',
    'crispy_forms',
    'crispy_bootstrap5',
    'celery'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] 

ROOT_URLCONF = 'studentnote.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'studentnote.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


#Base de donnée initial sqlite3

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

""""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'student_note',
        'USER': 'elmaniora',
        'PASSWORD': 'ivai@2005.',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
"""

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Utilisation de WhiteNoise pour servir les fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

#DATABASES = {
 #   'default':dj_database_url.parse(config('DATABASE_URL'))

#}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field


STATIC_URL = '/static/'
STATICFILES_DIRS=[BASE_DIR/"static"]

# MEDIA

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

# Custom Django auth settings

AUTH_USER_MODEL = "login.UserAccount"

LOGIN_URL = "log:login"

LOGOUT_URL = "logout"

SIGNUP_URL = "log:register"

LOGIN_REDIRECT_URL = "home"

LOGOUT_REDIRECT_URL = "home"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_HOST_USER = env("email")

EMAIL_HOST_PASSWORD = env("em_pass")

EMAIL_PORT = 587


# Messages built-in framework

MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}


# Third party apps configuration

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

PHONENUMBER_DB_FORMAT = "INTERNATIONAL"

PHONENUMBER_DEFAULT_FORMAT = "INTERNATIONAL"

PHONENUMBER_DEFAULT_REGION = "TG"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


if os.environ.get('ENV') == 'PRODUCTION':

    # Static files settings
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

    # Extra places for collectstatic to find static files.
    STATICFILES_DIRS = (
        os.path.join(PROJECT_ROOT, 'static'),
    )

    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    DATABASES = { 'default': dj_database_url.config(conn_max_age=500) }



    # settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Changez selon votre configuration Redis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Utilisé pour stocker les résultats des tâches

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')





# URL de redirection après connexion
LOGIN_REDIRECT_URL = '/'