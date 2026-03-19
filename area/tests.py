from django.test import TestCase
from django.urls import reverse


class AreaAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("area:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Area Formulas")

    def test_calculate_circle(self):
        response = self.client.post(
            reverse("area:calculate", kwargs={"slug": "area-of-circle"}),
            {"radius": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A = ")
