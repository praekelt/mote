import json
import re
import warnings
from hashlib import md5

from bs4 import BeautifulSoup
import xmltodict

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django import template
from django.template.base import VariableDoesNotExist
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.utils.functional import Promise
from django.utils.six import string_types, text_type

from mote.utils import deepmerge, deephash, get_object_by_dotted_name
from mote.views import ElementPartialView, VariationPartialView,\
    ElementIndexView


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

        # If element_or_identifier is a string convert it
        if isinstance(element_or_identifier, string_types):
            # The "self" project triggers a project lookup. It first checks for
            # a context variable (used internally by the Mote explorer) then
            # for a setting (used when calling render_element over the API).
            if element_or_identifier.startswith("self."):
                project_id = context.get("__mote_project_id__", None)
                if project_id is None:
                    try:
                        value = settings.MOTE["project"]
                    except (AttributeError, KeyError):
                        raise RuntimeError(
                            "Define MOTE[\"project\"] setting for project lookup"
                       )
                    if callable(value):
                        project_id = value(context["request"])
                    else:
                        project_id = value
                obj = get_object_by_dotted_name(
                    element_or_identifier.replace("self.", project_id + ".")
                )
            else:
                obj = get_object_by_dotted_name(element_or_identifier)
            if not isinstance(obj, (Element, Variation)):
                raise template.TemplateSyntaxError(
                    "Invalid identifier %s" % element_or_identifier
                )
        else:
            obj = element_or_identifier

        # Set the object in the context as "element"
        with context.push():
            context["element"] = obj

            # Resolve the kwargs
            resolved = {}
            for k, v in self.kwargs.items():
                try:
                    r = v.resolve(context)
                except VariableDoesNotExist:
                    continue
                if isinstance(r, Promise):
                    r = text_type(r)

                # Strings may be interpreted further
                if isinstance(r, string_types):

                    # Attempt to resolve any variables by rendering
                    t = template.Template(r)
                    raw_struct = t.render(context)

                    # Attempt to convert to JSON
                    try:
                        resolved[k] = json.loads(raw_struct)
                    except ValueError:
                        resolved[k] = r

                else:
                    resolved[k] = r

            # Find the correct view and construct view kwargs
            view_kwargs = dict(
                project=obj.project.id,
                aspect=obj.aspect.id,
                pattern=obj.pattern.id,
            )
            if isinstance(obj, Variation):
                view = VariationPartialView
                view_kwargs.update(dict(
                    element=obj.element.id,
                    variation=obj.id
                ))
            else:
                view = ElementPartialView
                view_kwargs.update(dict(
                    element=obj.id
                ))

			# Compute a cache key before we pop from resolved
            li = [obj.modified, deephash(resolved)]
            li.extend(frozenset(sorted(view_kwargs.items())))
            hashed = md5(
                u":".join([text_type(l) for l in li]).encode("utf-8")
            ).hexdigest()
            cache_key = "render-element-%s" % hashed
            cached = cache.get(cache_key, None)
            if cached is not None:
                return cached

           # Automatically perform masking with the default data
            request = context["request"]
            masked = obj.data
            # Omit top-level key
            if masked:
                masked = masked[list(masked.keys())[0]]
            if "data" in request.GET:
                masked = deepmerge(masked, json.loads(request.GET["data"]))
            elif "data" in resolved:
                masked = deepmerge(masked, resolved.pop("data"))
            context["data"] = masked

            # Construct a final kwargs that includes the context
            final_kwargs = context.flatten()
            del final_kwargs["request"]
            final_kwargs.update(resolved)
            final_kwargs.update(view_kwargs)

            # Call the view. Let any error propagate.
            result = view.as_view()(request, **final_kwargs)

            if isinstance(result, TemplateResponse):
                # The result of a generic view
                result.render()
                html = result.rendered_content
            elif isinstance(result, HttpResponse):
                # Old-school view
                html = result.content

            # Make output beautiful for Chris
            if not settings.DEBUG:
                beauty = BeautifulSoup(html, "html.parser")
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

        # Call the view. Let any error propagate.
        request = context["request"]
        view_kwargs = dict(
            project=obj.project.id,
            aspect=obj.aspect.id,
            pattern=obj.pattern.id,
            element=obj.id
        )
        result = ElementIndexView.as_view()(request, **view_kwargs)

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
        warnings.warn(
            "ResolveNode is being deprecated. Refactor your templates.",
            DeprecationWarning
        )
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
                r = text_type(r)
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
        warnings.warn(
            "Masking is now implicit. Refactor your templates.",
            DeprecationWarning
        )
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


@register.tag(name="get_element_data")
def do_get_element_data(parser, token):
    """{% get_element_data template_name as name %}"""
    tokens = token.split_contents()
    if len(tokens) != 4:
        raise template.TemplateSyntaxError(
            "{% get_element_data template_name as name }"
        )
    return GetElementDataNode(tokens[1], tokens[3])


class GetElementDataNode(template.Node):
    """Use a template to assemble an XML string, convert it to a dictionary
    and set it in the context."""

    def __init__(self, template_name, name):
        self.template_name = template.Variable(template_name)
        # Clean up the name without resorting to resolving a variable
        self.name = name.strip("'").strip('"')

    def render(self, context):
        template_name = self.template_name.resolve(context)
        di = xmltodict.parse(
            render_to_string(template_name, context=context, request=context["request"]),
            force_list={"hex": True}
        )

        # Discard the root node
        di = di[list(di.keys())[0]]

        # In debug mode use expensive conversion for easy debugging
        if settings.DEBUG:
            context[self.name] = json.loads(json.dumps(di))
        else:
            context[self.name] = di

        return ""
