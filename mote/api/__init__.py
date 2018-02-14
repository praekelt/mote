import json

from django import template
from django.http import JsonResponse, HttpResponseBadRequest,\
    HttpResponseServerError
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.base import View

from rest_framework import serializers, generics
from rest_framework.response import Response

from mote.models import Project, Aspect, Pattern, Element, Variation
from mote.utils import get_object_by_dotted_name


class BaseSerializer(serializers.Serializer):
    rendered = serializers.SerializerMethodField()

    model_class = None

    def get_rendered(self, obj):
        # Let the template tag do the rendering for us
        src = "{% load mote_tags %}{% render object %}"
        context = template.Context({
            "object": obj,
            "request": self.context["request"]
        })
        data = self.context.get("data", {})
        if data:
            context["data"] = data
        t = template.Template(src)
        return t.render(context)


class VariationSerializer(BaseSerializer):
    model_class = Variation


class ElementSerializer(BaseSerializer):
    model_class = Element


class BaseDetail(generics.GenericAPIView):
    queryset = []
    permission_classes = []
    model_class = None

    def get(self, request, format=None, *args, **kwargs):
        obj = kwargs.pop("object", None)
        if obj is None:
            obj = self.get_object(**kwargs)
        # Not a fan of modifying kwargs but there really are no side effects
        kwargs["request"] = request
        serializer = globals()[self.model_class.__name__ + "Serializer"](
            obj, context=kwargs
        )
        return Response(serializer.data)


class VariationDetail(BaseDetail):
    model_class = Variation

    def get_object(self, project, aspect, pattern, element, variation):
        project = Project(project)
        aspect = Aspect(aspect, project)
        pattern = Pattern(pattern, aspect)
        element = Element(element, pattern)
        variation = Variation(variation, element)
        return variation


class ElementDetail(BaseDetail):
    model_class = Element

    def get_object(self, project, aspect, pattern, element):
        project = Project(project)
        aspect = Aspect(aspect, project)
        pattern = Pattern(pattern, aspect)
        element = Element(element, pattern)
        return element


class Multiplex(View):
    """Decode multiple API calls from the request and return encoded results."""

    def get(self, request, *args, **kwargs):
        try:
            project_id = request.GET["project_id"]
        except (KeyError, MultiValueDictKeyError):
            project_id = None

        try:
            calls = json.loads(request.GET["calls"])
        except ValueError:
            return HttpResponseBadRequest()

        results = []
        for call in calls:
            obj = get_object_by_dotted_name(call["id"], project_id=project_id)
            view_klass = globals()[obj.__class__.__name__ + "Detail"]
            view = view_klass().as_view()(
                request=request,
                object=obj,
                data=call["data"],
                format="json"
            )
            if view.status_code == 500:
                return HttpResponseServerError(view.content)
            rendered = view.render().content
            results.append(json.loads(rendered))

        return JsonResponse({"results": results})
