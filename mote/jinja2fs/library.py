from __future__ import unicode_literals

import os.path

from django.utils.functional import cached_property

from mote.patterns.library import BasePatternElement, BasePatternEngine
from mote.patterns.library import scandir


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

    def html(self, data, variant_name=None):
        node = self._get_template_node(self.name)
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
            path = path.split(self.base_path)[1]
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
            elements.append(
                self.element_class(
                    name,
                    pattern,
                    self,
                    full_path
                )
            )

        return elements

    def element(self, aspect, pattern, name):
        path = self.get_element_location(aspect, pattern, name)
        return self.element_class(name, pattern, self, path)
