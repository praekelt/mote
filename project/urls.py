from django.conf.urls import patterns, url, include
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns("",
    (r"", include("mote.urls", namespace="mote")),
    (r"^admin/", include(admin.site.urls)),
)
