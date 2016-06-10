from __future__ import unicode_literals

import os.path

from django.utils.functional import cached_property
import ujson as json

from mote.patterns.library import (BasePatternElement, BasePatternEngine,
                                   TemplateDoesNotExist, scandir)


class DjangoPatternElement(BasePatternElement):
    metadata_name = "metadata.json"
    data_path = "json"

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

    @property
    def data(self):
        return self.json

    @cached_property
    def json(self):
        _data = {}
        path = self.get_data_dir()
        if os.path.exists(path):
            for entry in scandir(path):
                if (entry.is_file() and not entry.name.startswith(".") and
                        entry.name.endswith(".json")):
                    name = entry.name.rstrip(".json")
                    _data[name] = self.load_from_json(entry.path)

        return _data

    def get_context(self):
        base = {"element": self}
        return base

    def html(self, data, variant_name=None, context={}):
        ctx = self.get_context()
        ctx.update(data)
        ctx.update(context)
        try:
            template = self.template
        except TemplateDoesNotExist:
            return ""
        return template.render(ctx)


class DjangoPatternEngine(BasePatternEngine):
    element_class = DjangoPatternElement
    template_engine_name = "django"
    patterns_location = "src/patterns/"
