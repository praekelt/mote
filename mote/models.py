"""Model the elements picked up from the filesystem"""

import os
import md5

import ujson as json
from cached_property import cached_property

from django.conf import settings


RESERVED_IDS = (
    "mote", "json", "metadata.json", "projects", "aspects", "patterns",
    "elements", "variations"
)

_OBJECT_CACHE = {}
_JSON_CACHE = {}


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
        """Traverse upwards and assemble a dictionary of json files. Parsing
        JSON is expensive so use caching."""

        global _JSON_CACHE

        result = {}
        node = self
        while node._parent is not None:
            for k, v in node._json_files.items():
                if k not in result:
                    cache_key = "%s%s" % (v, os.path.getmtime(v))
                    cached = _JSON_CACHE.get(cache_key, None)
                    if cached is not None:
                        as_json = cached
                    else:
                        try:
                            as_json = json.loads(open(v, "r").read())
                        except ValueError:
                            raise "Invalid JSON at %s" % v
                        _JSON_CACHE[cache_key] = as_json
                    result[k] = as_json
            node = node._parent
        return result

    @property
    def modified(self):
        try:
            return os.path.getmtime(self._root)
        except OSError:
            return 0


class Variation(MetadataMixin):
    """A variation *is* an index but the subclassing breaks down"""

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
    def template_name(self):
        return "%s/element.html" % self.relative_path


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
    def template_name(self):
        return "%s/element.html" % self.relative_path

    @property
    def index_template_name(self):
        return "%s/index.html" % self.relative_path

    @cached_property
    def variations(self):
        pth = os.path.join(self._root, "variations")
        if not os.path.exists(pth):
            return []
        li = [get_object(Variation, id, self) for id in os.listdir(pth) if not id.startswith(".") and not id in RESERVED_IDS]
        li.sort(lambda a, b: cmp(a.metadata.get("position"), a.metadata.get("position")))
        return li

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
        li = [get_object(Element, id, self) for id in os.listdir(self._root) if not id.startswith(".") and not id in RESERVED_IDS]
        li.sort(lambda a, b: cmp(a.metadata.get("position"), a.metadata.get("position")))
        return li

    def __getattr__(self, key):
        """Allow element lookup by name"""
        return {e.id: e for e in self.elements}.get(key)


class Aspect(MetadataMixin):

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
        li = [get_object(Pattern, id, self) for id in os.listdir(os.path.join(self._root, "src", "patterns")) if not id.startswith(".") and not id in RESERVED_IDS]
        li.sort(lambda a, b: cmp(a.metadata.get("position"), a.metadata.get("position")))
        return li

    def __getattr__(self, key):
        """Allow pattern lookup by name"""
        return {e.id: e for e in self.patterns}.get(key)


class Project(MetadataMixin):

    def __init__(self, id):
        self._id = id
        self._parent = None
        self._root = os.path.join(os.path.dirname(__file__), "..", "projects", id)
        super(Project, self).__init__()

    @cached_property
    def aspects(self):
        li = [get_object(Aspect, id, self) for id in os.listdir(self._root) if not id.startswith(".") and not id in RESERVED_IDS]
        li.sort(lambda a, b: cmp(a.metadata.get("position"), a.metadata.get("position")))
        return li

    def __getattr__(self, key):
        """Allow aspect lookup by name"""
        return {e.id: e for e in self.aspects}.get(key)



def get_object(klass, *args, **kwargs):
    """Return object from cache if possible. Avoid many filesystem read
    operations. Use an in-memory cache to avoid any pickling issues. Caching is
    only required for production."""

    if settings.DEBUG:
        return klass(*args, **kwargs)

    global _OBJECT_CACHE

    # Compute a key
    li = list(args)
    keys = kwargs.keys()
    keys.sort()
    for key in keys:
        li.append('%s,%s' % (key, kwargs[key]))
    li.append(klass.__name__)
    key = md5.new(':'.join([str(l) for l in li])).hexdigest()

    cached = _OBJECT_CACHE.get(key, None)
    if cached is not None:
        return cached

    obj = klass(*args, **kwargs)
    _OBJECT_CACHE[key] = obj

    return obj
