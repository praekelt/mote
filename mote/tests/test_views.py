from django.test import TestCase
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from mote import models


class ViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ViewsTestCase, cls).setUpTestData()
        cls.project = models.Project("myproject")
        cls.aspect = models.Aspect("website", cls.project)
        cls.pattern = models.Pattern("atoms", cls.aspect)
        cls.element = models.Element("button", cls.pattern)

    def test_element_partial(self):
        url = reverse(
            "mote:element-partial",
            args=("myproject", "website", "atoms", "button")
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_element_partial_post_request(self):
        response = self.client.post(
            reverse(
                "mote:element-partial",
                args=("myproject", "website", "atoms", "button")
            )
        )
        self.assertEqual(response.status_code, 200)
