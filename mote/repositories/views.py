from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views import generic

from .models import Worktree
from ..repositories import tasks


class WorktreeUpdate(generic.UpdateView):
    model = Worktree
    fields = ["library_root_path", "static_path", "pattern_engine"]

    def get_success_url(self):
        return reverse(
            "projects:project-detail",
            kwargs={"slug": self.kwargs["slug"]}
        )


class WorktreePull(generic.RedirectView):
    """Redirect to the Atom view as there is nothing to show in an aspect
    detail view.
    """
    pattern_name = "projects:project-detail"

    def dispatch(self, request, *args, **kwargs):
        # Perform pull and set message
        worktree = get_object_or_404(Worktree, pk=self.kwargs["pk"])
        tasks.pull_worktree(worktree.pk)
        msg = "Worktree '{0}' pulled.".format(worktree.branch)
        messages.add_message(request, messages.INFO, msg)
        return super(WorktreePull, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        if "pk" in kwargs:
            kwargs.pop("pk")
        if "repository" in kwargs:
            kwargs.pop("repository")
        return super(WorktreePull, self).get_redirect_url(*args, **kwargs)
