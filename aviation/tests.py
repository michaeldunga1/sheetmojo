from django.test import TestCase
from django.urls import reverse


class AviationAppTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("aviation:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aviation Calculators")
        self.assertContains(response, "Aerodynamics")
        self.assertContains(response, "Performance")

    def test_load_form_returns_partial(self):
        response = self.client.get(
            reverse("aviation:load-form"),
            {"formula": "lift-force"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lift Force")

    def test_lift_force(self):
        response = self.client.post(
            reverse("aviation:calculate", kwargs={"slug": "lift-force"}),
            {"rho": "1.225", "v": "50", "wing_area": "16", "cl": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lift L (N) = 24500")

    def test_dynamic_pressure(self):
        response = self.client.post(
            reverse("aviation:calculate", kwargs={"slug": "dynamic-pressure"}),
            {"rho": "1.2", "v": "40"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dynamic Pressure q (Pa) = 960")

    def test_stall_speed(self):
        response = self.client.post(
            reverse("aviation:calculate", kwargs={"slug": "stall-speed"}),
            {"weight_n": "12000", "rho": "1.225", "wing_area": "16", "cl_max": "1.5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stall Speed Vs (m/s)")

    def test_mach_number(self):
        response = self.client.post(
            reverse("aviation:calculate", kwargs={"slug": "mach-number"}),
            {"v": "250", "temperature_k": "288.15"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mach Number M")

    def test_breguet_weight_validation(self):
        response = self.client.post(
            reverse("aviation:calculate", kwargs={"slug": "breguet-range-jet"}),
            {"v": "230", "sfc_1_s": "0.0002", "ld": "15", "wi": "50000", "wf": "50000"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Initial weight must be greater than final weight")

    def test_invalid_formula_returns_404(self):
        response = self.client.get(
            reverse("aviation:load-form"),
            {"formula": "does-not-exist"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
