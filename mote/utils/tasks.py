from __future__ import unicode_literals

import wrapt
from structlog import get_logger

from .models import TaskLock


default_logger = get_logger("mote.utils")


# Force keyword arguments.
def require_task_lock(*, expire, creator=None, logger=default_logger):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        lock = None
        if creator is None:
            creator_name = "{module}.{name}".format(
                module=wrapped.__module__,
                name=wrapped.__name__
            )
        else:
            creator_name = creator
        try:
            lock = TaskLock.acquire(creator_name, expire)
            if lock is None:
                # Couldn't acquire lock so bail out with warning.
                message = "Could not acquire lock"
                logger.warn(message, creator=creator_name, expire=expire)
                return

            return wrapped(*args, **kwargs)

        finally:
            if lock is not None:
                lock.release()

    return wrapper
