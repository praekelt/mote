"""Model the elements picked up from the filesystem"""

import os

import ujson as json

from django.utils.functional import cached_property

from mote import PROJECT_PATHS
from mote.utils import get_object_by_dotted_name


RESERVED_IDS = (
    "mote", "json", "metadata.json", "projects", "aspects", "patterns",
    "elements", "variations"
)


class MetadataMixin(object):

    def __init__(self):
        if not hasattr(self, "id"):
            self._id = ""
            self._parent = None
            self._root = ""
        self._metadata = {}
        self._json_files = {}

        # Load metadata in memory because it is never large
        pth = os.path.join(self._root, "metadata.json")
        if os.path.exists(pth):
            fp = open(pth, "r")
            try:
                self._metadata = json.load(fp)
            finally:
                fp.close()

        # Find json files in the json directory, if any
        pth = os.path.join(self._root, "json")
        if os.path.exists(pth):
            for name in os.listdir(pth):
                if name.endswith(".json"):
                    self._json_files[name[:-5]] = os.path.join(pth, name)

    @property
    def id(self):
        return self._id

    @property
    def root(self):
        return self._root

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
        """Traverse upwards and assemble a dictionary of json files"""
        result = {}
        node = self
        while node._parent is not None:
            for k, v in node._json_files.items():
                if k not in result:
                    fp = open(v, "r")
                    try:
                        buf = fp.read()
                    finally:
                        fp.close()
                    if buf:
                        try:
                            result[k] = json.loads(buf)
                        except ValueError:
                            raise RuntimeError("Invalid JSON at %s" % v)
            node = node._parent
        return result

    @cached_property
    def data(self):
        """Return the data for this object"""
        return self.json.get("data", {})


class Variation(MetadataMixin):
    """A variation *is* an element but the subclassing breaks down"""

    def __init__(self, id, element):
        self._id = id
        self._parent = element
        self._element = element
        self._root = os.path.join(element.root, "variations", id)
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
        li = ["%s/element.html" % self.relative_path]
        for parent_id in reversed(self.project.metadata.get("parents", [])):
            li.append("%s/%s/src/patterns/%s/%s/%s/element.html" % (parent_id, self.aspect.id, self.pattern.id, self.element.id, self.id))
        return li

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
        try:
            return os.path.getmtime(self._root)
        except OSError:
            return 0


class Element(MetadataMixin):

    def __init__(self, id, pattern):
        self._id = id
        self._parent = pattern
        self._pattern = pattern
        self._root = os.path.join(pattern.root, id)
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
    def template_names(self):
        li = ["%s/element.html" % self.relative_path]
        for parent_id in reversed(self.project.metadata.get("parents", [])):
            li.append("%s/%s/src/patterns/%s/%s/element.html" % (parent_id, self.aspect.id, self.pattern.id, self.id))
        return li

    @property
    def dotted_name(self):
        return "%s.%s.%s.%s" % (
            self.project.id,
            self.aspect.id,
            self.pattern.id,
            self.id,
        )

    @property
    def index_template_names(self):
        li = ["%s/index.html" % self.relative_path]
        for parent_id in reversed(self.project.metadata.get("parents", [])):
            li.append("%s/%s/src/patterns/%s/%s/index.html" % (parent_id, self.aspect.id, self.pattern.id, self.id))
        return li

    @cached_property
    def variations(self):
        pth = os.path.join(self._root, "variations")
        if os.path.exists(pth):
            li = [Variation(id, self) for id in os.listdir(pth) if not id.startswith(".") and not id in RESERVED_IDS]
        else:
            li = []
        for parent_id in reversed(self.project.metadata.get("parents", [])):
            obj = get_object_by_dotted_name("%s.%s.%s.%s" % (parent_id, self.aspect.id, self.pattern.id, self.id))
            li.extend(obj.variations)
        processed = []
        result = []
        for l in li:
            if l.id not in processed:
                result.append(l)
                processed.append(l.id)
        return sorted(result, key=lambda item: item.metadata.get("position"))

    @property
    def modified(self):
        try:
            return os.path.getmtime(self._root)
        except OSError:
            return 0

    def __getattr__(self, key):
        """Allow variation lookup by name"""
        return {e.id: e for e in self.variations}.get(key)


class Pattern(MetadataMixin):

    def __init__(self, id, aspect):
        self._id = id
        self._parent = aspect
        self._aspect = aspect
        self._root = os.path.join(aspect.root, "src", "patterns", id)
        super(Pattern, self).__init__()

    @property
    def aspect(self):
        return self._aspect

    @property
    def project(self):
        return self.aspect.project

    @cached_property
    def elements(self):
        li = [Element(id, self) for id in os.listdir(self._root) if not id.startswith(".") and not id in RESERVED_IDS]
        for parent_id in reversed(self.project.metadata.get("parents", [])):
            obj = get_object_by_dotted_name("%s.%s.%s" % (parent_id, self.aspect.id, self.id))
            li.extend(obj.elements)
        processed = []
        result = []
        for l in li:
            if l.id not in processed:
                result.append(l)
                processed.append(l.id)
        return sorted(result, key=lambda item: item.metadata.get("position"))

    def __getattr__(self, key):
        """Allow element lookup by name"""
        return {e.id: e for e in self.elements}.get(key)


class Aspect(MetadataMixin):
    """Examples of aspects are website, email templates."""

    def __init__(self, id, project):
        self._id = id
        self._parent = project
        self._project = project
        self._root = os.path.join(project.root, id)
        super(Aspect, self).__init__()

    @property
    def project(self):
        return self._project

    @property
    def relative_path(self):
        return "%s/%s/dist/" % (
            self.project.id,
            self.id,
        )

    @cached_property
    def patterns(self):
        pth = os.path.join(self._root, "src", "patterns")
        li = [Pattern(id, self) for id in os.listdir(pth) if not id.startswith(".") and not id in RESERVED_IDS]
        for parent_id in reversed(self.project.metadata.get("parents", [])):
            obj = get_object_by_dotted_name("%s.%s" % (parent_id, self.id))
            li.extend(obj.patterns)
        processed = []
        result = []
        for l in li:
            if l.id not in processed:
                result.append(l)
                processed.append(l.id)
        return sorted(result, key=lambda item: item.metadata.get("position"))

    def __getattr__(self, key):
        """Allow pattern lookup by name"""
        return {e.id: e for e in self.patterns}.get(key)


class Project(MetadataMixin):

    def __init__(self, id):
        self._id = id
        self._parent = None
        self._root = os.path.join(PROJECT_PATHS[id], id)
        super(Project, self).__init__()

    @cached_property
    def aspects(self):
        li = [Aspect(id, self) for id in os.listdir(self._root) if not id.startswith(".") and not id in RESERVED_IDS]
        for parent_id in reversed(self.metadata.get("parents", [])):
            obj = Project(parent_id)
            li.extend(obj.aspects)
        processed = []
        result = []
        for l in li:
            if l.id not in processed:
                result.append(l)
                processed.append(l.id)
        return sorted(result, key=lambda item: item.metadata.get("position"))

    def __getattr__(self, key):
        """Allow aspect lookup by name"""
        return {e.id: e for e in self.aspects}.get(key)
