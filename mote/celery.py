from __future__ import absolute_import
from __future__ import unicode_literals

import os

from celery import Celery

from django.conf import settings

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "mote.settings.production"
)

app = Celery("mote")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
