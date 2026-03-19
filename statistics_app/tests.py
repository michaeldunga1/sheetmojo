from django.test import TestCase
from django.urls import reverse


class StatisticsAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("statistics:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Statistics Problems")

    def test_calculate_arithmetic_mean(self):
        response = self.client.post(
            reverse("statistics:calculate", kwargs={"slug": "arithmetic-mean-of-five-values"}),
            {"x1": "2", "x2": "4", "x3": "6", "x4": "8", "x5": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mean = 6")

    def test_calculate_z_score(self):
        response = self.client.post(
            reverse("statistics:calculate", kwargs={"slug": "z-score-of-a-value"}),
            {"x": "85", "mean": "70", "std_dev": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "z-score = 3")

    def test_calculate_confidence_interval(self):
        response = self.client.post(
            reverse("statistics:calculate", kwargs={"slug": "confidence-interval-for-mean"}),
            {"sample_mean": "50", "std_dev": "10", "sample_size": "25", "z_value": "1.96"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confidence interval = [46.08, 53.92]")
