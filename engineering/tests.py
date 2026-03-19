from django.test import TestCase
from django.urls import reverse


class EngineeringAppTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("engineering:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Engineering Calculators")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Mechanics &amp; Strength")
        self.assertContains(response, "Stress")

    def test_load_form_returns_partial_for_valid_formula(self):
        response = self.client.get(
            reverse("engineering:load-form"),
            {"formula": "stress"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stress")
        self.assertContains(response, "Compute")

    def test_calculate_success(self):
        response = self.client.post(
            reverse("engineering:calculate", kwargs={"slug": "stress"}),
            {"force": "100", "area": "25"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sigma = 4")

    def test_calculate_with_divide_by_zero_shows_non_field_error(self):
        response = self.client.post(
            reverse("engineering:calculate", kwargs={"slug": "stress"}),
            {"force": "100", "area": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Area must not be zero")

    def test_invalid_formula_returns_404(self):
        response = self.client.get(
            reverse("engineering:load-form"),
            {"formula": "not-real"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
