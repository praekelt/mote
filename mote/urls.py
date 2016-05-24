from django.conf.urls import patterns, include


urlpatterns = patterns(
    "",
    (r"", include("mote.dirtree.urls", namespace="mote")),
)
