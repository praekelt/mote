from django import template
from django.test import TestCase
from django.test.client import RequestFactory

from mote import models
from mote.utils import get_object_by_dotted_name


class LayersTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(LayersTestCase, cls).setUpTestData()
        cls.factory = RequestFactory()

    def test_render_label(self):
        """We override label element and data"""
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "myprojectchild.website.atoms.label" %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result, "<child>Label child</child>"
        )

    def test_render_anchor(self):
        """We override anchor element but not data"""
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "myprojectchild.website.atoms.anchor" %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result, "<child>Anchor child</child>"
        )

    def test_render_panel(self):
        """We inherit panel fully"""
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "myprojectchild.website.atoms.panel" %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result, "Panel"
        )

    def test_metadata_label(self):
        """We override label element and data"""
        obj = get_object_by_dotted_name("myprojectchild.website.atoms.label")
        self.assertEqual(obj.metadata["title"], "MyProjectChild label")

    def test_metadata_anchor(self):
        """We override anchor element but not data"""
        obj = get_object_by_dotted_name("myprojectchild.website.atoms.anchor")
        self.assertEqual(obj.metadata["title"], "Anchor")

    def test_metadata_panel(self):
        """We inherit panel fully"""
        obj = get_object_by_dotted_name("myprojectchild.website.atoms.panel")
        self.assertEqual(obj.metadata["title"], "Panel")
