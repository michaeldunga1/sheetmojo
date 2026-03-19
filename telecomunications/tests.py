from django.test import TestCase
from django.urls import reverse


class TelecomunicationsAppTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("telecomunications:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Telecomunications Calculators")
        self.assertContains(response, "Signal Levels and RF Basics")
        self.assertContains(response, "Noise, Capacity, and Digital Links")

    def test_load_form_returns_partial(self):
        response = self.client.get(
            reverse("telecomunications:load-form"),
            {"formula": "power-to-dbm"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Power to dBm")

    def test_power_to_dbm(self):
        response = self.client.post(
            reverse("telecomunications:calculate", kwargs={"slug": "power-to-dbm"}),
            {"power_w": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Power (dBm) = 30")

    def test_fspl(self):
        response = self.client.post(
            reverse("telecomunications:calculate", kwargs={"slug": "fspl-db"}),
            {"distance_km": "10", "frequency_mhz": "2400"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FSPL (dB)")

    def test_shannon_capacity(self):
        response = self.client.post(
            reverse("telecomunications:calculate", kwargs={"slug": "shannon-capacity"}),
            {"bandwidth_hz": "1000000", "snr_linear": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Capacity C (bps)")

    def test_vswr_validation(self):
        response = self.client.post(
            reverse("telecomunications:calculate", kwargs={"slug": "vswr-from-gamma"}),
            {"gamma": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reflection coefficient magnitude must satisfy")

    def test_return_loss_validation(self):
        response = self.client.post(
            reverse("telecomunications:calculate", kwargs={"slug": "return-loss"}),
            {"gamma": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reflection coefficient magnitude must satisfy")

    def test_invalid_formula_returns_404(self):
        response = self.client.get(
            reverse("telecomunications:load-form"),
            {"formula": "does-not-exist"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
