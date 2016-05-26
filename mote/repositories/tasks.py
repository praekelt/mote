from __future__ import unicode_literals

from celery import shared_task
from django.utils.timezone import now
from structlog import get_logger
from columbia import git

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

    if not repository.handler.ready:
        try:
                repository.handler.clone()
        except git.RepositoryError as exc:
            # Cloning the repository has failed, log the failure.
            message = str(exc)
            log.error("Could not clone repository", message=message)
            return
    else:
        repository.handler.update()

    updated_on = now()
    repository.ready = True
    repository.updated_on = updated_on
    repository.save()
    # Add all worktrees
    for wt in repository.handler.worktrees():
        worktree, created = repository.worktrees.get_or_create(
            branch=wt.branch,
            defaults={
                "path": wt.path,
                "ready": True,
                "head": wt.head,
                "updated_on": updated_on
            }
        )


@shared_task(ignore_result=True)
def get_repository_copy_with_lock(repository_pk, expire=300):
    log = logger.bind(repository_pk=repository_pk)
    # We need a lock here to prevent multiple processess trying to access the
    # same repository on disk, so we want to lock on the repository pk as that
    # will guarantee repo level isolation. This is also why we can't use the
    # generic anduin.utils lock decorator.
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
