from __future__ import unicode_literals

try:
    from os import scandir
except ImportError:
    from scandir import scandir

from collections import OrderedDict
import os.path


class Node(object):

    def __init__(self, element, name):
        self.element = element
        self.name = name

    def __repr__(self):
        return "<Node element={0}, name={1}>".format(
            self.element.kind, self.name
        )


class Element(object):

    def __init__(self, aspect, kind):
        self.aspect = aspect
        self.kind = kind
        self.elements = None

    def __repr__(self):
        return "<Element aspect={0}, kind={1}>".format(
            self.aspect.name, self.kind
        )

    def __iter__(self):
        """Return an iterator of all nodes for this element kind and aspect."""
        if self.elements is None:
            self.discover()
        return self.elements.itervalues()

    def __getattr__(self, name):
        """Directly get node by name."""
        if self.elements is None:
            self.discover()

        if name in self.elements:
            return self.elements[name]

        msg = "No element named '{0}' found in current Aspect.".format(name)
        raise AttributeError(msg)

    @property
    def path(self):
        """Return the expected absolute path based for the element kind."""
        return os.path.join(
            self.aspect.path,
            self.aspect.name,
            "src/patterns",
            self.kind
        )

    def discover(self):
        """Discover elements of this kind."""
        path = self.path

        nodes = OrderedDict()
        if os.path.exists(path):
            for entry in scandir(path):
                if entry.is_dir() and not entry.name.startswith("."):
                    nodes[entry.name] = Node(self, entry.name)
        self.elements = nodes

    def all(self):
        """Return all the elements of this kind for the given Aspect."""
        # This is the same as iterating on the object itself, so this
        # method is provided just for clarity.
        if self.elements is None:
            self.discover()

        return self.elements.itervalues()


class Aspect(object):
    kinds = [
        "atoms", "molecules",
        "organisms", "pages", "templates"
    ]

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __repr__(self):
        return "<Aspect name={0}, path={1}>".format(self.name, self.path)

    def __getattr__(self, name):
        if name in self.kinds:
            return Element(self, name)

        msg = "'{0}' object has no attribute '{1}'".format(
            self.__class__.__name__, name
        )
        raise AttributeError(msg)

    @classmethod
    def discover(cls, path):
        """Discover what aspects if any this repo provides."""

        aspects = []
        if os.path.exists(path):
            for entry in scandir(path):
                if entry.is_dir() and not entry.name.startswith("."):
                    aspects.append(cls(entry.name, entry.path))

        return aspects
