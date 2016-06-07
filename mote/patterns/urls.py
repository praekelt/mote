from __future__ import unicode_literals

from django.conf.urls import url, include

from . import views


urlpatterns = [
    # List of available aspects.
    url(r"^$", views.IndexView.as_view(), name="aspect-list"),
    url(
        r"^(?P<aspect>[\w-]+)/",
        include([
            url(
                r"^$",
                views.AspectIndexView.as_view(),
                name="aspect-detail"
            ),
            url(
                r"^(?P<pattern>[\w-]+)/$",
                views.PatternIndexView.as_view(),
                name="pattern-list"
            ),
            url(
                r"^(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/iframe$",
                views.PatternIframeView.as_view(),
                name="pattern-iframe"
            ),
        ])
    )
]
