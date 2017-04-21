from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from mote import models, views


class ViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ViewsTestCase, cls).setUpTestData()
        cls.project = models.Project("myproject")
        cls.aspect = models.Aspect("website", cls.project)
        cls.pattern = models.Pattern("atoms", cls.aspect)
        cls.element = models.Element("button", cls.pattern)
        cls.factory = RequestFactory()

    def test_element_partial(self):
        url = reverse("mote:element-partial", args=("myproject", "website", "atoms", "button"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_element_partial_post_request(self):
        request = self.factory.post(
            reverse("mote:element-partial", args=("myproject", "website", "atoms", "button"))
        )
        response = views.ElementPartialView.as_view()(request, project="myproject", aspect="website", pattern="atoms", element="button")
        self.assertEqual(response.status_code, 200)
