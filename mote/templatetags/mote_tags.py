import json
import re
import warnings
from collections import OrderedDict
from copy import deepcopy
from hashlib import md5

from bs4 import BeautifulSoup
import xmltodict

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django import template
from django.template.defaultfilters import stringfilter
from django.template.base import VariableDoesNotExist
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.utils.functional import Promise
from six import string_types, text_type
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from mote.utils import deepmerge, deephash, get_object_by_dotted_name
from mote.views import ElementPartialView, VariationPartialView,\
    ElementIndexView


register = template.Library()

# Under certain conditions Mote on Linux
# emits strings with both leading and trailing
# whitespace. This filter gives us a way of
# removing that whitespace.
@register.filter
@stringfilter
def trim(value):
    return value.strip()

@register.tag
def render(parser, token):
    """{% render element_or_identifier [data] %}"""
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError(
            "render element_or_identifier [data] %}"
        )
    return RenderNode(*tokens[1:])


class RenderNode(template.Node):

    def __init__(self, element_or_identifier, data=None):
        self.element_or_identifier = template.Variable(element_or_identifier)
        self.data = None
        if data:
            self.data = template.Variable(data)

    def render(self, context):
        # We must import late
        from mote.models import Project, Aspect, Pattern, Element, Variation

        # To keep templates as simple as possible we don't require quotes to
        # denote a string. That requires special handling.
        try:
            element_or_identifier = self.element_or_identifier.resolve(context)
        except template.VariableDoesNotExist:
            element_or_identifier = \
                context["element"].data[self.element_or_identifier.var]

        data = OrderedDict()
        if self.data:
            data = self.data.resolve(context)

        # Shortcut notation allows an element to be looked up from data
        if isinstance(element_or_identifier, dict):
            copied = deepcopy(element_or_identifier)
            element_or_identifier = copied.pop("id")
            data = copied

        # If element_or_identifier is a string convert it
        if isinstance(element_or_identifier, string_types):

            # The "self" project triggers a project lookup. It first checks for
            # a context variable (used internally by the Mote explorer) then
            # for a setting (used when calling render over the API).
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

            # Non-self lookup
            else:
                obj = get_object_by_dotted_name(element_or_identifier)

            # Type check
            if not isinstance(obj, (Element, Variation)):
                raise template.TemplateSyntaxError(
                    "Invalid identifier %s" % element_or_identifier
                )

        elif isinstance(element_or_identifier, (Element, Variation)):
            obj = element_or_identifier
            data = context.get("data")

        else:
            raise RuntimeError("Cannot identify %r" % element_or_identifier)

        with context.push():

            # We use a completely clean context to avoid leakage
            newcontext = {}

            # Set the object in the new context as "element"
            newcontext["element"] = obj

            # Convert self.data if possible
            if isinstance(data, Promise):
                data = text_type(data)

            # Strings may be interpreted further
            if isinstance(data, string_types):

                # Attempt to resolve any variables by rendering
                t = template.Template(data)
                raw_struct = t.render(context)

                # Attempt to convert to JSON
                try:
                    data = json.loads(raw_struct)
                except ValueError:
                    pass

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

            # Compute a cache key
            li = [obj.checksum, deephash(data)]
            li.extend(frozenset(sorted(view_kwargs.items())))
            hashed = md5(
                ":".join([text_type(l) for l in li]).encode("utf-8")
            ).hexdigest()
            cache_key = "render-element-%s" % hashed
            cached = cache.get(cache_key, None)
            if cached is not None:
                return cached

           # Automatically perform masking with the default data
            request = context["request"]
            masked = obj.data
            if "data" in request.GET:
                masked = deepmerge(masked, json.loads(request.GET["data"]))
            elif data:
                masked = deepmerge(masked, data)

            # Set data on new context. Also set the keys in data directly on
            # new context to make for cleaner templates.
            newcontext["data"] = masked
            for k, v in masked.items():
                if k in ("data", "element", "original_element", "pretty_data"):
                    raise RuntimeError("%s is a reserved key" % k)
                newcontext[k] = v

            # Update new context with the view kwargs
            newcontext.update(view_kwargs)

            # Make data legible in debug mode
            if settings.DEBUG:
                newcontext["pretty_data"] = json.dumps(newcontext["data"], indent=4)

            # Call the view. Let any error propagate.
            result = view.as_view()(request, **newcontext)

            if isinstance(result, TemplateResponse):
                # The result of a generic view
                result.render()
                html = result.rendered_content
            elif isinstance(result, HttpResponse):
                # Old-school view
                html = result.content

            # Make output beautiful for Chris. This is expensive but required
            # for production. Make it togglable for develop.
            if not settings.DEBUG or request.GET.get("beautify", False):
                beauty = BeautifulSoup(html, "html.parser")
                html = beauty.prettify()

            # Useful debug info
            if settings.DEBUG:
                html = "<!-- " + obj.dotted_name + " -->" + html

            cache.set(cache_key, html, 300)
            return html


@register.tag
def render_index(parser, token):
    """{% render_index object %}"""
    tokens = token.split_contents()
    if len(tokens) != 2:
        raise template.TemplateSyntaxError(
            "render_index object %}"
        )
    return RenderIndexNode(tokens[1])


class RenderIndexNode(template.Node):

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
        try:
            request = context.request
        except AttributeError:
            request = context["request"]
        di = xmltodict.parse(
            render_to_string(template_name, context=context.flatten(), request=request)
        )

        # Discard the root node
        di = di[list(di.keys())[0]]

        # In debug mode use expensive conversion for easy debugging
        if settings.DEBUG:
            context[self.name] = json.loads(json.dumps(di))
        else:
            context[self.name] = di

        return ""
