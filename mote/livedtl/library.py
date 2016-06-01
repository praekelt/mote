from __future__ import unicode_literals

try:
    from os import scandir
except ImportError:
    from scandir import scandir

from collections import OrderedDict
import os.path

from django.conf import settings
from django.template import engines, TemplateDoesNotExist
from django.utils.functional import cached_property
import ujson as json


class Node(object):
    index_template = "index.html"
    element_template = "element.html"

    def __init__(self, element, name):
        self.element = element
        self.name = name
        self._metadata = {}
        self._json_files = {}

        # Load metadata in memory because it is never large
        path = os.path.join(self.path, "metadata.json")
        if os.path.exists(path):
            fp = open(path, "r")
            try:
                self._metadata = json.load(fp)
            finally:
                fp.close()

    def __repr__(self):
        return "<Node element={0}, name={1}>".format(
            self.element.kind, self.name
        )

    def get_index_template(self):
        #index_path = os.path.join(self.relative_path, self.index_template)
        #return [index_path, "element/index.html"]
        return ["element/index.html"]

    def get_element_template(self):
        element_path = os.path.join(self.relative_path, self.element_template)
        return element_path

    def get_context(self):
        base = {"element": self}
        if self.element.aspect.extra_context is not None:
            base.update(self.element.aspect.extra_context)
        return base

    def render(self):
        template = self.element.engine.get_template(
            self.get_element_template()
        )
        return template.render(self.get_context())

    def index(self):
        template = self.element.select_template(
            self.get_index_template()
        )
        return template.render(self.get_context())

    @property
    def path(self):
        """Return the expected absolute path."""
        return os.path.join(
            self.element.path,
            self.name
        )

    @property
    def relative_path(self):
        """Return the relative path to this element based on the configured
        REPOSITORY_BASE_DIR settings.
        """
        # Ensure that REPOSITORY_BASE_DIR has a trailing slash before split.
        repo_base = os.path.join(settings.REPOSITORY_BASE_DIR, "")
        return self.path.split(repo_base)[1]

    @property
    def json_files(self):
        if not self._json_files:
            json_path = os.path.join(self.path, "json")
            if os.path.exists(json_path):
                for entry in scandir(json_path):
                    if entry.is_file() and entry.name.endswith(".json"):
                        self._json_files[entry.name[:-5]] = entry.path
        return self._json_files

    @property
    def id(self):
        return self.name

    @property
    def metadata(self):
        return self._metadata

    @property
    def title(self):
        return self.metadata.get("title", self.id)

    @property
    def description(self):
        return self.metadata.get("description", None)

    @cached_property
    def json(self):
        result = {}
        for name, path in self.json_files.items():
            with open(path, "r") as fp:
                try:
                    parsed = json.load(fp)
                except ValueError:
                    raise ValueError("Invalid JSON at {0}".format(path))
                result[name] = parsed

        return result


class Element(object):
    template_engine = "django"

    def __init__(self, aspect, kind):
        self.aspect = aspect
        self.kind = kind
        self.elements = None
        self._renderer = None

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
        """Return the expected absolute path."""
        return os.path.join(
            self.aspect.path,
            "src/patterns",
            self.kind
        )

    @property
    def engine(self):
        return engines[self.template_engine]

    def select_template(self, template_name_list):
        chain = []
        for template_name in template_name_list:
                try:
                    return self.engine.get_template(template_name)
                except TemplateDoesNotExist as e:
                    chain.append(e)

        if template_name_list:
            raise TemplateDoesNotExist(
                ", ".join(template_name_list), chain=chain
            )
        else:
            raise TemplateDoesNotExist("No template names provided")

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
    reserved_names = ["templates"]

    def __init__(self, name, path, extra_context=None):
        self.name = name
        self.path = path
        self.extra_context = extra_context

    def __repr__(self):
        return "<Aspect name={0}, path={1}>".format(self.name, self.path)

    def __getattr__(self, name):
        if name in self.kinds:
            return Element(self, name)

        msg = "'{0}' object has no attribute '{1}'".format(
            self.__class__.__name__, name
        )
        raise AttributeError(msg)

    @property
    def root_path(self):
        return os.path.abspath(os.path.join(self.path, os.path.pardir))

    @classmethod
    def discover(cls, path):
        """Discover what aspects if any this repo provides."""
        aspects = []
        if os.path.exists(path):
            for entry in scandir(path):
                if (entry.is_dir() and not entry.name.startswith(".") and
                        entry.name not in cls.reserved_names):
                    aspects.append(cls(entry.name, entry.path))

        return aspects

    @classmethod
    def get(cls, name, path, extra_context=None):
        """Get an Aspect by name."""
        path = os.path.join(path, name)
        if os.path.exists(path):
            return cls(name, path, extra_context)

        return None
