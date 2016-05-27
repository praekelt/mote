from __future__ import unicode_literals

from celery import shared_task
from structlog import get_logger

from . import models
from mote.utils.models import TaskLock


logger = get_logger("mote.repositories")


def _get_repository_copy(repository_pk):
    log = logger.bind(repository_pk=repository_pk)
    try:
        repository = models.Repository.objects.get(pk=repository_pk)
    except models.Project.DoesNotExist:
        # An invalid repository_pk here is an edge case that could happen in
        # the situation where a repository was deleted while this task was in
        # the queue. Log the error and return.
        log.warn("Could not find a Repository with given pk")
        return

    try:
        repository.clone()
    except models.RepositoryAlreadyExists:
        repository.update()
    except models.MoteRepositoryError as exc:
        # Cloning the repository has failed, log the failure for now but
        # we could potentially retry here.
        message = str(exc)
        log.error("Could not clone repository", message=message)
        return

    # Add all the worktrees currently defined in the repo. This will normally
    # be just the single default worktree after a repo is cloned.
    repository.sync_worktrees()


@shared_task(ignore_result=True)
def get_repository_copy_with_lock(repository_pk, expire=300):
    """A wraper task to call _get_repository_copy with a DB-backed lock."""
    log = logger.bind(repository_pk=repository_pk)
    # We need a lock here to prevent multiple processess trying to access the
    # same repository on disk, so we want to lock on the repository pk as that
    # will guarantee repo level isolation. This is also why we can't use the
    # generic mote.utils lock decorator.
    creator = "{function}-{repository_pk}".format(
        function="mote.repositories.tasks.get_repository_copy_with_lock",
        repository_pk=repository_pk
    )
    lock = None
    try:
        lock = TaskLock.acquire(creator, expire=expire)
        if lock is None:
            message = "Could not acquire lock"
            log.warn(message, creator=creator, expire=expire)
            return

        _get_repository_copy(repository_pk)

    finally:
        if lock is not None:
            lock.release()
