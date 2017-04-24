"""Model the elements picked up from the filesystem"""

import json
import os
from importlib import import_module

import yaml

from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.utils.functional import cached_property

from mote import PROJECT_PATHS
from mote.utils import get_object_by_dotted_name


RESERVED_IDS = (
    "mote", "json", "metadata.json", "projects", "aspects", "patterns",
    "elements", "variations"
)


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
        myproject/website/src/patterns/atoms/button/."""
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
        try:
            return select_template([pth + name for pth in self._relative_paths])
        except TemplateDoesNotExist:
            return None

    @cached_property
    def metadata(self):
        t = None
        try:
            t = select_template([self.relative_path + "metadata.json"])
        except TemplateDoesNotExist:
            pass
        if t is None:
            t = self._get_template("metadata.json")

        if t is not None:
            return json.loads(t.template.source)

        return {}

    @property
    def title(self):
        return self.metadata.get("title", self.id)

    @property
    def description(self):
        return self.metadata.get("description", None)

    @cached_property
    def data(self):
        """Return the data for this object"""
        # Handle all styles of data
        for name in ("data.json", "data.yaml", "json/data.json"):
            t = self._get_template(name)
            if t is not None:
                if name.endswith(".yaml"):
                    return yaml.load(t.template.source)
                else:
                    return json.loads(t.template.source)
        return {}

    def _get_children(self, klass, subdirectory=""):
        """Helper method to fetch children of a certain type"""
        li = []

        # Our own
        t = select_template([self.project.relative_path + "metadata.json"])
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

        return sorted(result, key=lambda item: item.metadata.get("position"))


class Variation(Base):
    """A variation *is* an element but the subclassing breaks down"""

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
        return "%s/%s/src/patterns/%s/%s/variations/%s/" % (
            self.project.id,
            self.aspect.id,
            self.pattern.id,
            self.element.id,
            self.id
        )

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

    @property
    def modified(self):
        t = self._get_template("element.html")

        if t is not None:
            try:
                return os.path.getmtime(t.template.origin.name)
            except OSError:
                return 0

        return 0


class Element(Base):

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
        return "%s/%s/src/patterns/%s/%s/" % (
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

    @property
    def index_template_names(self):
        return [pth + "index.html" for pth in self._relative_paths]

    @cached_property
    def variations(self):
        return self._get_children(Variation, "variations")

    @property
    def modified(self):
        t = self._get_template("element.html")

        if t is not None:
            try:
                return os.path.getmtime(t.template.origin.name)
            except OSError:
                return 0

        return 0

    def __getattr__(self, key):
        """Allow variation lookup by name"""
        return {e.id: e for e in self.variations}.get(key)


class Pattern(Base):

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
        return "%s/%s/src/patterns/%s/" % (
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

    def __init__(self, id, project):
        self._id = id
        self._project = project
        super(Aspect, self).__init__()

    @property
    def project(self):
        return self._project

    @property
    def relative_path(self):
        return "%s/%s/" % (
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
        return self._get_children(Pattern, "src/patterns")

    def __getattr__(self, key):
        """Allow pattern lookup by name"""
        return {e.id: e for e in self.patterns}.get(key)


class Project(Base):

    def __init__(self, id):
        self._id = id
        self._full_path = os.path.join(PROJECT_PATHS[id], id)
        super(Project, self).__init__()

    @cached_property
    def metadata(self):
        """A project must have a metadata file"""
        try:
            select_template([self.relative_path + "metadata.json"])
        except TemplateDoesNotExist:
            raise RuntimeError(
                "Project %s needs a metadata.json file" % self.id
            )
        return super(Project, self).metadata

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
        return self._get_children(Aspect)

    def __getattr__(self, key):
        """Allow aspect lookup by name"""
        return {e.id: e for e in self.aspects}.get(key)
