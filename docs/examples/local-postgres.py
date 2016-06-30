from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mote',
        'USER': 'jason',
        'PASSWORD': '',
    }
}

INSTALLED_APPS = [
    'django_pdb'
] + INSTALLED_APPS

MIDDLEWARE_CLASSES += [
    'django_pdb.middleware.PdbMiddleware'
]

# Don't validate password in dev
AUTH_PASSWORD_VALIDATORS = []

CELERY_ALWAYS_EAGER = True
BROKER_TRANSPORT = 'memory'
