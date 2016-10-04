import os

from django.template.utils import get_app_template_dirs
from django.template.loaders.filesystem import Loader as FilesystemLoader


class Loader(FilesystemLoader):

    def get_dirs(self):
        return get_app_template_dirs(os.path.join("..", "projects"))
