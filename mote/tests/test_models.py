from django.test import TestCase

from mote import models


class ModelsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ModelsTestCase, cls).setUpTestData()
        cls.project = models.Project("myproject")
        cls.aspect = models.Aspect("website", cls.project)
        cls.pattern = models.Pattern("atoms", cls.aspect)
        cls.element = models.Element("button", cls.pattern)

    def test_project(self):
        self.assertEqual(self.project.id, "myproject")
        self.assertEqual(self.project.title, "My Project")
        self.assertEqual(self.aspect.id, self.project.aspects[0].id)

    def test_aspect(self):
        self.assertEqual(self.aspect.id, "website")
        self.assertEqual(self.aspect.title, "Website")
        self.assertEqual(self.pattern.id, self.aspect.patterns[0].id)

    def test_pattern(self):
        self.assertEqual(self.pattern.id, "atoms")
        self.assertEqual(self.pattern.title, "Atoms")
        self.assertEqual(self.element.id, self.pattern.elements[0].id)

    def test_element(self):
        self.assertEqual(self.element.id, "button")
        self.assertEqual(self.element.title, "Button")
