from django.test import TestCase
from django.urls import reverse


class AlgebraAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("algebra:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Algebra Calculators")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Quadratics &amp; Polynomials")
        self.assertContains(response, "Quadratic Formula")

    def test_load_form(self):
        response = self.client.get(
            reverse("algebra:load-form"), {"formula": "quadratic-formula"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quadratic Formula")

    def test_quadratic_two_real_roots(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "quadratic-formula"}),
            {"a": "1", "b": "-5", "c": "6"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "x₁")
        self.assertContains(response, "x₂")

    def test_quadratic_complex_roots(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "quadratic-formula"}),
            {"a": "1", "b": "0", "c": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "i")

    def test_discriminant(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "discriminant"}),
            {"a": "1", "b": "5", "c": "6"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Δ = 1")

    def test_vertex_of_parabola(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "vertex-of-parabola"}),
            {"a": "1", "b": "-4", "c": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vertex")

    def test_solve_linear_equation(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "solve-linear-equation"}),
            {"a": "2", "b": "-8"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "x = 4")

    def test_slope_of_line(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "slope-of-line"}),
            {"x1": "0", "y1": "0", "x2": "4", "y2": "8"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "m = 2")

    def test_slope_vertical_line_error(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "slope-of-line"}),
            {"x1": "3", "y1": "0", "x2": "3", "y2": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "undefined")

    def test_distance_between_points(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "distance-between-two-points"}),
            {"x1": "0", "y1": "0", "x2": "3", "y2": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "d = 5")

    def test_midpoint(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "midpoint"}),
            {"x1": "0", "y1": "0", "x2": "4", "y2": "6"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "M = (2, 3)")

    def test_slope_intercept_form(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "slope-intercept-form"}),
            {"m": "3", "b": "1", "x": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "y = 7")

    def test_arithmetic_sequence_nth_term(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "arithmetic-sequence-nth-term"}),
            {"a1": "2", "d": "3", "n": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "aₙ = 14")

    def test_arithmetic_series_sum(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "arithmetic-series-sum"}),
            {"a1": "1", "d": "1", "n": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sₙ = 55")

    def test_geometric_sequence_nth_term(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "geometric-sequence-nth-term"}),
            {"a1": "2", "r": "3", "n": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "aₙ = 54")

    def test_geometric_series_sum(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "geometric-series-sum"}),
            {"a1": "1", "r": "2", "n": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sₙ = 15")

    def test_simple_interest(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "simple-interest"}),
            {"P": "1000", "r": "0.05", "t": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "I = 150")

    def test_compound_interest(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "compound-interest"}),
            {"P": "1000", "r": "0.1", "n": "1", "t": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A = 1100")

    def test_change_of_base_logarithm(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "change-of-base-logarithm"}),
            {"x": "8", "b": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "log_b(x) = 3")

    def test_sum_of_natural_numbers(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "sum-of-natural-numbers"}),
            {"n": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "S = 55")

    def test_sum_of_squares(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "sum-of-squares"}),
            {"n": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "S = 14")

    def test_sum_of_cubes(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "sum-of-cubes"}),
            {"n": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "S = 36")

    def test_binomial_square(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "binomial-square"}),
            {"a": "3", "b": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "(a+b)² = 49")

    def test_binomial_difference_square(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "binomial-difference-square"}),
            {"a": "5", "b": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "(a−b)² = 9")

    def test_difference_of_squares(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "difference-of-squares"}),
            {"a": "5", "b": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "a²−b² = 16")

    def test_percentage_change(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "percentage-change"}),
            {"old_value": "200", "new_value": "250"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "% change = 25 %")

    def test_percentage_of_a_number(self):
        response = self.client.post(
            reverse("algebra:calculate", kwargs={"slug": "percentage-of-a-number"}),
            {"p": "20", "x": "150"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "R = 30")
