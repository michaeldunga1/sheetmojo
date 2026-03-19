from django.test import TestCase
from django.urls import reverse


class ComputingAppTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("computing:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Computing Calculators")
        self.assertContains(response, "Number Systems &amp; Units")
        self.assertContains(response, "Networking &amp; Subnetting")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Binary to Decimal")
        self.assertContains(response, "Convert binary digits into a base-10 value")

    def test_load_form_returns_binary_partial(self):
        response = self.client.get(
            reverse("computing:load-form"),
            {"formula": "binary-to-decimal"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Binary to Decimal")

    def test_binary_to_decimal(self):
        response = self.client.post(
            reverse("computing:calculate", kwargs={"slug": "binary-to-decimal"}),
            {"binary": "101101"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Decimal = 45")

    def test_binary_to_decimal_rejects_invalid_input(self):
        response = self.client.post(
            reverse("computing:calculate", kwargs={"slug": "binary-to-decimal"}),
            {"binary": "10201"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid base-2 digits")

    def test_decimal_to_hex(self):
        response = self.client.post(
            reverse("computing:calculate", kwargs={"slug": "decimal-to-hex"}),
            {"decimal": "255"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hex = FF")

    def test_cpu_execution_time(self):
        response = self.client.post(
            reverse("computing:calculate", kwargs={"slug": "cpu-execution-time"}),
            {"instruction_count": "1000000000", "cpi": "2", "clock_rate_ghz": "2.5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Time (s) = 0.8")

    def test_amdahls_law(self):
        response = self.client.post(
            reverse("computing:calculate", kwargs={"slug": "amdahls-law"}),
            {"parallel_fraction": "0.8", "parallel_speedup": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Speedup = 2.5")

    def test_subnet_usable_hosts(self):
        response = self.client.post(
            reverse("computing:calculate", kwargs={"slug": "subnet-usable-hosts"}),
            {"prefix_length": "24"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usable Hosts = 254")

    def test_hamming_parity_bits(self):
        response = self.client.post(
            reverse("computing:calculate", kwargs={"slug": "hamming-parity-bits"}),
            {"data_bits": "8"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Parity Bits = 4")

    def test_download_time_with_efficiency(self):
        response = self.client.post(
            reverse("computing:calculate", kwargs={"slug": "download-time-with-efficiency"}),
            {"file_size_mb": "100", "bandwidth_mbps": "20", "efficiency_percent": "80"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Time (s) = 50")

    def test_invalid_formula_returns_404(self):
        response = self.client.get(
            reverse("computing:load-form"),
            {"formula": "does-not-exist"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
