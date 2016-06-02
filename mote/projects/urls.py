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
    # The mote internal pattern library doesn't use a repo.
    url(
        r"^mote/",
        include([
            url(
                r"patterns/",
                include("mote.patterns.urls", namespace="internal")
            ),
        ])
    ),
    url(
        r"^(?P<project>[\w-]+)/(?P<repository>[\w-]+)/",
        include([
            url(
                r"patterns/",
                include("mote.patterns.urls", namespace="patterns")
            ),
            url(
                r"(?P<branch>[\w-]+)/patterns/",
                include("mote.patterns.urls", namespace="patterns2")
            ),
        ])
    ),
]
