from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.core import validators

from .models import Project, ProjectRepository


class RepositoryQuickCreateForm(forms.Form):
    repository_url = forms.CharField(
        required=False,
        validators=[
            # validators.URLValidator(schemes=settings.ALLOWED_URL_SCHEMES)
        ]
    )

    def save(self):
        instance = super(RepositoryQuickCreateForm, self).save()
        instance.add_repository_from_url(self.cleaned_data["repository_url"])
        return instance
