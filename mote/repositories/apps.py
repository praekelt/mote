from __future__ import unicode_literals

from django.apps import AppConfig
from structlog import get_logger

from . import signals


logger = get_logger("mote.repositories")


def handle_fetch_repository_signal(sender, **kwargs):
    """This is a wrapper function that kicks off a celery task to move the
    Repository fetching to an async worker.
    """
    repository_pk = kwargs.get("repository_pk", None)
    log = logger.bind(repository_pk=repository_pk)
    if repository_pk is None:
        log.error("Fetch Repository Signal Handler failed, missing PK")
        return

    # Offload processing to celery worker, only import tasks here to avoid
    # pulling in the whole import chain before the App is fully initialised.
    from . import tasks
    tasks.get_repository_copy_with_lock.delay(repository_pk)


class RepositoriesConfig(AppConfig):
    name = "mote.repositories"
    verbose_name = "Repositories"

    def ready(self):
        dispatch_uid = ("mote.repositories.tasks."
                        "get_repository_copy_with_lock")
        signals.fetch_repository.connect(
            handle_fetch_repository_signal,
            dispatch_uid=dispatch_uid
        )
