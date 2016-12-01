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
            # The test environment unfortunately requires special handling
            if name == "mote.tests":
                pth = os.path.join(os.path.dirname(mod.__file__), "mote", "projects")
            else:
                pth = os.path.join(os.path.dirname(mod.__file__), "..", "mote", "projects")
            if os.path.exists(pth):
                for id in os.listdir(pth):
                    if not id.startswith("."):
                        PROJECT_PATHS[id] = pth
