from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from mote import models


class TestViews(TestCase):

    @classmethod
    def setUpTest(cls):
        super(TestViews, cls).setUpTest()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        super(TestViews, cls).setUpTestData()
        cls.project = models.Project("myproject")
        cls.aspect = models.Aspect("website", cls.project)
        cls.pattern = models.Pattern("atoms", cls.aspect)
        cls.element = models.Element("button", cls.pattern)

    def test_elementpartial(self):
        url = reverse("mote:element-partial", args=("myproject", "website", "atoms", "button"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        print response.content
