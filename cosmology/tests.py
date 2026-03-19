from django.test import TestCase
from django.urls import reverse


class CosmologyAppTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("cosmology:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cosmology Calculators")
        self.assertContains(response, "Expansion &amp; Redshift")
        self.assertContains(response, "Gravity &amp; Orbits")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Hubble Law Velocity")

    def test_load_form_returns_hubble_partial(self):
        response = self.client.get(
            reverse("cosmology:load-form"),
            {"formula": "hubble-law"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hubble Law Velocity")

    def test_hubble_law(self):
        response = self.client.post(
            reverse("cosmology:calculate", kwargs={"slug": "hubble-law"}),
            {"h0_km_s_mpc": "70", "distance_mpc": "100"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recession Velocity (km/s) = 7000")

    def test_redshift_to_scale_factor(self):
        response = self.client.post(
            reverse("cosmology:calculate", kwargs={"slug": "redshift-to-scale-factor"}),
            {"redshift": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scale Factor a = 0.5")

    def test_age_from_hubble(self):
        response = self.client.post(
            reverse("cosmology:calculate", kwargs={"slug": "age-from-hubble"}),
            {"h0_km_s_mpc": "70"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Age (Gyr) = 13.97142857")

    def test_luminosity_distance(self):
        response = self.client.post(
            reverse("cosmology:calculate", kwargs={"slug": "luminosity-distance"}),
            {"redshift": "1", "comoving_distance_mpc": "3400"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Luminosity Distance (Mpc) = 6800")

    def test_invalid_redshift_validation(self):
        response = self.client.post(
            reverse("cosmology:calculate", kwargs={"slug": "redshift-to-scale-factor"}),
            {"redshift": "-1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Redshift must be greater than -1")

    def test_invalid_formula_returns_404(self):
        response = self.client.get(
            reverse("cosmology:load-form"),
            {"formula": "does-not-exist"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
