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

    def test_render_select_by_identifier(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.select" %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result,
            """<select>
                <option value="1">
                    <span>
                        Option label 1
                    </span>
                </option>
                <option value="2">
                    <span>
                        Option label 2
                    </span>
                </option>
            </select>"""
        )

    def test_render_select_with_variable_arg(self):
        request = self.factory.get("/")
        arg = {"options": [
                {"value": 1, "label": {"text": "Foo option label 1"}},
                {"value": 2, "label": {"text": "Foo option label 2"}}
        ]}
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.select" arg %}"""
        )
        result = t.render(template.Context({
            "request": request,
            "arg": arg
        }))
        self.assertHTMLEqual(
            result,
            """<select>
                <option value="1">
                    <span>
                        Foo option label 1
                    </span>
                </option>
                <option value="2">
                    <span>
                        Foo option label 2
                    </span>
                </option>
            </select>"""
        )

    def test_render_select_with_button(self):
        """Do something crazy and replace label with a button"""
        request = self.factory.get("/")
        arg = {"options": [
                {"value": 1, "label": {"id": "self.website.atoms.button", "label": {"text": "Foo option label 1"}}},
                {"value": 2, "label": {"id": "self.website.atoms.button", "label": {"text": "Foo option label 2"}}}
        ]}
        t = template.Template("""{% load mote_tags %}
            {% render "myproject.website.atoms.select" arg %}"""
        )
        result = t.render(template.Context({
            "request": request,
            "arg": arg
        }))
        self.assertHTMLEqual(
            result,
            """<select>
                <option value="1">
                    <button>
                    <span>
                        Foo option label 1
                    </span>
                    </button>
                </option>
                <option value="2">
                    <button>
                    <span>
                        Foo option label 2
                    </span>
                    </button>
                </option>
            </select>"""
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
