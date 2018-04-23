"""Model the elements picked up from the filesystem"""

import hashlib
import json
import os
from collections import OrderedDict
from importlib import import_module

import pypandoc
import yaml
import yamlordereddictloader

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.functional import cached_property

from mote import monkey
from mote import PROJECT_PATHS
from mote.utils import get_object_by_dotted_name


RESERVED_IDS = (
    "mote", "json", "metadata.json", "metadata.yaml", "projects", "aspects",
    "patterns", "elements", "variations", "tokens", "app"
)


class Cache(object):
    """Objects never change in a live system so we can cache heavily without
    any expiration."""

    _items = OrderedDict()

    def get(self, key, default=None):
        if settings.DEBUG:
            return default
        return self._items.get(key, default)

    def set(self, key, value):
        # Paranoia check for any memory leak
        if len(self._items) > 10000:
            self._items.popitem(0)
        self._items[key] = value

CACHE = Cache()


class Base(object):

    def __init__(self):
        if not hasattr(self, "id"):
            self._id = ""

    @property
    def id(self):
        return self._id

    @property
    def relative_path(self):
        """The relative path to the object, eg.
        myproject/website/patterns/atoms/button/."""
        raise NotImplementedError

    @property
    def _relative_paths(self):
        """List of paths to search. Used by the layering machinery."""
        li = [self.relative_path]
        part = "/".join(self.relative_path.split("/")[1:])
        for parent_id in reversed(self.project.metadata.get("parents", [])):
            li.append("%s/%s" % (parent_id, part))
        return li

    def _get_template(self, name):
        """Return first matching template"""
        try:
            return select_template([pth + name for pth in self._relative_paths])
        except TemplateDoesNotExist:
            return None

    def _get_templates(self, name):
        """Return all matching templates"""
        li = []
        for pth in self._relative_paths:
            try:
                li.append(select_template([pth + name]))
            except TemplateDoesNotExist:
                pass
        return li

    @cached_property
    def metadata(self):
        return self._get_metadata()

    @cached_property
    def metadata_no_traverse(self):
        return self._get_metadata(False)

    def _get_metadata(self, traverse=True):
        """Retrieve metadata for this object. Traverses upward else we can't
        infer metadata when layering."""
        t = None
        for name in ("metadata.json", "metadata.yaml"):
            try:
                t = select_template([self.relative_path + name])
            except TemplateDoesNotExist:
                pass
            if traverse and (t is None):
                t = self._get_template(name)
            if t is not None:
                if name.endswith(".yaml"):
                    return yaml.load(t.template.source, Loader=yamlordereddictloader.Loader) or {}
                else:
                    return json.loads(t.template.source) or {}
        return {}

    @property
    def title(self):
        return self.metadata.get("title", self.id.replace("_", " ").replace("-", " ").capitalize())

    @property
    def description(self):
        return self.metadata.get("description", None)

    @cached_property
    def data(self):
        """Return the data for this object. We start with top level data.X
        files and traverse down to our own data.X, doing dictionary updates
        along the way.  Note we deliberately do not do deepmerges because it
        causes mayhem as dictionaries may keep growing."""
        result = OrderedDict()
        for t in reversed(self._get_templates("data.yaml")):
            if t is not None:
                result.update(yaml.load(t.template.source, Loader=yamlordereddictloader.Loader) or {})
        return result

    @cached_property
    def data_json_string(self):
        return json.dumps(self.data, indent=4)

    def _get_children(self, klass, subdirectory=""):
        """Helper method to fetch children of a certain type"""
        li = []

        # Our own
        try:
            t = select_template([self.project.relative_path + "metadata.json"])
        except TemplateDoesNotExist:
            # Either metadata.json or metadata.yaml must exist. Let it raise if
            # it is not the case.
            t = select_template([self.project.relative_path + "metadata.yaml"])
        pth = os.path.join(os.path.dirname(t.template.origin.name), "..", self.relative_path, subdirectory)
        if os.path.exists(pth):
            li = [klass(id, self) for id in os.listdir(pth) if not id.startswith(".") and not id in RESERVED_IDS]

        # Ask parents
        attr = klass.__name__.lower() + "s"
        for project_id in reversed(self.project.metadata.get("parents", [])):
            obj = get_object_by_dotted_name(".".join([str(project_id)] + self.dotted_name.split(".")[1:]))
            li.extend(getattr(obj, attr))

        # Remove duplicates
        processed = []
        result = []
        for l in li:
            if l.id not in processed:
                result.append(l)
                processed.append(l.id)

        return sorted(result, key=lambda item: item.metadata.get("position", 0))

    @cached_property
    def usage(self):
        t = self._get_template("usage.html")
        if t is not None:
            return t.render()
        t = self._get_template("usage.md")
        if t is not None:
            return pypandoc.convert_text(t.render(), "html", format="md")
        t = self._get_template("usage.rst")
        if t is not None:
            return pypandoc.convert_text(t.render(), "html", format="rst")
        return ""


class ChecksumMixin(object):

    @property
    def checksum(self):
        """Return hash of modification dates of all applicable files"""
        li = []
        for name in (
            "element.html", "metadata.json", "metadata.yaml", "usage.html",
            "usage.md", "usage.rst"
        ):
            t = self._get_template(name)
            if t is not None:
                try:
                    li.append(str(os.path.getmtime(t.template.origin.name)))
                except OSError:
                    pass

        return hashlib.md5(":".join(li).encode("utf-8")).hexdigest()


