from django import template
from django.test import TestCase
from django.test.client import RequestFactory

from mote import models
from mote.utils import get_object_by_dotted_name


class TagsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TagsTestCase, cls).setUpTestData()
        cls.factory = RequestFactory()

    def test_render_label_by_identifier(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.label" %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result,
            """<span>Label default text</span>"""
        )

    def test_render_label_by_self(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "self.website.atoms.label" %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result,
            """<span>Label default text</span>"""
        )

    def test_render_label_with_variable_arg(self):
        request = self.factory.get("/")
        arg = {"text": "Foo"}
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.label" arg %}"""
        )
        result = t.render(template.Context({
            "request": request,
            "arg": arg
        }))
        self.assertHTMLEqual(
            result,
            """<span>Foo</span>"""
        )

    def test_render_label_with_string_arg(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.label" '{"text": "Foo"}' %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result,
            """<span>Foo</span>"""
        )

    def test_render_button_by_identifier(self):
        request = self.factory.get("/")

        # Default
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.button" %}"""
        )
        result = t.render(template.Context({"request": request}))

        self.assertHTMLEqual(
            result,
            """<button><span>Button label default text</span></button>"""
        )

    def test_render_button_with_variable_arg(self):
        request = self.factory.get("/")
        arg = {"label": {"text": "Foo"}}
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.button" arg %}"""
        )
        result = t.render(template.Context({
            "request": request,
            "arg": arg
        }))
        self.assertHTMLEqual(
            result,
            """<button><span>Foo</span></button>"""
        )

    def test_render_button_with_string_arg(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.button" '{"label": {"text": "Foo"}}' %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result,
            """<button><span>Foo</span></button>"""
        )

    def test_render_button_with_replacement_label(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.button" '{"label": {"id": "myproject.website.atoms.label.fancy", "text": "Foo"}}' %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result,
            """<button><fancy>Foo</fancy></button>"""
        )

    def test_get_element_data(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% get_element_data "tests/fleet.xml" as fleet %}
            <fleet>
            {% for car in fleet.cars %}
                <car>
                    <brand>{{ car.brand }}</brand>
                    <model>{{ car.model }}</model>
                </car>
            {% endfor %}
            <value>{{ fleet.value }}</value>
            </fleet>"""
        )
        result = t.render(template.Context({
            "request": request,
            "cars": [
                {"brand": "Opel", "model": "Astra"},
                {"brand": "Ford", "model": "Ikon"}
            ]
        }))
        expected = """<fleet>
            <car>
                <brand>Opel</brand>
                <model>Astra</model>
            </car>
            <car>
                <brand>Ford</brand>
                <model>Ikon</model>
            </car>
            <value>100</value>
        </fleet>"""

        self.assertHTMLEqual(result, expected)
