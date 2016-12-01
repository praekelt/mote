from django.conf.urls import url, include


urlpatterns = [
    url(r"^mote/", include("mote.urls", namespace="mote")),
]
