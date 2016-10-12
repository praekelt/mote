from django.core.urlresolvers import reverse as django_reverse, NoReverseMatch
from django import template

from rest_framework import serializers, viewsets, generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from mote.models import Project, Aspect, Pattern, Element, Variation


class BaseSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    url = serializers.SerializerMethodField()
    flags = serializers.SerializerMethodField()
    json = serializers.SerializerMethodField()
    rendered = serializers.SerializerMethodField()

    model_class = None

    def get_url(self, obj):
        di = {}
        for klass in (Project, Aspect, Pattern, Element, Variation):
            key = attr = klass.__name__.lower()
            if klass == self.model_class:
                di[key] = obj.id
                break
            else:
                di[key] = getattr(obj, attr).id
        return reverse(
            "mote:api-%s-detail" % key, kwargs=di,
            request=self.context["request"]
        )

    def get_flags(self, obj):
        return obj.metadata.get("flags", {})

    def get_json(self, obj):
        # Keep things fast and simple by not including json if we're at a high
        # level.
        if obj.__class__ in (Project, Aspect):
            setattr(self.context["request"]._request, "_dont_json", True)

        if hasattr(self.context["request"]._request, "_dont_json"):
            return None

        return obj.json

    def get_rendered(self, obj):
        # Keep things fast and simple by not rendering elements if we're at a
        # high level.
        if obj.__class__ in (Project, Aspect):
            setattr(self.context["request"]._request, "_dont_render", True)

        if hasattr(self.context["request"]._request, "_dont_render"):
            return None

        # Let the template tag do the rendering for us
        name = self.model_class.__name__.lower()
        if name not in ("variation", "element"):
            return None
        src = "{% load mote_tags %}{% render_element object %}"
        context = template.Context({"object": obj, "request": self.context["request"]._request})
        t = template.Template(src)
        return t.render(context)


class VariationSerializer(BaseSerializer):
    model_class = Variation


class ElementSerializer(BaseSerializer):
    variations = VariationSerializer(many=True, read_only=True)
    model_class = Element


class PatternSerializer(BaseSerializer):
    elements = ElementSerializer(many=True, read_only=True)
    model_class = Pattern


class AspectSerializer(BaseSerializer):
    patterns = PatternSerializer(many=True, read_only=True)
    model_class = Aspect


class ProjectSerializer(BaseSerializer):
    aspects = AspectSerializer(many=True, read_only=True)
    model_class = Project


class BaseDetail(generics.GenericAPIView):
    queryset = []
    permission_classes = []
    model_class = None

    def get(self, request, format=None, *args, **kwargs):
        obj = self.get_object(**kwargs)
        serializer = globals()[self.model_class.__name__ + "Serializer"](
            obj, context={"request": request}
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


class PatternDetail(BaseDetail):
    model_class = Pattern

    def get_object(self, project, aspect, pattern):
        project = Project(project)
        aspect = Aspect(aspect, project)
        pattern = Pattern(pattern, aspect)
        return pattern


class AspectDetail(BaseDetail):
    model_class = Aspect

    def get_object(self, project, aspect):
        project = Project(project)
        aspect = Aspect(aspect, project)
        return aspect


class ProjectDetail(BaseDetail):
    model_class = Project

    def get_object(self, project):
        project = Project(project)
        return project
