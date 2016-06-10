from __future__ import unicode_literals

import os.path

from django.conf import settings
from django.utils.functional import cached_property

from mote.patterns.library import (BasePatternElement, BasePatternEngine,
                                   TemplateDoesNotExist, scandir)


class JinjaPatternElement(BasePatternElement):

    def _get_template_node(self, name):
        template = self.template
        return getattr(template.template.module, name)

    @cached_property
    def template(self):
        path = os.path.join(
            self.relative_path,
            "{0}.html".format(self.pattern)
        )
        return self.engine.template_engine.get_template(path)

    def get_meta_path(self):
        return os.path.join(
            self.path,
            self.pattern,
            self.name
        )

    def html(self, data={}, variant_name=None):
        try:
            node = self._get_template_node(self.name)
        except TemplateDoesNotExist:
            return ""
        return node(**data)


class JinjaPatternEngine(BasePatternEngine):
    element_class = JinjaPatternElement
    template_engine_name = "jinja2"

    def get_template(self, path, name):
        path = os.path.join(path, name)
        return self.template_engine.get_template(path)

    def get_elements_location(self, aspect, pattern, relative=False):
        path = self.get_patterns_location(aspect)
        if relative:
            if settings.REPOSITORY_BASE_DIR in self.base_path:
                # This is from a repo, use that as the base path
                base_path = settings.REPOSITORY_BASE_DIR
            else:
                base_path = self.base_path
            base_path = os.path.join(base_path, "")
            path = path.split(base_path)[1]
        return path

    def get_element_location(self, aspect, pattern, name):
        return self.get_elements_location(aspect, pattern)

    def patterns(self, aspect):
        path = self.get_patterns_location(aspect)
        patterns = []
        if os.path.exists(path):
            for entry in scandir(path):
                if (entry.is_file() and not entry.name.startswith(".") and
                        entry.name not in self.pattern_reserved_names and
                        entry.name.endswith((".html"))):
                    patterns.append(entry.name.rstrip(".html"))
        return patterns

    def elements(self, aspect, pattern):
        full_path = self.get_elements_location(aspect, pattern)
        path = self.get_elements_location(aspect, pattern, relative=True)
        template = self.get_template(path, "{0}.html".format(pattern))
        macro_names = [
            macro for macro in template.template.module.__dict__
            if not macro.startswith("_")
        ]
        elements = []
        for name in macro_names:
            # Ignore variants
            if "__" not in name:
                elements.append(
                    self.element_class(
                        name,
                        pattern,
                        aspect,
                        self,
                        full_path
                    )
                )
        return elements

    def element(self, aspect, pattern, name):
        path = self.get_element_location(aspect, pattern, name)
        return self.element_class(name, pattern, aspect, self, path)
