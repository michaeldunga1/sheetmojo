from django.test import TestCase
from django.urls import reverse


class BiologyAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("biology:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Biology Calculators")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Population Ecology")
        self.assertContains(response, "Population Density")

    def test_population_density(self):
        response = self.client.post(
            reverse("biology:calculate", kwargs={"slug": "population-density"}),
            {"population": "500", "area": "25"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "D = 20")

    def test_logistic_population(self):
        response = self.client.post(
            reverse("biology:calculate", kwargs={"slug": "logistic-population"}),
            {"N0": "100", "K": "1000", "r": "0.5", "t": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nt =")

    def test_hardy_weinberg_heterozygous(self):
        response = self.client.post(
            reverse("biology:calculate", kwargs={"slug": "hardy-weinberg-2pq"}),
            {"p": "0.7", "q": "0.3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2pq = 0.42")

    def test_mitotic_index(self):
        response = self.client.post(
            reverse("biology:calculate", kwargs={"slug": "mitotic-index"}),
            {"dividing_cells": "20", "total_cells": "200"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mitotic index = 10 %")

    def test_bacterial_population(self):
        response = self.client.post(
            reverse("biology:calculate", kwargs={"slug": "bacterial-population"}),
            {"N0": "100", "n": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nt = 800")

    def test_npp(self):
        response = self.client.post(
            reverse("biology:calculate", kwargs={"slug": "net-primary-productivity"}),
            {"gpp": "1200", "respiration": "450"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NPP = 750")

    def test_shannon_diversity(self):
        response = self.client.post(
            reverse("biology:calculate", kwargs={"slug": "shannon-diversity-index-3"}),
            {"n1": "10", "n2": "20", "n3": "30"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "H&#x27; =")

    def test_magnification_zero_actual_size_shows_error(self):
        response = self.client.post(
            reverse("biology:calculate", kwargs={"slug": "magnification"}),
            {"image_size": "45", "actual_size": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "must not be zero")

    def test_load_form_renders_formula_title(self):
        response = self.client.get(
            reverse("biology:load-form"),
            {"formula": "population-density"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Population Density")
