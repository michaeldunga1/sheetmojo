from math import sin, cos, tan, radians, degrees, asin, pi
from django.test import TestCase
from django.urls import reverse


class TrigonometryAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("trigonometry:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trigonometry Calculators")

    def test_load_form(self):
        response = self.client.get(
            reverse("trigonometry:load-form"), {"formula": "sine-degrees"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sine Function")

    # ── Basic Trig Functions ───────────────────────────────────────────────────
    def test_sine_degrees(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "sine-degrees"}),
            {"angle": "30"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sin(θ°) = 0.5")

    def test_cosine_degrees(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "cosine-degrees"}),
            {"angle": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cos(θ°) = 1")

    def test_tangent_degrees(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "tangent-degrees"}),
            {"angle": "45"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tan(θ°) = 1")

    def test_tangent_undefined(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "tangent-degrees"}),
            {"angle": "90"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "undefined")

    def test_sine_radians(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "sine-radians"}),
            {"angle": str(pi / 6)},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sin(θ) = 0.5")

    # ── Inverse Trig Functions ─────────────────────────────────────────────────
    def test_arcsine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "arcsine"}),
            {"value": "0.5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "θ = 30°")

    def test_arccosine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "arccosine"}),
            {"value": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "θ = 90°")

    def test_arctangent(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "arctangent"}),
            {"value": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "θ = 45°")

    def test_arcsine_invalid(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "arcsine"}),
            {"value": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "between -1 and 1")

    # ── Identity ───────────────────────────────────────────────────────────────
    def test_pythagorean_identity(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "pythagorean-identity"}),
            {"angle": "45"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Result = 1")

    # ── Sum Formulas ───────────────────────────────────────────────────────────
    def test_sum_formula_sine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "sum-formula-sine"}),
            {"A": "30", "B": "60"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sin(A+B) =")

    def test_sum_formula_cosine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "sum-formula-cosine"}),
            {"A": "0", "B": "60"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cos(A+B) =")

    # ── Difference Formulas ────────────────────────────────────────────────────
    def test_difference_formula_sine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "difference-formula-sine"}),
            {"A": "45", "B": "30"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sin(A−B)")

    def test_difference_formula_cosine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "difference-formula-cosine"}),
            {"A": "60", "B": "30"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cos(A−B)")

    # ── Double Angle Formulas ──────────────────────────────────────────────────
    def test_double_angle_sine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "double-angle-sine"}),
            {"angle": "30"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sin(2θ)")

    def test_double_angle_cosine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "double-angle-cosine"}),
            {"angle": "45"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cos(2θ)")

    def test_double_angle_tangent(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "double-angle-tangent"}),
            {"angle": "20"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tan(2θ)")

    # ── Half Angle Formulas ────────────────────────────────────────────────────
    def test_half_angle_sine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "half-angle-sine"}),
            {"angle": "90"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sin(θ/2)")

    def test_half_angle_cosine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "half-angle-cosine"}),
            {"angle": "60"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cos(θ/2)")

    # ── Special Angles ────────────────────────────────────────────────────────
    def test_complementary_angle(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "complementary-angle"}),
            {"angle": "35"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Complement = 55°")

    def test_supplementary_angle(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "supplementary-angle"}),
            {"angle": "60"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Supplement = 120°")

    def test_reference_angle_quadrant1(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "reference-angle"}),
            {"angle": "45"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reference angle = 45°")

    def test_reference_angle_quadrant2(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "reference-angle"}),
            {"angle": "135"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reference angle = 45°")

    # ── Triangle Solving ──────────────────────────────────────────────────────
    def test_law_of_sines_side(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "law-of-sines-side"}),
            {"A": "30", "c": "10", "C": "60"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Side a")

    def test_law_of_sines_angle(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "law-of-sines-angle"}),
            {"A": "30", "a": "5", "b": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Angle B")

    def test_law_of_cosines_side(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "law-of-cosines-side"}),
            {"a": "3", "b": "4", "C": "90"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Side c = 5")

    def test_law_of_cosines_angle(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "law-of-cosines-angle"}),
            {"a": "3", "b": "4", "c": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Angle C = 90°")

    def test_triangle_area_sine(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "triangle-area-sine"}),
            {"A": "90", "b": "3", "c": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Area = 6")

    def test_triangle_area_sine_invalid(self):
        response = self.client.post(
            reverse("trigonometry:calculate", kwargs={"slug": "triangle-area-sine"}),
            {"A": "200", "b": "3", "c": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "between 0°")
