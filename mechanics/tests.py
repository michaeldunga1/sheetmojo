from django.test import TestCase
from django.urls import reverse


class MechanicsAppTests(TestCase):
    def test_index_page_loads(self):
        response = self.client.get(reverse("mechanics:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mechanics Calculators")
        self.assertContains(response, "Kinematics")
        self.assertContains(response, "Dynamics")
        self.assertContains(response, "Final Velocity")

    def test_load_form_returns_partial(self):
        response = self.client.get(
            reverse("mechanics:load-form"),
            {"formula": "newton-force"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Newton&#x27;s Second Law")

    def test_final_velocity_calculation(self):
        response = self.client.post(
            reverse("mechanics:calculate", kwargs={"slug": "final-velocity"}),
            {"u": "10", "a": "2", "t": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Final Velocity v (m/s) = 20")

    def test_newton_force_calculation(self):
        response = self.client.post(
            reverse("mechanics:calculate", kwargs={"slug": "newton-force"}),
            {"m": "5", "a": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Force F (N) = 15")

    def test_kinetic_energy(self):
        response = self.client.post(
            reverse("mechanics:calculate", kwargs={"slug": "kinetic-energy"}),
            {"m": "2", "v": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kinetic Energy KE (J) = 16")

    def test_frequency(self):
        response = self.client.post(
            reverse("mechanics:calculate", kwargs={"slug": "frequency"}),
            {"period": "0.5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Frequency f (Hz) = 2")

    def test_density(self):
        response = self.client.post(
            reverse("mechanics:calculate", kwargs={"slug": "density"}),
            {"mass": "10", "volume": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Density rho (kg/m^3) = 5")

    def test_time_division_validation(self):
        response = self.client.post(
            reverse("mechanics:calculate", kwargs={"slug": "power"}),
            {"work": "100", "time": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Time must be greater than 0")

    def test_invalid_formula_returns_404(self):
        response = self.client.get(
            reverse("mechanics:load-form"),
            {"formula": "does-not-exist"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
