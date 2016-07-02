from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r"^(?P<pk>[0-9]+)/",
        views.WorktreeUpdate.as_view(),
        name="worktree-update"
    ),

]
