from __future__ import unicode_literals

from django.conf.urls import url, include

from . import views


urlpatterns = [
    # List of available aspects.
    url(r"^$", views.IndexView.as_view(), name="aspect-list"),
    url(
        r"(?P<aspect_slug>[\w-]+)/",
        include([
            # Base aspect index.
            url(r"^$", views.AspectIndexView.as_view(), name="aspect-detail"),
            url(
                r"^(?P<kind>[\w-]+)/$",
                views.PatternIndexView.as_view(),
                name="pattern-list"
            ),
        ])
    )
]
