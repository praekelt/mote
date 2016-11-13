from django import template
from django.test import TestCase
from django.test.client import RequestFactory

from mote import models


class TagsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TagsTestCase, cls).setUpTestData()
        cls.factory = RequestFactory()

    def test_render_element_by_identifier(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render_element "myproject.website.atoms.button" %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result,
            """<button class="Button Button--solid Button--yellowButtercup">
            <i>Lorem ipsum</i>
            </button>"""
        )

    def test_render_element_with_kwargs_variable(self):
        request = self.factory.get("/")
        button = {"Italic": {"text": "Foo"}}
        t = template.Template("""{% load mote_tags %}
            {% render_element "myproject.website.atoms.button" button=button %}"""
        )
        result = t.render(template.Context({
            "request": request,
            "button": button
        }))
        self.assertHTMLEqual(
            result,
            """<button class="Button Button--solid Button--yellowButtercup">
            <i>Foo</i>
            </button>"""
        )

    def test_render_element_with_kwargs_dict(self):
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render_element "myproject.website.atoms.button" button='{"Italic": {"text": "Foo"}}' %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        self.assertHTMLEqual(
            result,
            """<button class="Button Button--solid Button--yellowButtercup">
            <i>Foo</i>
            </button>"""
        )

    def xtest_render_element_with_kwargs_combo(self):
        # todo: this is a hard one
        request = self.factory.get("/")
        t = template.Template("""{% load mote_tags %}
            {% render_element "myproject.website.atoms.button" button='{"Italic": {"text": some_text}}' %}"""
        )
        result = t.render(template.Context({
            "request": request,
            "some_text": "Foo"
        }))
        self.assertHTMLEqual(
            result,
            """<button class="Button Button--solid Button--yellowButtercup">
            <i>Foo</i>
            </button>"""
        )
