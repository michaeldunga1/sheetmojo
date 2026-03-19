from django.test import TestCase
from django.urls import reverse


class AreaAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("volume:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volume Formulas")

    def test_calculate_sphere(self):
        response = self.client.post(
            reverse("volume:calculate", kwargs={"slug": "volume-of-sphere"}),
            {"radius": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V = ")
