from __future__ import unicode_literals

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from posixpath import basename

from django.conf import settings
from django.core import validators
from django.db import models
from django.utils.functional import cached_property
from columbia import git

from . import signals


class RepositoryManager(models.Manager):
    def get_or_create_from_url(self, url):
        handler = git.setup_repository(
            settings.REPOSITORY_BASE_DIR,
            url,
            binary=settings.GIT_BINARY
        )
        path = str(handler.location.path)
        return self.get_or_create(
            fetch_url=url, defaults={"path": path}
        )


class Repository(models.Model):
    fetch_url = models.URLField(
        unique=True,
        validators=[
            validators.URLValidator(schemes=settings.ALLOWED_URL_SCHEMES)
        ]
    )
    path = models.CharField(max_length=255, unique=True)
    patterns_path = models.CharField(max_length=255, default="")
    ready = models.BooleanField(default=False)
    updated_on = models.DateTimeField(null=True)
    objects = RepositoryManager()

    def save(self, *args, **kwargs):
        should_fetch = False
        if self._state.adding:
            # Always fetch the first time.
            should_fetch = True
        else:
            if self.fetch_url != self._loaded_values["fetch_url"]:
                should_fetch = True
        super(Repository, self).save(*args, **kwargs)
        # Only initiate the fetch after the save has completed successfully.
        if should_fetch:
            signals.fetch_repository.send(
                sender=self.__class__,
                repository_pk=self.pk
            )

    @cached_property
    def handler(self):
        # NOTE: This property will point to the wrong repo if fetch_url or path
        # are changed on the instance and hence needs to be invalidated when
        # that happens ("del <instance>.handler" will invalidate).
        handler = git.setup_repository(
            settings.REPOSITORY_BASE_DIR,
            self.fetch_url,
            binary=settings.GIT_BINARY,
        )
        return handler

    @classmethod
    def from_db(cls, db, field_names, values):
        # Override loading the instance from the db so we can store the
        # loaded values separately for change tracking purposes.
        instance = super(Repository, cls).from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    @staticmethod
    def get_name_from_url(url):
        parsed_url = urlparse(url)
        path = basename(parsed_url.path)
        git_in_path = path.find(".git")
        if git_in_path > 0:
            path = path[:git_in_path]
        return path


class Worktree(models.Model):
    repository = models.ForeignKey(Repository, related_name="worktrees")
    branch = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    ready = models.BooleanField(default=False)
    head = models.CharField(max_length=255, default="")
    updated_on = models.DateTimeField(null=True)
