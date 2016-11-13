import re
import md5
import json
import types

from bs4 import BeautifulSoup

from django.core.cache import cache
from django.core.urlresolvers import reverse, resolve, get_script_prefix
from django.http import HttpResponse
from django import template
from django.template.base import VariableDoesNotExist
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.utils.functional import Promise
from django.conf import settings

from mote.utils import deepmerge


register = template.Library()


# todo: consolidate render_element and render_element_index
@register.tag
def render_element(parser, token):
    """{% render_element element_or_identifier [k=v] [k=v] ... %}"""
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError(
            "render_element element_or_identifier [k=v] [k=v] ... %}"
        )
    di = {}
    for t in tokens[2:]:
        k, v = t.split("=")
        di[k] = v
    return RenderElementNode(tokens[1], **di)


class RenderElementNode(template.Node):

    def __init__(self, element_or_identifier, **kwargs):
        self.element_or_identifier = template.Variable(element_or_identifier)
        self.kwargs = {}
        for k, v in kwargs.items():
            self.kwargs[k] = template.Variable(v)

    def render(self, context):
        # We must import late
        from mote.models import Project, Aspect, Pattern, Element, Variation

        element_or_identifier = self.element_or_identifier.resolve(context)

        # If element_or_identifier is not an element or variation convert it
        if not isinstance(element_or_identifier, (Element, Variation)):
            parts = element_or_identifier.split(".")
            length = len(parts)
            if length not in (4, 5):
                raise template.TemplateSyntaxError(
                    "Invalid identifier %s" % element_or_identifier
                )
            project = Project(parts[0])
            aspect = Aspect(parts[1], project)
            pattern = Pattern(parts[2], aspect)
            obj = Element(parts[3], pattern)
            if length == 5:
                obj = Variation(parts[4], obj)
        else:
            obj = element_or_identifier

        # Resolve the kwargs
        resolved = {}
        for k, v in self.kwargs.items():
            try:
                r = v.resolve(context)
            except VariableDoesNotExist:
                continue
            if isinstance(r, Promise):
                r = unicode(r)
            # Attempt to convert to JSON
            #if "{" in r:
            #    import pdb;pdb.set_trace()
            try:
                resolved[k] = json.loads(unicode(r))
            except ValueError:
                resolved[k] = r

        if isinstance(obj, Variation):
            url = reverse(
                "mote:variation-partial",
                kwargs=dict(
                    project=obj.project.id,
                    aspect=obj.aspect.id,
                    pattern=obj.pattern.id,
                    element=obj.element.id,
                    variation=obj.id
                )
            )
        else:
            url = reverse(
                "mote:element-partial",
                kwargs=dict(
                    project=obj.project.id,
                    aspect=obj.aspect.id,
                    pattern=obj.pattern.id,
                    element=obj.id
                )
            )
        # Resolve needs any possible prefix removed
        url = re.sub(r"^%s" % get_script_prefix().rstrip('/'), '', url)
        view, args, kwargs = resolve(url)
        kwargs.update(resolved)

        # Compute a cache key
        li = [url, obj.modified]
        keys = resolved.keys()
        keys.sort()
        for key in keys:
            li.append('%s,%s' % (key, str(resolved[key])))
        hashed = md5.new(':'.join([str(l) for l in li])).hexdigest()
        cache_key = 'render-element-%s' % hashed

        cached = cache.get(cache_key, None)
        if cached is not None:
            return cached

        # Call the view. Let any error propagate.
        request = context["request"]
        result = view(request, *args, **kwargs)
        if isinstance(result, TemplateResponse):
            # The result of a generic view
            result.render()
            html = result.rendered_content
        elif isinstance(result, HttpResponse):
            # Old-school view
            html = result.content

        # Make output beautiful for Chris
        if not settings.DEBUG:
            beauty = BeautifulSoup(html)
            html = beauty.prettify()

        cache.set(cache_key, html, 300)
        return html


@register.tag
def render_element_index(parser, token):
    """{% render_element_index object %}"""
    tokens = token.split_contents()
    if len(tokens) != 2:
        raise template.TemplateSyntaxError(
            "render_element_index object %}"
        )
    return RenderElementIndexNode(tokens[1])


class RenderElementIndexNode(template.Node):

    def __init__(self, obj):
        self.obj = template.Variable(obj)

    def render(self, context):
        obj = self.obj.resolve(context)
        url = reverse(
            "mote:element-index",
            kwargs=dict(
                project=obj.project.id,
                aspect=obj.aspect.id,
                pattern=obj.pattern.id,
                element=obj.id
            )
        )
        # Resolve needs any possible prefix removed
        url = re.sub(r"^%s" % get_script_prefix().rstrip('/'), '', url)
        view, args, kwargs = resolve(url)
        # Call the view. Let any error propagate.
        request = context["request"]
        result = view(request, *args, **kwargs)
        if isinstance(result, TemplateResponse):
            # The result of a generic view
            result.render()
            html = result.rendered_content
        elif isinstance(result, HttpResponse):
            # Old-school view
            html = result.content
        return html


@register.tag(name="resolve")
def do_resolve(parser, token):
    """{% resolve var [var] [var] ... %}"""
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError(
            "{% resolve var [var] [var] ... }"
        )
    return ResolveNode(*tokens[1:])


class ResolveNode(template.Node):
    """Return first argument that resolves."""

    def __init__(self, *args):
        self.args = []
        for arg in args:
            self.args.append(template.Variable(arg))

    def render(self, context):
        for arg in self.args:
            try:
                r = arg.resolve(context)
            except VariableDoesNotExist:
                continue
            if isinstance(r, Promise):
                r = unicode(r)
            return r
        return ""


@register.tag(name="mask")
def do_mask(parser, token):
    """{% mask var as name %}"""
    tokens = token.split_contents()
    if len(tokens) != 4:
        raise template.TemplateSyntaxError(
            "{% mask var as name }"
        )
    return MaskNode(tokens[1], tokens[3])


class MaskNode(template.Node):
    """Resolve a dictionary and update keys if a similarly named dictionary
    exists in the template context. This allows dictionaries to be updated
    partially, making for cleaner templates and smaller JSON files."""

    def __init__(self, var, name):
        self.var = template.Variable(var)
        # Clean up the name without resorting to resolving a variable
        self.name = name.strip("'").strip('"')

    def render(self, context):
        var = self.var.resolve(context)
        request = context["request"]
        if self.name in request.GET:
            var = deepmerge(var, json.loads(request.GET[self.name]))
        elif self.name in context:
            var = deepmerge(var, context[self.name])
        context[self.name] = var
        return ""
