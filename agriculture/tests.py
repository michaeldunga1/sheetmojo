from django.test import TestCase
from django.urls import reverse


class AgricultureAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("agriculture:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Agriculture Calculators")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Crop Production")
        self.assertContains(response, "Yield per Hectare")

    def test_yield_per_hectare(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "yield-per-hectare"}),
            {"total_yield_ton": "50", "area_ha": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Yield (ton/ha) = 5")

    def test_total_yield(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "total-yield"}),
            {"yield_per_ha": "4", "area_ha": "12"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Total yield (ton) = 48")

    def test_seed_requirement_total(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "seed-requirement-total"}),
            {"seed_rate_kg_ha": "25", "area_ha": "20"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Total seed (kg) = 500")

    def test_plant_population(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "plant-population"}),
            {"area_m2": "10000", "row_spacing_m": "0.5", "plant_spacing_m": "0.25"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Plant count = 80000")

    def test_fertilizer_required(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "fertilizer-required"}),
            {"n_required_kg_ha": "60", "fertilizer_n_percent": "46"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Fertilizer (kg/ha)")

    def test_irrigation_volume(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "irrigation-volume"}),
            {"depth_mm": "50", "area_ha": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Volume (m3) = 1000")

    def test_theoretical_field_capacity(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "theoretical-field-capacity"}),
            {"speed_km_h": "5", "implement_width_m": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "TFC (ha/h) = 1")

    def test_feed_conversion_ratio(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "feed-conversion-ratio"}),
            {"feed_intake_kg": "12", "weight_gain_kg": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "FCR = 4")

    def test_harvest_index(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "harvest-index"}),
            {"economic_yield": "5", "biological_yield": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Harvest index = 50 %")

    def test_benefit_cost_ratio(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "benefit-cost-ratio"}),
            {"gross_return": "2000", "total_cost": "1000"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "BCR = 2")

    def test_roi(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "return-on-investment"}),
            {"profit": "300", "cost": "1000"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "ROI = 30 %")

    def test_soil_bulk_density(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "soil-bulk-density"}),
            {"oven_dry_mass_g": "130", "core_volume_cm3": "100"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Bulk density (g/cm3) = 1.3")

    def test_soil_moisture_gravimetric(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "soil-moisture-gravimetric"}),
            {"wet_weight": "120", "dry_weight": "100"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Soil moisture = 20 %")

    def test_emission_intensity(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "emission-intensity"}),
            {"emissions_kg_co2e": "1000", "production_ton": "20"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Emission intensity (kg CO2e/ton) = 50")

    def test_error_rendered(self):
        response = self.client.post(
            reverse("agriculture:calculate", kwargs={"slug": "yield-per-hectare"}),
            {"total_yield_ton": "50", "area_ha": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "must not be zero")
