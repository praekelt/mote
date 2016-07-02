from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.views import generic

from .models import Worktree


class WorktreeUpdate(generic.UpdateView):
    model = Worktree
    fields = ["library_root_path", "static_path", "pattern_engine"]

    def get_success_url(self):
        return reverse(
            "projects:project-detail",
            kwargs={"slug": self.kwargs["slug"]}
        )
