from __future__ import unicode_literals

from django.utils.functional import cached_property
import ujson as json

from mote.patterns.library import BasePatternElement, BasePatternEngine


class DjangoPatternElement(BasePatternElement):
    metadata_name = "metadata.json"

    def load_from_json(self, path):
        data = None
        try:
            with open(path, "r") as fp:
                data = json.load(fp)
        except IOError:
            # No file, empty data.
            pass
        return data

    @cached_property
    def metadata(self):
        return self.load_from_json(self.get_metadata_path())

    def get_context(self):
        base = {"element": self}
        return base

    def html(self, data, variant_name=None):
        template = self.template
        return template.render(self.get_context())


class DjangoPatternEngine(BasePatternEngine):
    element_class = DjangoPatternElement
    template_engine_name = "django"
    patterns_location = "src/patterns/"
