from django.test import TestCase
from django.urls import reverse


class GeographyAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("geography:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Geography Calculators")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Population Geography")
        self.assertContains(response, "Population Density")

    def test_haversine(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "great-circle-distance"}),
            {"lat1": "0", "lon1": "0", "lat2": "0", "lon2": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Distance (km)")

    def test_population_density(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "population-density"}),
            {"population": "1000", "area": "100"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "People per unit area = 10")

    def test_growth_rate(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "population-growth-rate-percent"}),
            {"P0": "100", "P1": "120"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Growth rate = 20 %")

    def test_doubling_time(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "doubling-time-rule-70"}),
            {"rate_percent": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Doubling time = 35")

    def test_cbr(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "crude-birth-rate"}),
            {"births": "30", "population": "1000"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "CBR (per 1000) = 30")

    def test_gradient(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "gradient"}),
            {"vertical_change": "100", "horizontal_distance": "2000"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Gradient = 0.05")

    def test_slope_percent(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "slope-percent"}),
            {"vertical_change": "100", "horizontal_distance": "2000"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Slope = 5 %")

    def test_drainage_density(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "drainage-density"}),
            {"channel_length": "50", "basin_area": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Dd = 5")

    def test_stream_discharge(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "stream-discharge"}),
            {"area": "4", "velocity": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Q = 12")

    def test_relative_humidity(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "relative-humidity"}),
            {"actual_vapor_pressure": "10", "saturation_vapor_pressure": "20"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "RH = 50 %")

    def test_celsius_to_fahrenheit(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "celsius-to-fahrenheit"}),
            {"c": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "F = 32")

    def test_time_zone_offset(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "time-zone-offset-from-longitude"}),
            {"longitude": "30"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Offset (hours) = 2")

    def test_solar_time_difference(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "solar-time-difference-minutes"}),
            {"longitude_diff": "15"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Time difference (min) = 60")

    def test_zero_division_error_rendered(self):
        response = self.client.post(
            reverse("geography:calculate", kwargs={"slug": "population-density"}),
            {"population": "1000", "area": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "must not be zero")
