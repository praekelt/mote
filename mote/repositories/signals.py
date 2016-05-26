from __future__ import unicode_literals

import django.dispatch


fetch_repository = django.dispatch.Signal(providing_args=["repository_pk"])
