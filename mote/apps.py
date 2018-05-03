import logging
import os
from importlib import import_module

from django.apps import AppConfig
from django.conf import settings

from mote import PROJECT_PATHS


logger = logging.getLogger("django")


class MoteConfig(AppConfig):
    name = "mote"
    verbose_name = "Mote"

    def ready(self):
        #import pdb;pdb.set_trace()
        # Iterate over apps
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

        # Iterate over explicitly defined directories
        try:
            directories = settings.MOTE["directories"]
        except (AttributeError, KeyError):
            directories = []
        for directory in directories:
            tokens = os.path.split(directory)
            if tokens[-1] == "mote":
                raise RuntimeError(
                    "Redundant trailing \"mote\" component in %s" % directory
                )
            pth = os.path.join(directory, "mote", "projects")
            if not os.path.exists(pth):
                logger.warn("Can't find a pattern library in %s" % pth)
            else:
                for id in os.listdir(pth):
                    if not id.startswith("."):
                        PROJECT_PATHS[id] = pth
