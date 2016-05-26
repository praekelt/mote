from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify

from mote.repositories.models import Repository


class Project(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=255, blank=True)
    repositories = models.ManyToManyField(
        Repository,
        through="ProjectRepository"
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("mote-projects:project-detail", kwargs={"pk": self.pk})

    def add_repository_from_url(self, url):
        repo, created = Repository.objects.get_or_create_from_url(url)
        name = Repository.get_name_from_url(url)
        slug = slugify(name)
        # TODO: protect from adding the same repo twice
        project_repo = ProjectRepository(
            project=self,
            repository=repo,
            name=name,
            slug=slug
        )
        project_repo.save()


class ProjectRepository(models.Model):
    project = models.ForeignKey(Project)
    repository = models.ForeignKey(Repository)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
