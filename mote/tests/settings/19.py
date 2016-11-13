import os
import glob
from os.path import expanduser


BASE_DIR = os.path.join(
    glob.glob(os.environ["VIRTUAL_ENV"] +  "/lib/*/site-packages")[0],
    "mote"
)

SECRET_KEY = "SECRET_KEY_PLACEHOLDER"

DEBUG = True

TEMPLATE_DEBUG = True

#ALLOWED_HOSTS = []

INSTALLED_APPS = (
    "mote",
    "mote.tests",

    # Django apps can be alphabetic
    #"django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    #"django.contrib.sessions",
    #"django.contrib.sites",
    #"django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
)

'''
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": TEMPLATE_CONTEXT_PROCESSORS,
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "mote.loaders.app_directories.Loader",
                "django.template.loaders.app_directories.Loader",
            ]
        },
    },
]
'''

ROOT_URLCONF = "mote.tests.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

USE_TZ = True

STATIC_URL = "/static/"

#MEDIA_ROOT = "%s/media/" % BASE_DIR
#MEDIA_URL = "/media/"
