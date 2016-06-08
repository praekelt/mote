from __future__ import unicode_literals

try:
    from os import scandir
except ImportError:
    from scandir import scandir

import os.path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import engines, TemplateDoesNotExist
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
import mistune
import ruamel.yaml


class BasePatternElement(object):
    # The default name of the template an element is expected to be in.
    template_name = "element.html"
    # The default name of the optional index template override.
    index_template_name = "index.html"
    # The default name of the usage text file.
    usage_name = "usage.md"
    # The default name of the changelog text file.
    changelog_name = "changelog.md"
    # The default name of the metadata file.
    metadata_name = "metadata.yml"
    # The default folder of the mock data.
    data_path = "data"

    def __init__(self, name, pattern, aspect, engine, path):
        self.name = name
        self.pattern = pattern
        self.aspect = aspect
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

    def select_template(self, template_name_list):
        chain = []
        for template_name in template_name_list:
            try:
                return self.engine.template_engine.get_template(template_name)
            except TemplateDoesNotExist as e:
                chain.append(e)

        if template_name_list:
            raise TemplateDoesNotExist(
                ", ".join(template_name_list), chain=chain
            )
        else:
            raise TemplateDoesNotExist("No template names provided")

    def get_element_from_reference(self, reference):
        """Loads a named element in the current aspect based on a dotted
        reference.
        """
        try:
            kind, name, data = reference.split(".")
        except ValueError:
            return None, None

        return self.engine.element(self.aspect, kind, name), data

    def load_from_yaml(self, path):
        data = None
        try:
            with open(path, "r") as fp:
                data = ruamel.yaml.load(fp)
        except IOError:
            # No file, empty data.
            pass
        return data

    def parse_yaml(self, path):
        data = self.load_from_yaml(path)
        parsed = {}
        # Expect data to be a dictionary.
        for key, value in data.items():
            # If the base dictionary has an include key, parse it as an
            # include of another element's data.
            if key == "include":
                try:
                    element_ref = value["file"]
                    bind_name = value["name"]
                except KeyError:
                    continue

                element, data_ref = self.get_element_from_reference(
                    element_ref
                )
                try:
                    parsed[bind_name] = element.data[data_ref]
                except KeyError:
                    # The given data ref doesn't exist in the target element.
                    pass
                continue
            parsed[key] = value
        return parsed

    def parse_markdown(self, path):
        try:
            with open(path, "r") as md_file:
                return mistune.markdown(md_file.read())
        except IOError:
            return ""

    # -- Helpers --
    @property
    def base_path(self):
        return self.engine.base_path

    @property
    def relative_path(self):
        """Return the relative path to this element."""
        # Ensure base path has trailing slash before trying to split.
        if settings.REPOSITORY_BASE_DIR in self.base_path:
            # This is from a repo, use that as the base path
            base_path = settings.REPOSITORY_BASE_DIR
        else:
            base_path = self.base_path
        base_path = os.path.join(base_path, "")
        return self.path.split(base_path)[1]

    @cached_property
    def template(self):
        path = os.path.join(self.relative_path, self.template_name)
        return self.engine.template_engine.get_template(path)

    def get_meta_path(self):
        return self.path

    def get_metadata_path(self):
        return os.path.join(self.get_meta_path(), self.metadata_name)

    def get_usage_path(self):
        return os.path.join(self.get_meta_path(), self.usage_name)

    def get_changelog_path(self):
        return os.path.join(self.get_meta_path(), self.changelog_name)

    def get_data_dir(self):
        return os.path.join(self.get_meta_path(), self.data_path)

    def get_index_template(self):
        return os.path.join(self.get_meta_path(), self.index_template_name)

    # -- Core API --
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

    @cached_property
    def metadata(self):
        return self.load_from_yaml(self.get_metadata_path())

    @cached_property
    def data(self):
        _data = {}
        path = self.get_data_dir()
        if os.path.exists(path):
            for entry in scandir(path):
                if (entry.is_file() and not entry.name.startswith(".") and
                        entry.name.endswith(".yml")):
                    name = entry.name.rstrip(".yml")
                    _data[name] = self.parse_yaml(entry.path)

        return _data

    def html(self, data, variant_name=None):
        template = self.template
        node = getattr(template.template.module, self.name)
        # Calling the node / macro will render the HTML.
        return node(**data)

    def source(self):
        pass

    @cached_property
    def changelog(self):
        return self.parse_markdown(self.get_changelog_path())

    @cached_property
    def usage(self):
        return self.parse_markdown(self.get_usage_path())


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
                            aspect,
                            self,
                            entry.path
                        )
                    )
        return elements

    def element(self, aspect, pattern, name):
        path = self.get_element_location(aspect, pattern, name)
        return self.element_class(name, pattern, aspect, self, path)


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
