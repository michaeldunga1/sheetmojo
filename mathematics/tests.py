from django.test import TestCase
from django.urls import reverse


class MathematicsAppTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("mathematics:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mathematics Calculators")
        self.assertContains(response, "Number Theory")
        self.assertContains(response, "Combinatorics")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Greatest Common Divisor")

    def test_load_form_returns_partial(self):
        response = self.client.get(
            reverse("mathematics:load-form"),
            {"formula": "gcd"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Greatest Common Divisor")

    def test_gcd_calculation(self):
        response = self.client.post(
            reverse("mathematics:calculate", kwargs={"slug": "gcd"}),
            {"a": "48", "b": "18"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gcd(a, b) = 6")

    def test_combinations_calculation(self):
        response = self.client.post(
            reverse("mathematics:calculate", kwargs={"slug": "combinations"}),
            {"n": "10", "r": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "C(n, r) = 120")

    def test_fibonacci_calculation(self):
        response = self.client.post(
            reverse("mathematics:calculate", kwargs={"slug": "fibonacci"}),
            {"n": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "F(n) = 55")

    def test_arithmetic_series(self):
        # a=1, d=2, n=5 → S5 = 5/2*(2+8) = 25
        response = self.client.post(
            reverse("mathematics:calculate", kwargs={"slug": "arithmetic-series"}),
            {"a": "1", "diff": "2", "n": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "= 25")

    def test_binomial_pmf(self):
        response = self.client.post(
            reverse("mathematics:calculate", kwargs={"slug": "binomial-pmf"}),
            {"n": "10", "k": "3", "p": "0.5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "P(X = k)")

    def test_modular_inverse_no_inverse(self):
        response = self.client.post(
            reverse("mathematics:calculate", kwargs={"slug": "modular-inverse"}),
            {"a": "4", "m": "6"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Modular inverse does not exist")

    def test_geometric_series_infinite_diverges(self):
        response = self.client.post(
            reverse("mathematics:calculate", kwargs={"slug": "geometric-series-infinite"}),
            {"a": "1", "r": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "diverges")

    def test_invalid_formula_returns_404(self):
        response = self.client.get(
            reverse("mathematics:load-form"),
            {"formula": "does-not-exist"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
