from __future__ import unicode_literals

from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r"^$", views.IndexView.as_view(), name="project-list"),
    url(r"^add/$", views.CreateView.as_view(), name="project-add"),
    url(
        r"^(?P<slug>[\w-]+)/$",
        views.DetailView.as_view(),
        name="project-detail"
    ),
    url(
        r"^(?P<project_slug>[\w-]+)/(?P<repository_slug>[\w-]+)/",
        include([
            url(
                r"patterns/",
                include("mote.patterns.urls", namespace="patterns")
            ),
            url(
                r"(?P<branch_slug>[\w-]+)/patterns/",
                include("mote.patterns.urls", namespace="patterns2")
            ),
        ])
    ),
]
