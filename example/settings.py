import os
import glob
import sys
from os.path import expanduser

if "VIRTUAL_ENV" in os.environ:
    BASE_DIR = os.path.join(
        glob.glob(os.environ["VIRTUAL_ENV"] +  "/lib/*/site-packages")[0],
        "mote"
    )
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = "SECRET_KEY_PLACEHOLDER"

DEBUG = True

TEMPLATE_DEBUG = True

INSTALLED_APPS = [
    "mote.chat",
    "mote",
    "motelibbase",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
]

#if sys.version_info[0] >= 3:
#    INSTALLED_APPS.insert(0, "channels")

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.i18n",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.tz",
    "django.template.context_processors.request",
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

ROOT_URLCONF = "mote.tests.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

USE_TZ = True

STATIC_URL = "/static/"

ALLOWED_HOSTS = ["*"]

ASGI_APPLICATION = "mote.routing.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}

MOTE = {
    "directories": ["/home/hedley/django/instances/mote/mote/tests"],
    "parallel": True
}
