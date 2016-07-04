from __future__ import unicode_literals

from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(
        r"^(?P<pk>[0-9]+)/",
        include([
            url(
                r"^$",
                views.WorktreeUpdate.as_view(),
                name="worktree-update"
            ),
            url(
                r"^pull/$",
                views.WorktreePull.as_view(),
                name="worktree-pull"
            ),
        ])
    ),
    url(
        r"^sync/$",
        views.WorktreeSync.as_view(),
        name="worktree-sync"
    ),
]
