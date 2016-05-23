import re
import md5

from bs4 import BeautifulSoup

from django import template
from django.utils.translation import ugettext as _
from django.utils.functional import Promise
from django.templatetags.cache import CacheNode
from django.template import resolve_variable
from django.template.base import VariableDoesNotExist
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.urlresolvers import reverse, resolve, get_script_prefix

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.conf import settings


register = template.Library()


class DictWithSet(dict):
    """Make dictionary have Django cache API"""

    def set(self, key, value, *args, **kwargs):
        self[key] = value


class CachedNode(template.Node):

    def render(self, context):
        """We cache on the request during development else rendering is too
        slow. During production we use normal caching."""

        request = context["request"]
        if not hasattr(request, "cache"):
            setattr(request, "cache", DictWithSet())
        if settings.DEBUG:
            self.cache = request.cache
        else:
            self.cache = cache


# todo: consolidate render_element and render_element_index
@register.tag
def render_element(parser, token):
    """{% render_element object [k=v] [k=v] ... %}"""
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError(
            "render_element object [k=v] [k=v] ... %}"
        )
    di = {}
    for t in tokens[2:]:
        k, v = t.split("=")
        di[k] = v
    return RenderElementNode(tokens[1], **di)


class RenderElementNode(CachedNode):

    def __init__(self, obj, **kwargs):
        self.obj = template.Variable(obj)
        self.kwargs = {}
        for k, v in kwargs.items():
            self.kwargs[k] = template.Variable(v)

    def render(self, context):
        super(RenderElementNode, self).render(context)
        obj = self.obj.resolve(context)
        resolved = {}
        for k, v in self.kwargs.items():
            try:
                r = v.resolve(context)
            except VariableDoesNotExist:
                pass
            else:
                if isinstance(r, Promise):
                    r = unicode(r)
                resolved[k] = r

        from mote.models import Variation
        if isinstance(obj, Variation):
            url = reverse(
                "mote:variation-partial",
                kwargs=dict(
                    id=obj.project.id,
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
                    id=obj.project.id,
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
        li = [url]
        keys = resolved.keys()
        keys.sort()
        for key in keys:
            li.append('%s,%s' % (key, str(resolved[key])))
        hashed = md5.new(':'.join([str(l) for l in li])).hexdigest()
        cache_key = 'render-element-%s' % hashed

        cached = self.cache.get(cache_key, None)
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
        beauty = BeautifulSoup(html)
        html = beauty.prettify()

        self.cache.set(cache_key, html, 1200)
        return html


@register.tag
def render_element_index(parser, token):
    """{% render_element object [k=v] [k=v] ... %}"""
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError(
            "render_element object [k=v] [k=v] ... %}"
        )
    di = {}
    for t in tokens[2:]:
        k, v = t.split("=")
        di[k] = v
    return RenderElementIndexNode(tokens[1], **di)


class RenderElementIndexNode(CachedNode):

    def __init__(self, obj, **kwargs):
        self.obj = template.Variable(obj)
        self.kwargs = {}
        for k, v in kwargs.items():
            self.kwargs[k] = template.Variable(v)

    def render(self, context):
        super(RenderElementIndexNode, self).render(context)
        obj = self.obj.resolve(context)
        resolved = {}
        for k, v in self.kwargs.items():
            try:
                r = v.resolve(context)
            except VariableDoesNotExist:
                pass
            else:
                if isinstance(r, Promise):
                    r = unicode(r)
                resolved[k] = r

        url = reverse(
            "mote:element-index",
            kwargs=dict(
                id=obj.project.id,
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
        li = [url]
        keys = resolved.keys()
        keys.sort()
        for key in keys:
            li.append('%s,%s' % (key, str(resolved[key])))
        hashed = md5.new(':'.join([str(l) for l in li])).hexdigest()
        cache_key = 'render-element-%s' % hashed

        cached = self.cache.get(cache_key, None)
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
        #beauty = BeautifulSoup(html)
        #html = beauty.prettify()

        self.cache.set(cache_key, html, 1200)
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


@register.tag
def render_view(parser, token):
    """{% render_view view_name [k=v] [k=v] ... %}"""
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError(
            "render_view view_name [k=v] [k=v] ... %}"
        )
    di = {}
    for t in tokens[2:]:
        k, v = t.split("=")
        di[k] = v
    return RenderViewNode(tokens[1], **di)



class RenderViewNode(template.Node):

    def __init__(self, view_name, **kwargs):
        self.view_name = template.Variable(view_name)
        self.kwargs = {}
        for k, v in kwargs.items():
            self.kwargs[k] = template.Variable(v)

    def render(self, context):
        view_name = self.view_name.resolve(context)
        resolved = {}
        for k, v in self.kwargs.items():
            try:
                r = v.resolve(context)
            except VariableDoesNotExist:
                pass
            else:
                if isinstance(r, Promise):
                    r = unicode(r)
                resolved[k] = r

        url = reverse(view_name, kwargs=resolved)

        # Resolve needs any possible prefix removed
        url = re.sub(r"^%s" % get_script_prefix().rstrip('/'), '', url)
        view, args, kwargs = resolve(url)
        kwargs.update(resolved)

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
