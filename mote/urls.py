from __future__ import unicode_literals

from django.conf.urls import include, url
from django.views.generic import RedirectView


urlpatterns = [
    url(
        r"^$",
        RedirectView.as_view(pattern_name="projects:project-list")
    ),
    url(
        r"^projects/",
        include("mote.projects.urls", namespace="projects")
    ),
]
