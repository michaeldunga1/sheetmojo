from django.test import TestCase
from django.urls import reverse


class CalculusAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("calculus:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Calculus Problems")

    def test_calculate_power_derivative(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "derivative-of-power-function-at-a-point"}),
            {"coefficient": "3", "exponent": "2", "x_value": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "f&#x27;(4) = 24")

    def test_calculate_quadratic_limit(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "limit-of-quadratic-at-a-point"}),
            {"a": "1", "b": "-3", "c": "2", "x_value": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Limit = 12")

    def test_calculate_related_rate_circle_area(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "related-rates-area-of-circle"}),
            {"radius": "3", "radius_rate": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dA/dt = 37.6991118431")

    def test_calculate_quadratic_vertex(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "vertex-of-quadratic"}),
            {"a": "1", "b": "-4", "c": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Minimum at (2, -3)")

    def test_calculate_maximum_rectangle_area(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "maximum-area-of-rectangle-with-fixed-perimeter"},
            ),
            {"perimeter": "20"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maximum area = 25 with l = w = 5")

    def test_calculate_cylinder_related_rate(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "related-rates-volume-of-cylinder"}),
            {"radius": "3", "height": "5", "radius_rate": "2", "height_rate": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dV/dt = 216.7698930977")

    def test_calculate_log_derivative(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "derivative-of-natural-logarithm-at-a-point"},
            ),
            {"coefficient": "6", "x_value": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "f&#x27;(3) = 2")

    def test_calculate_rational_limit_by_cancellation(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "limit-of-rational-function-by-cancellation"},
            ),
            {"coefficient": "3", "approach_value": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Limit = 30")

    def test_calculate_maximum_area_along_wall(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "maximum-area-of-rectangle-along-a-wall"},
            ),
            {"fencing": "40"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maximum area = 200 with width 10 and length 20")

    def test_calculate_sliding_ladder_related_rate(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "related-rates-sliding-ladder"}),
            {"ladder_length": "10", "base_distance": "6", "base_rate": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Height = 8, d y/dt = -1.5")

    def test_calculate_integral_by_parts(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "definite-integral-by-parts-of-xe-to-kx"},
            ),
            {"coefficient": "1", "rate": "1", "lower_bound": "0", "upper_bound": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integral = 1")

    def test_calculate_integral_by_substitution(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "definite-integral-by-substitution-of-x-times-quadratic-power"},
            ),
            {
                "outer_coefficient": "4",
                "inner_coefficient": "1",
                "constant": "1",
                "exponent": "1",
                "lower_bound": "0",
                "upper_bound": "1",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integral = 3")

    def test_calculate_left_hand_limit_at_asymptote(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "left-hand-limit-of-reciprocal-at-vertical-asymptote"},
            ),
            {"coefficient": "3", "asymptote": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Limit = -infinity")

    def test_calculate_right_hand_limit_at_asymptote(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "right-hand-limit-of-reciprocal-at-vertical-asymptote"},
            ),
            {"coefficient": "3", "asymptote": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Limit = infinity")

    def test_calculate_cone_related_rate(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "related-rates-volume-of-cone"}),
            {"radius": "3", "height": "4", "radius_rate": "2", "height_rate": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dV/dt = 59.6902604182")

    def test_calculate_water_level_rate_in_cylinder(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "water-level-rate-in-cylinder"}),
            {"radius": "2", "volume_rate": "12.5663706144"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dh/dt = 1")

    def test_calculate_definite_integral_of_sec_squared(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "definite-integral-of-sec-squared"}),
            {"coefficient": "2", "rate": "1", "lower_bound": "0", "upper_bound": "0.7853981634"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integral = 2")

    def test_calculate_definite_integral_of_sine_times_cosine(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "definite-integral-of-sine-times-cosine"}),
            {"coefficient": "2", "rate": "1", "lower_bound": "0", "upper_bound": "1.5707963268"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integral = 1")

    def test_calculate_left_hand_limit_of_absolute_value_quotient(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "left-hand-limit-of-absolute-value-quotient"},
            ),
            {"point": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Limit = -1")

    def test_calculate_right_hand_limit_of_absolute_value_quotient(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "right-hand-limit-of-absolute-value-quotient"},
            ),
            {"point": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Limit = 1")

    def test_calculate_maximum_volume_closed_cylinder(self):
        response = self.client.post(
            reverse(
                "calculus:calculate",
                kwargs={"slug": "maximum-volume-of-closed-cylinder-with-fixed-surface-area"},
            ),
            {"surface_area": "600"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maximum volume = 1128.3791670955")

    def test_calculate_water_level_rate_in_conical_tank(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "water-level-rate-in-conical-tank"}),
            {"tank_radius": "3", "tank_height": "6", "water_depth": "2", "volume_rate": "6.2831853072"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dh/dt = 2")

    def test_calculate_definite_integral_of_sine_squared(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "definite-integral-of-sine-squared"}),
            {"coefficient": "2", "rate": "1", "lower_bound": "0", "upper_bound": "1.5707963268"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integral = 1.5707963268")

    def test_calculate_definite_integral_of_cosine_squared(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "definite-integral-of-cosine-squared"}),
            {"coefficient": "2", "rate": "1", "lower_bound": "0", "upper_bound": "1.5707963268"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integral = 1.5707963268")

    def test_calculate_definite_integral_of_secant_times_tangent(self):
        response = self.client.post(
            reverse("calculus:calculate", kwargs={"slug": "definite-integral-of-secant-times-tangent"}),
            {"coefficient": "1", "rate": "1", "lower_bound": "0", "upper_bound": "1.0471975512"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Integral = 1")
