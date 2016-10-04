from django.conf.urls import patterns, url, include

from mote import views


urlpatterns = patterns("",
    url(r"^$", views.HomeView.as_view(), name="home"),

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

    url(r"^brand-guide/$", views.Brand.as_view(), name="brand"),
    url(r"^documentation/$", views.Docs.as_view(), name="documentation"),
    url(r"^basic/$", views.Basic.as_view(), name="basic"),
    url(r"^create_pattern/(?P<library>\w+)?/$", views.create_pattern, name="create_pattern"),
    url(r"^sort_menu/$", views.sort_menu, name="sort_menu"),
)
