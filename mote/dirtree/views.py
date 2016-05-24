import os
import glob
import re
from collections import OrderedDict
from termcolor import cprint

import ujson as json
from cached_property import cached_property

from django.views.generic.base import TemplateView
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.templatetags.static import PrefixNode
from django.utils.six.moves.urllib.parse import urljoin
from django.conf import settings

from .models import Project, Aspect, Pattern, Element, Variation, get_object


class HomeView(TemplateView):

    template_name = "mote/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        li = [get_object(Project, id) for id in os.listdir(os.path.join(settings.ROOT_DIR, "projects"))]
        li.sort(lambda a, b: cmp(a.metadata.get("position"), a.metadata.get("position")))
        context["projects"] = li
        return context


class HeadView(TemplateView):
    """Render a <head> tag"""

    @cached_property
    def aspect(self):
        project = get_object(Project, self.kwargs["id"])
        aspect = get_object(Aspect, self.kwargs["aspect"], project)
        return aspect

    def get_template_names(self):
        return (
            "%s/%s/mote/head.html" % (self.aspect.project.id, self.aspect.id),
            "%s/mote/head.html" % self.aspect.project.id,
            "mote/head.html"
        )


class ProjectView(TemplateView):
    """Detail view for a project"""

    template_name = "mote/project.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context["project"] = get_object(Project, kwargs["id"])
        return context


class AspectView(TemplateView):
    """Detail view for an aspect"""

    template_name = "mote/aspect.html"

    def get_context_data(self, **kwargs):
        context = super(AspectView, self).get_context_data(**kwargs)
        project = get_object(Project, kwargs["id"])
        context["aspect"] = get_object(Aspect, kwargs["aspect"], project)
        return context


class PatternView(TemplateView):
    """Detail view for a pattern"""

    template_name = "mote/pattern.html"

    def get_context_data(self, **kwargs):
        context = super(PatternView, self).get_context_data(**kwargs)
        project = get_object(Project, kwargs["id"])
        aspect = get_object(Aspect, kwargs["aspect"], project)
        pattern = get_object(Pattern, kwargs["pattern"], aspect)
        context["pattern"] = pattern

        # A pattern may have an intro view. First look in the pattern itself,
        # then fall back to normal template resolution.
        template_names = (
            "%s/%s/src/patterns/%s/mote/intro.html" % (project.id, aspect.id, pattern.id),
            "mote/pattern/intros/%s.html" % pattern.id,
        )
        intro = None
        for template_name in template_names:
            # todo: dont' render it here, only in the template. Just check that it loads.
            try:
                intro = render_to_string(template_name, {})
                break
            except TemplateDoesNotExist:
                pass
        context["intro"] = intro

        return context


class ElementBaseView(TemplateView):

    @cached_property
    def element(self):
        project = get_object(Project, self.kwargs["id"])
        aspect = get_object(Aspect, self.kwargs["aspect"], project)
        pattern = get_object(Pattern, self.kwargs["pattern"], aspect)
        element = get_object(Element, self.kwargs["element"], pattern)
        return element

    def get_context_data(self, **kwargs):
        context = super(ElementBaseView, self).get_context_data(**kwargs)
        context["element"] = self.element
        context["static_root"] = urljoin(PrefixNode.handle_simple("STATIC_URL"), self.element.aspect.relative_path)
        return context


class ElementIndexView(ElementBaseView):
    """Index view for an element. Provides common UI around an element."""

    def get_template_names(self):
        return (
            self.element.index_template_name,
            "mote/element/index.html"
        )


class ElementPartialView(ElementBaseView):
    """Element view with no wrapping html and body tags"""

    def get_template_names(self):
        return (
            self.element.template_name,
        )


class ElementIframeView(ElementBaseView):
    """Element view suitable for rendering in an iframe"""

    def get_template_names(self):
        return (
            "mote/element/iframe.html"
        )


class VariationBaseView(ElementBaseView):

    @cached_property
    def variation(self):
        return get_object(Variation, self.kwargs["variation"], self.element)

    def get_context_data(self, **kwargs):
        context = super(VariationBaseView, self).get_context_data(**kwargs)
        # Rename some variables so we can re-use templates
        context["original_element"] = self.element
        context["element"] = self.variation
        return context


class VariationPartialView(VariationBaseView):

    def get_template_names(self):
        return (
            self.variation.template_name,
        )


class VariationIframeView(VariationBaseView):
    """Variation view suitable for rendering in an iframe"""

    def get_template_names(self):
        return (
            "mote/element/iframe.html"
        )
