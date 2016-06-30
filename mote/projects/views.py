from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views import generic

from .models import Project
from . import forms


class IndexView(generic.ListView):
    template_name = "projects/index.html"

    def get_queryset(self):
        return Project.objects.order_by("-created_on")


class DetailView(generic.DetailView):
    model = Project
    template_name = "projects/detail.html"


class CreateView(generic.CreateView):
    model = Project
    fields = ["name", "slug", "description"]
    # form_class = forms.ProjectQuickCreateForm


class UpdateView(generic.UpdateView):
    model = Project
    fields = ["name", "slug", "description"]


class DeleteView(generic.DeleteView):
    model = Project
    success_url = reverse_lazy("projects:project-list")
