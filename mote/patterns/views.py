from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import resolve, reverse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, RedirectView

from mote.projects.models import Project
from .library import PatternLibrary


class PatternView(TemplateView):

    def _setup_instances(self):
        self.library_type = "jinja2"
        if self.internal:
            self.library_path = settings.MOTE_INTERNAL_PATTERN_LIBRARY
        else:
            self.project = get_object_or_404(
                Project,
                slug=self.url_kwargs["project"]
            )
            self.repository = get_object_or_404(
                self.project.repositories,
                project_link__slug=self.url_kwargs["repository"],
            )
            branch = self.url_kwargs.get("branch", None)
            if branch is not None:
                self.worktree = get_object_or_404(
                    self.repository.worktrees,
                    branch=branch,
                )
            else:
                self.worktree = self.repository.default_worktree
            self.library_type = self.worktree.pattern_engine
            self.library_path = self.worktree.patterns_path

    def dispatch(self, request, *args, **kwargs):
        # Match the current URL to determine which namespace was called.
        self.url_details = resolve(request.path_info)
        self.url_kwargs = kwargs

        # Determine if we are viewing the internal mote pattern library.
        if "internal" in self.url_details.namespaces:
            self.internal = True
        else:
            self.internal = False

        self._setup_instances()
        self.library = PatternLibrary(self.library_type, *self.library_path)
        return super(PatternView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PatternView, self).get_context_data(**kwargs)
        context["url_kwargs"] = self.url_kwargs
        context["url_namespace"] = self.url_details.namespace
        return context


class IndexView(PatternView):
    template_name = "patterns/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["aspects"] = self.library.aspects()
        return context


class AspectIndexView(RedirectView):
    """Redirect to the Atom view as there is nothing to show in an aspect
    detail view.
    """
    pattern_name = ":pattern-list"

    def dispatch(self, request, *args, **kwargs):
        # Match the current URL to determine which namespace was called.
        self.url_details = resolve(request.path_info)
        return super(AspectIndexView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        kwargs["pattern"] = "atoms"
        self.pattern_name = "{0}{1}".format(
            self.url_details.namespace,
            self.pattern_name
        )
        return super(AspectIndexView, self).get_redirect_url(*args, **kwargs)


class PatternIndexView(PatternView):
    template_name = "patterns/patterns-index.html"

    def get_element_url(self, element):
        kwargs = self.url_kwargs.copy()
        kwargs.update({"element": element})
        return reverse(
            self.url_details.namespace + ":pattern-iframe",
            kwargs=kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(PatternIndexView, self).get_context_data(**kwargs)
        pattern = kwargs["pattern"]
        context["patterns"] = self.library.patterns(self.url_kwargs["aspect"])
        context["pattern"] = pattern
        elements = self.library.elements(
            self.url_kwargs["aspect"],
            pattern
        )
        context["elements"] = {
            e: self.get_element_url(e.name)
            for e in elements
        }
        return context


class PatternIframeView(PatternView):
    template_name = "patterns/patterns-iframe.html"

    def get_context_data(self, **kwargs):
        context = super(PatternIframeView, self).get_context_data(**kwargs)
        pattern = kwargs["pattern"]
        element_name = kwargs["element"]
        context["pattern"] = pattern
        element = self.library.element(
            self.url_kwargs["aspect"],
            pattern,
            element_name
        )
        data = {}
        context["element_html"] = element.html(data)
        return context