class Variation(ChecksumMixin, Base):
    """A variation *is* an element but the subclassing breaks down"""

    def __new__(cls, id, element):
        dotted_name = "%s.%s" % (element.dotted_name, id)
        obj = CACHE.get(dotted_name, None)
        if obj is not None:
            return obj
        obj = super(Variation, cls).__new__(cls)
        CACHE.set(dotted_name, obj)
        return obj

    def __init__(self, id, element):
        self._id = id
        self._element = element
        super(Variation, self).__init__()

    @property
    def element(self):
        return self._element

    @property
    def pattern(self):
        return self.element.pattern

    @property
    def aspect(self):
        return self.element.aspect

    @property
    def project(self):
        return self.element.aspect.project

    @property
    def relative_path(self):
        return "%s/library/%s/patterns/%s/%s/variations/%s/" % (
            self.project.id,
            self.aspect.id,
            self.pattern.id,
            self.element.id,
            self.id
        )

    @property
    def _relative_paths(self):
        """A variation *is* an element and can inherit from the element. Adjust
        _relative_paths to allow it."""
        return super(Variation, self)._relative_paths \
            + self.element._relative_paths

    @property
    def title(self):
        return self.metadata_no_traverse.get("title", self.id.replace(
            "_", " ").replace("-", " ").capitalize())

    @property
    def template_names(self):
        return [pth + "element.html" for pth in self._relative_paths]

    @property
    def dotted_name(self):
        return "%s.%s.%s.%s.%s" % (
            self.project.id,
            self.aspect.id,
            self.pattern.id,
            self.element.id,
            self.id
        )


class Element(ChecksumMixin, Base):

    def __new__(cls, id, pattern):
        dotted_name = "%s.%s" % (pattern.dotted_name, id)
        obj = CACHE.get(dotted_name, None)
        if obj is not None:
            return obj
        obj = super(Element, cls).__new__(cls)
        CACHE.set(dotted_name, obj)
        return obj

    def __init__(self, id, pattern):
        self._id = id
        self._pattern = pattern
        super(Element, self).__init__()

    @property
    def pattern(self):
        return self._pattern

    @property
    def aspect(self):
        return self.pattern.aspect

    @property
    def project(self):
        return self.pattern.aspect.project

    @property
    def relative_path(self):
        return "%s/library/%s/patterns/%s/%s/" % (
            self.project.id,
            self.aspect.id,
            self.pattern.id,
            self.id
        )

    @property
    def dotted_name(self):
        return "%s.%s.%s.%s" % (
            self.project.id,
            self.aspect.id,
            self.pattern.id,
            self.id,
        )

    @property
    def template_names(self):
        return [pth + "element.html" for pth in self._relative_paths]

    @cached_property
    def variations(self):
        return self._get_children(Variation, "variations")

    def __getattr__(self, key):
        """Allow variation lookup by name"""
        return {e.id: e for e in self.variations}.get(key)

    @property
    def checksum(self):
        """Consider variations as well"""
        result = super(Element, self).checksum
        for variation in self.variations:
            result += variation.checksum
        return result


class Pattern(Base):

    def __new__(cls, id, aspect):
        dotted_name = "%s.%s" % (aspect.dotted_name, id)
        obj = CACHE.get(dotted_name, None)
        if obj is not None:
            return obj
        obj = super(Pattern, cls).__new__(cls)
        CACHE.set(dotted_name, obj)
        return obj

    def __init__(self, id, aspect):
        self._id = id
        self._aspect = aspect
        super(Pattern, self).__init__()

    @property
    def aspect(self):
        return self._aspect

    @property
    def project(self):
        return self.aspect.project

    @property
    def relative_path(self):
        return "%s/library/%s/patterns/%s/" % (
            self.project.id,
            self.aspect.id,
            self.id
        )

    @property
    def dotted_name(self):
        return "%s.%s.%s" % (
            self.project.id,
            self.aspect.id,
            self.id
        )

    @cached_property
    def elements(self):
        return self._get_children(Element)

    def __getattr__(self, key):
        """Allow element lookup by name"""
        return {e.id: e for e in self.elements}.get(key)


class Aspect(Base):
    """Examples of aspects are website, email templates."""

    def __new__(cls, id, project):
        dotted_name = "%s.%s" % (project.dotted_name, id)
        obj = CACHE.get(dotted_name, None)
        if obj is not None:
            return obj
        obj = super(Aspect, cls).__new__(cls)
        CACHE.set(dotted_name, obj)
        return obj

    def __init__(self, id, project):
        self._id = id
        self._project = project
        super(Aspect, self).__init__()

    @property
    def project(self):
        return self._project

    @property
    def relative_path(self):
        return "%s/library/%s/" % (
            self.project.id,
            self.id,
        )

    @property
    def dotted_name(self):
        return "%s.%s" % (
            self.project.id,
            self.id
        )

    @cached_property
    def patterns(self):
        return self._get_children(Pattern, "patterns")

    def __getattr__(self, key):
        """Allow pattern lookup by name"""
        return {e.id: e for e in self.patterns}.get(key)


class Project(Base):

    def __new__(cls, id):
        dotted_name = id
        obj = CACHE.get(dotted_name, None)
        if obj is not None:
            return obj
        obj = super(Project, cls).__new__(cls)
        CACHE.set(dotted_name, obj)
        return obj

    def __init__(self, id):
        self._id = id
        self._full_path = os.path.join(PROJECT_PATHS[id], id)
        super(Project, self).__init__()

    @cached_property
    def metadata(self):
        """A project must have a metadata file"""
        result = super(Project, self).metadata
        if not result:
            raise RuntimeError(
                "Project %s needs a metadata.yaml file" % self.id
            )
        return result

    @property
    def project(self):
        return self

    @property
    def relative_path(self):
        return str(self.id) + "/"

    @property
    def dotted_name(self):
        return str(self.id)

    @cached_property
    def aspects(self):
        return self._get_children(Aspect, "library")

    def __getattr__(self, key):
        """Allow aspect lookup by name"""
        return {e.id: e for e in self.aspects}.get(key)
