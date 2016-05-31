from __future__ import unicode_literals

try:
    from os import scandir
except ImportError:
    from scandir import scandir

import os.path


class Pattern(object):
    pattern_types = [
        "atoms", "molecules",
        "organisms", "pages", "templates"
    ]

    def __init__(self, path, aspect, kind, name):
        self.path = path
        self.aspect = aspect
        self.kind = kind
        self.name = name

    def render(self):
        pass

    def index(self):
        pass

    def mock_data(self):
        pass

    def changelog(self):
        pass

    def __repr__(self):
        return "<Pattern path={0}, kind={1}".format(self.path, self.kind)

    @classmethod
    def _get_element_path(cls, path, kind, aspect):
        """Return the expected absolute path based on the element kind."""
        if kind in cls.pattern_types:
            return os.path.join(path, aspect, "src/patterns", kind)
        return path

    @classmethod
    def discover(cls, path, kind, aspect=None):
        element_path = cls._get_element_path(path, kind, aspect)
        for entry in scandir(element_path):
            if entry.is_dir() and not entry.name.startswith("."):
                yield Pattern(entry.path, aspect, kind, entry.name)
