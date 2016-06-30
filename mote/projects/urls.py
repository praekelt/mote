from __future__ import unicode_literals

from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r"^$", views.IndexView.as_view(), name="project-list"),
    url(r"^add/$", views.CreateView.as_view(), name="project-add"),
    url(
        r"^(?P<slug>[\w-]+)/",
        include([
            url(
                r"^$",
                views.DetailView.as_view(),
                name="project-detail"
            ),
            url(
                r"^update/$",
                views.UpdateView.as_view(),
                name="project-update"
            ),
            url(
                r"^delete/$",
                views.DeleteView.as_view(),
                name="project-delete"
            ),
            url(
                r"^repos/add$",
                views.RepositoryCreateView.as_view(),
                name="repository-add"
            ),
            url(
                r"^repos/quick-add$",
                views.RepositoryQuickCreateView.as_view(),
                name="repository-quick-add"
            ),
        ])
    ),
    # The mote internal pattern library doesn't use a repo.
    url(
        r"^mote/",
        include([
            url(
                r"^patterns/",
                include("mote.patterns.urls", namespace="internal")
            ),
        ])
    ),
    # Pattern views
    url(
        r"^(?P<project>[\w-]+)/(?P<repository>[\w-]+)/",
        include([
            url(
                r"^patterns/",
                include("mote.patterns.urls", namespace="patterns")
            ),
            url(
                r"^(?P<branch>[\w-]+)/patterns/",
                include("mote.patterns.urls", namespace="patterns-branch")
            ),
        ])
    ),
]
