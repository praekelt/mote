from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r"^$", views.IndexView.as_view(), name="project-list"),
    url(r"^add/$", views.CreateView.as_view(), name="project-add"),
    url(
        r"^(?P<pk>[0-9]+)/$",
        views.DetailView.as_view(),
        name="project-detail"
    ),
]
