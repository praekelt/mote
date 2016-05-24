from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

from . import views


urlpatterns = patterns("",
    url(r"^$", views.HomeView.as_view(), name="home"),

    url(
        r"^project/head/(?P<id>[\w-]+)/(?P<aspect>[\w-]+)/$",
        views.HeadView.as_view(),
        name="head"
    ),
    url(
        r"^project/partial/(?P<id>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/(?P<variation>[\w-]+)/$",
        views.VariationPartialView.as_view(),
        name="variation-partial"
    ),
    url(
        r"^project/iframe/(?P<id>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/(?P<variation>[\w-]+)/$",
        views.VariationIframeView.as_view(),
        name="variation-iframe"
    ),
    url(
        r"^project/partial/(?P<id>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/$",
        views.ElementPartialView.as_view(),
        name="element-partial"
    ),
    url(
        r"^project/iframe/(?P<id>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/$",
        views.ElementIframeView.as_view(),
        name="element-iframe"
    ),
    url(
        r"^project/(?P<id>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/(?P<element>[\w-]+)/$",
        views.ElementIndexView.as_view(),
        name="element-index"
    ),
    url(
        r"^project/(?P<id>[\w-]+)/(?P<aspect>[\w-]+)/(?P<pattern>[\w-]+)/$",
        views.PatternView.as_view(),
        name="pattern"
    ),
    url(
        r"^project/(?P<id>[\w-]+)/(?P<aspect>[\w-]+)/$",
        views.AspectView.as_view(),
        name="aspect"
    ),
    url(
        r"^project/(?P<id>[\w-]+)/$",
        views.ProjectView.as_view(),
        name="project"
    ),
)
