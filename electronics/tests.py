from django.test import TestCase
from django.urls import reverse


class ElectronicsAppTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("electronics:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Electronics Calculators")
        self.assertContains(response, "DC Circuits")
        self.assertContains(response, "AC and Reactive Circuits")

    def test_load_form_returns_partial(self):
        response = self.client.get(
            reverse("electronics:load-form"),
            {"formula": "ohms-voltage"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ohm&#x27;s Law")

    def test_ohms_voltage(self):
        response = self.client.post(
            reverse("electronics:calculate", kwargs={"slug": "ohms-voltage"}),
            {"current_a": "2", "resistance_ohm": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Voltage V (V) = 20")

    def test_power_vi(self):
        response = self.client.post(
            reverse("electronics:calculate", kwargs={"slug": "power-vi"}),
            {"voltage_v": "12", "current_a": "1.5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Power P (W) = 18")

    def test_capacitive_reactance(self):
        response = self.client.post(
            reverse("electronics:calculate", kwargs={"slug": "capacitive-reactance"}),
            {"frequency_hz": "50", "cap_f": "0.0001"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reactance Xc (ohm)")

    def test_transformer_vout(self):
        response = self.client.post(
            reverse("electronics:calculate", kwargs={"slug": "transformer-vout"}),
            {"v_primary": "120", "n_primary": "1000", "n_secondary": "500"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Secondary Voltage Vs (V) = 60")

    def test_power_factor_validation(self):
        response = self.client.post(
            reverse("electronics:calculate", kwargs={"slug": "power-factor"}),
            {"real_w": "500", "apparent_va": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apparent power must be greater than 0")

    def test_invalid_formula_returns_404(self):
        response = self.client.get(
            reverse("electronics:load-form"),
            {"formula": "does-not-exist"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
