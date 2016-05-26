from __future__ import unicode_literals

from django.conf.urls import include, url


urlpatterns = [
    url(r"^d/", include("mote.dirtree.urls", namespace="mote")),
    url(
        r"^projects/",
        include("mote.projects.urls", namespace="mote-projects")
    ),
]
