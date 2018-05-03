import logging

from django.conf import settings
from django.template.loaders.cached import Loader as CachedLoader

from mote import _thread_locals


logger = logging.getLogger(__name__)


class Loader(CachedLoader):

    def get_template(self, *args, **kwargs):
        if settings.DEBUG:
            # The cache is only valid per request and can thus not be
            # instantiated in __init__. This method provides a convenient
            # instantiation point.
            cache = getattr(_thread_locals, "_cache", None)
            if cache is None:
                setattr(
                    _thread_locals,
                    "_cache",
                    {
                        "template_cache": {},
                        "find_template_cache": {},
                        "get_template_cache": {}
                    }
                )
                cache = _thread_locals._cache
            self.template_cache = cache["template_cache"]
            self.find_template_cache = cache["find_template_cache"]
            self.get_template_cache = cache["get_template_cache"]

        else:
            logger.info(
                "mote.loaders.cached is only intended for use when DEBUG=True"
            )

        return super(Loader, self).get_template(*args, **kwargs)
