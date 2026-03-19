from django.test import TestCase
from django.urls import reverse


class HomeAppTests(TestCase):
    def test_home_loads(self):
        response = self.client.get(reverse("home:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Explore Calculator Apps")
        self.assertContains(response, "Volume")
        self.assertContains(response, "Agriculture")

    def test_list_view_mode(self):
        response = self.client.get(reverse("home:index"), {"view": "list"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List View")
        self.assertContains(response, "Open App")

    def test_invalid_view_defaults_to_grid(self):
        response = self.client.get(reverse("home:index"), {"view": "unknown"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grid View")
