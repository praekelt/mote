from django.conf.urls import url, include
from django.views.generic.base import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

from mote import views, api


app_name = "mote"

urlpatterns = [
    url(r"^$", views.HomeView.as_view(), name="home"),

    url(
        r"^project/partial/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/(?P<variation>[\w-]+)/$",
        views.VariationPartialView.as_view(),
        name="variation-partial"
    ),
    url(
        r"^project/iframe/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/(?P<variation>[\w-]+)/$",
        views.VariationIframeView.as_view(),
        name="variation-iframe"
    ),
    url(
        r"^project/partial/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/$",
        views.ElementPartialView.as_view(),
        name="element-partial"
    ),
    url(
        r"^project/iframe/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/$",
        views.ElementIframeView.as_view(),
        name="element-iframe"
    ),
    url(
        r"^project/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/$",
        views.ElementIndexView.as_view(),
        name="element-index"
    ),
    url(
        r"^project/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/$",
        views.PatternView.as_view(),
        name="pattern"
    ),
    url(
        r"^project/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/$",
        views.AspectView.as_view(),
        name="aspect"
    ),
    url(
        r"^project/(?P<project>[\w-]+)/$",
        views.ProjectView.as_view(),
        name="project"
    ),
]


api_urlpatterns = [
    url(
        r"^api/project/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/(?P<variation>[\w-]+)/$",
        api.VariationDetail.as_view(),
        name="api-variation-detail",
    ),
    url(
        r"^api/project/(?P<project>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/$",
        api.ElementDetail.as_view(),
        name="api-element-detail",
    ),
    url(
        r"^api/multiplex/$",
        api.Multiplex.as_view(),
        name="api-multiplex"
    ),
]

urlpatterns = urlpatterns + format_suffix_patterns(api_urlpatterns)
