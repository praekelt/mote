from __future__ import unicode_literals

try:
    from os import scandir
except ImportError:
    from scandir import scandir

import os.path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import engines
from django.utils.functional import cached_property
from django.utils.module_loading import import_string


class BasePatternElement(object):
    template_name = "element.html"
    usage_name = "usage.md"
    changelog_name = "changelog.md"
    metadata_name = "metadata.json"

    def __init__(self, name, pattern, engine, path):
        self.name = name
        self.pattern = pattern
        self.engine = engine
        self.path = path

    def __repr__(self):
        rep = (
            "<{klass} name='{name}' pattern='{pattern}', "
            "engine='{engine} 'path='{path}'>"
        )
        return rep.format(
            klass=self.__class__.__name__,
            name=self.name,
            pattern=self.pattern,
            engine=self.engine,
            path=self.path
        )

    # -- Helpers --
    @property
    def relative_path(self):
        """Return the relative path to this element."""
        return self.path.split(self.engine.base_path)[1]

    @cached_property
    def template(self):
        path = os.path.join(self.relative_path, self.template_name)
        return self.engine.template_engine.get_template(path)

    @cached_property
    def variants(self):
        # Variants are defined inline with the base element as macros.
        template = self.template
        macro_names = [
            macro for macro in template.template.module.__dict__
            if macro.startswith("{0}__".format(self.name))
        ]
        variants = []
        for name in macro_names:
            # Variations of this element are named <name>__<variant>.
            try:
                element, variant = name.split("__")
            except ValueError:
                # Not a variant name pattern, skip.
                continue
            variants.append(variant)
        return variants

    # -- Core API --
    def metadata(self):
        pass

    def mock_data(self):
        pass

    def html(self, data, variant_name=None):
        template = self.template
        node = getattr(template.template.module, self.name)
        # Calling the node / macro will render the HTML.
        return node(**data)

    def source(self):
        pass

    def changelog(self):
        pass

    def usage(self):
        pass


class BasePatternEngine(object):
    # The relative path inside the library structure to the folder where the
    # pattern types are stored.
    patterns_location = "patterns"
    # Blacklist of reserved names for aspects.
    aspect_reserved_names = []
    # Blacklist of reserved names for patterns.
    pattern_reserved_names = []
    # Blacklist of reserved names for elements.
    element_reserved_names = []
    # The class to use for elements.
    element_class = BasePatternElement
    # The template engine name to use for rendering.
    template_engine_name = "jinja2"

    def __init__(self, base_path, library_path):
        self.base_path = base_path
        self.library_path = library_path
        # An invalid engine name here will raise InvalidTemplateEngineError
        self.template_engine = engines[self.template_engine_name]

    def _list_subdirs(self, path, reserved_names=[]):
        subdirs = []
        if os.path.exists(path):
            for entry in scandir(path):
                if (entry.is_dir() and not entry.name.startswith(".") and
                        entry.name not in reserved_names):
                    subdirs.append(entry.name)
        return subdirs

    @cached_property
    def path(self):
        return os.path.join(self.base_path, self.library_path)

    def get_patterns_location(self, aspect):
        return os.path.join(self.path, aspect, self.patterns_location)

    def get_elements_location(self, aspect, pattern):
        return os.path.join(
            self.get_patterns_location(aspect),
            pattern
        )

    def get_element_location(self, aspect, pattern, name):
        return os.path.join(
            self.get_elements_location(aspect, pattern),
            name
        )

    def aspects(self):
        """Discover what aspects, if any, this repo provides."""
        return self._list_subdirs(self.path, self.aspect_reserved_names)

    def patterns(self, aspect):
        path = self.get_patterns_location(aspect)
        return self._list_subdirs(path, self.pattern_reserved_names)

    def elements(self, aspect, pattern):
        path = self.get_elements_location(aspect, pattern)
        elements = []
        if os.path.exists(path):
            for entry in scandir(path):
                if (entry.is_dir() and not entry.name.startswith(".") and
                        entry.name not in self.element_reserved_names):
                    elements.append(
                        self.element_class(
                            entry.name,
                            pattern,
                            self,
                            entry.path
                        )
                    )
        return elements

    def element(self, aspect, pattern, name):
        path = self.get_element_location(aspect, pattern, name)
        return self.element_class(name, pattern, self, path)


class PatternLibrary(object):

    def __init__(self, engine_name, base_path, library_path):
        self.engine_name = engine_name
        self.base_path = base_path
        self.library_path = library_path

        # Setup the selected pattern engine.
        try:
            engine_class_string = settings.MOTE_PATTERN_ENGINES[engine_name]
        except KeyError:
            msg = "Unknown Mote pattern engine: '{0}'".format(engine_name)
            raise ImproperlyConfigured(msg)

        self.engine_class = import_string(engine_class_string)
        self.engine = self.engine_class(base_path, library_path)

    def aspects(self):
        return self.engine.aspects()

    def patterns(self, aspect):
        return self.engine.patterns(aspect)

    def elements(self, aspect, pattern):
        return self.engine.elements(aspect, pattern)

    def element(self, aspect, pattern, name):
        return self.engine.element(aspect, pattern, name)
