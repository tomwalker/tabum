from .base import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'tabum_django_db',

        'USER': 'tabum_django',
        'PASSWORD': 'noyahun',
        'HOST': 'localhost',
        'PORT': '5432',     
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = "1234567890abcdefghijklmnopqrstuvwxyz"

# MIDDLEWARE_CLASSES += \
#("debug_toolbar.middleware.DebugToolbarMiddleware", )

# Celery related
import djcelery
djcelery.setup_loader()

INSTALLED_APPS += (
    'djcelery',
)

# CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ("core.tasks", )
# CELERY_ALWAYS_EAGER = True

# should have strong user + pass for
# production


BROKER_VHOST = "myvhost"
BROKER_URL = "amqp://guest:guest@localhost:5672//"

CELERY_IGNORE_RESULT = True
