from .base import *

DEBUG = True

# Don't validate password in dev
AUTH_PASSWORD_VALIDATORS = []

CELERY_ALWAYS_EAGER = True
BROKER_TRANSPORT = 'memory'
