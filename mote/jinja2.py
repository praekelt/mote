from __future__ import absolute_import

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse

from jinja2 import Environment, Undefined


class SilentUndefined(Undefined):
    """Don't fail template rendering due to undefined variables."""
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""


def environment(**options):
    options["undefined"] = SilentUndefined
    options["extensions"] = ['jinja2.ext.do']
    env = Environment(**options)
    env.globals.update({
        "static": staticfiles_storage.url,
        "url": reverse,
    })
    return env
