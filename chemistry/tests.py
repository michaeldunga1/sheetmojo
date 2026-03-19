from django.test import TestCase
from django.urls import reverse


class ChemistryAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("chemistry:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chemistry Calculators")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Stoichiometry &amp; Mole Concepts")
        self.assertContains(response, "Moles from Mass")

    def test_moles_from_mass(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "moles-from-mass"}),
            {"m": "18", "M": "18"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "n = 1")

    def test_molarity(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "molarity"}),
            {"n": "2", "V": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "M = 0.5")

    def test_ph(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "ph-from-hplus"}),
            {"H": "1e-7"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "pH = 7")

    def test_percent_yield(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "percent-yield"}),
            {"actual": "80", "theoretical": "100"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "% yield = 80 %")

    def test_ideal_pressure(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "ideal-gas-pressure"}),
            {"n": "1", "T": "273", "V": "22.4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "P =")

    def test_combined_gas_p2(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "combined-gas-p2"}),
            {"P1": "1", "V1": "1", "T1": "300", "V2": "2", "T2": "300"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "P2 = 0.5")

    def test_heat_energy(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "heat-energy"}),
            {"m": "2", "c": "4", "dT": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "q = 40")

    def test_first_order_half_life(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "first-order-half-life"}),
            {"k": "0.2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "t1/2 = 3.465")

    def test_equilibrium_kc(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "equilibrium-kc"}),
            {
                "A": "1",
                "B": "1",
                "C": "2",
                "D": "3",
                "a": "1",
                "b": "1",
                "c": "1",
                "d": "1",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Kc = 6")

    def test_gibbs_free_energy(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "gibbs-free-energy"}),
            {"dH": "100", "T": "2", "dS": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Delta G = 80")

    def test_photon_energy(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "photon-energy"}),
            {"f": "1e14"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "E =")

    def test_wavelength_from_frequency(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "wavelength-from-frequency"}),
            {"f": "3e8"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "lambda =")

    def test_boiling_point_elevation(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "boiling-point-elevation"}),
            {"i": "2", "Kb": "0.5", "m": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Delta Tb = 1")

    def test_error_rendered(self):
        response = self.client.post(
            reverse("chemistry:calculate", kwargs={"slug": "molarity"}),
            {"n": "1", "V": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "must not be zero")
