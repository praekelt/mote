from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, RedirectView

from mote.projects.models import Project
from mote.livedtl.library import Aspect


class PatternView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        aspect_slug = kwargs.get("aspect_slug", None)
        self.base_url_kwargs = {
            "project_slug": kwargs["project_slug"],
            "repository_slug": kwargs["repository_slug"],
            "aspect_slug": aspect_slug
        }
        self.project = get_object_or_404(Project, slug=kwargs["project_slug"])
        self.repository = get_object_or_404(
            self.project.repositories,
            project_link__slug=kwargs["repository_slug"],
        )
        self.worktree = self.repository.default_worktree
        self.renderer = Aspect
        if aspect_slug is not None:
            self.aspect = Aspect(aspect_slug, self.worktree.patterns_path)
        return super(PatternView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatternView, self).get_context_data(**kwargs)
        context["base_url_kwargs"] = self.base_url_kwargs
        return context


class IndexView(PatternView):
    template_name = "patterns/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["aspects"] = self.renderer.discover(
            self.worktree.patterns_path
        )
        return context


class AspectIndexView(RedirectView):
    """Redirect to the Atom view as there is nothing to show in an aspect
    detail view.
    """
    pattern_name = "projects:patterns:pattern-list"

    def get_redirect_url(self, *args, **kwargs):
        kwargs["kind"] = "atoms"
        return super(AspectIndexView, self).get_redirect_url(*args, **kwargs)


class PatternIndexView(PatternView):
    template_name = "patterns/patterns-index.html"

    def get_context_data(self, **kwargs):
        context = super(PatternIndexView, self).get_context_data(**kwargs)
        kind = kwargs["kind"]
        context["patterns"] = self.renderer.kinds
        context["kind"] = kind
        context["elements"] = getattr(self.aspect, kind)
        return context
