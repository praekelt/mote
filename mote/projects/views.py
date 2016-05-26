from __future__ import unicode_literals

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
    form_class = forms.ProjectQuickCreateForm
