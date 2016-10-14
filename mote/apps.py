import os
from importlib import import_module

from django.apps import AppConfig
from django.conf import settings

from mote import PROJECT_PATHS


class MoteConfig(AppConfig):
    name = "mote"
    verbose_name = "Mote"

    def ready(self):
        for name in settings.INSTALLED_APPS:
            mod = import_module(name)
            pth = os.path.join(os.path.dirname(mod.__file__), "..", "mote", "projects")
            if os.path.exists(pth):
                for id in os.listdir(pth):
                    PROJECT_PATHS[id] = pth