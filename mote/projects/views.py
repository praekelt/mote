from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.views import generic

from . import forms
from .models import Project


class ProjectIndex(generic.ListView):
    template_name = "projects/index.html"

    def get_queryset(self):
        return Project.objects.order_by("-created_on")


class ProjectDetail(generic.DetailView):
    model = Project
    template_name = "projects/detail.html"


class ProjectCreate(generic.CreateView):
    model = Project
    fields = ["name", "slug", "description"]
    # form_class = forms.ProjectQuickCreateForm


class ProjectUpdate(generic.UpdateView):
    model = Project
    fields = ["name", "slug", "description"]


class ProjectDelete(generic.DeleteView):
    model = Project
    success_url = reverse_lazy("projects:project-list")


class RepositoryCreateView(generic.FormView):
    template_name = "projects/projectrepository_form.html"
    form_class = forms.RepositoryQuickCreateForm

    def get_context_data(self, **kwargs):
        context = super(RepositoryCreateView, self).get_context_data(**kwargs)
        project = get_object_or_404(Project, slug=self.kwargs['slug'])
        context['project'] = project
        return context

    def get_success_url(self):
        return reverse(
            "projects:project-detail",
            kwargs={"slug": self.kwargs["slug"]}
        )

    def form_valid(self, form):
        project = get_object_or_404(Project, slug=self.kwargs['slug'])
        project.add_repository_from_url(form.cleaned_data["repository_url"])
        return super(RepositoryCreateView, self).form_valid(form)


class RepositoryQuickCreateView(generic.FormView):
    template_name = "projects/projectrepository_form.html"
    form_class = forms.RepositoryQuickCreateForm

    def get_context_data(self, **kwargs):
        context = super(
            RepositoryQuickCreateView, self
        ).get_context_data(**kwargs)
        project = get_object_or_404(Project, slug=self.kwargs['slug'])
        context['project'] = project
        return context

    def get_success_url(self):
        return reverse(
            "projects:project-detail",
            kwargs={"slug": self.kwargs["slug"]}
        )

    def form_valid(self, form):
        project = get_object_or_404(Project, slug=self.kwargs['slug'])
        project.add_repository_from_url(form.cleaned_data["repository_url"])
        return super(RepositoryQuickCreateView, self).form_valid(form)
