from .base import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': 'tabum_test_db',

        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',     
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'


