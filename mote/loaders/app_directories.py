import os

from django.conf import settings
from django.template.utils import get_app_template_dirs
from django.template.loaders.filesystem import Loader as FilesystemLoader


class Loader(FilesystemLoader):

    def get_dirs(self):
        # Explicitly defined directories
        try:
            dirs = tuple([
                os.path.join(d, "mote", "projects") \
                    for d in settings.MOTE["directories"]
            ])
        except (AttributeError, KeyError):
            dirs = ()

        # App directories. Note the testing environment does not require upward
        # traversal.
        result = dirs + get_app_template_dirs(os.path.join("..", "mote", "projects")) \
            + get_app_template_dirs(os.path.join("mote", "projects"))

        return result
