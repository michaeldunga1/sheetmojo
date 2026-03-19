from django.test import TestCase
from django.urls import reverse


class PhysicsAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("physics:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Physics Calculators")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Mechanics &amp; Motion")
        self.assertContains(response, "Speed")

    def test_speed(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "speed"}),
            {"d": "100", "t": "20"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "v = 5")

    def test_acceleration(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "acceleration"}),
            {"dv": "30", "dt": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "a = 6")

    def test_force(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "newtons-second-law"}),
            {"m": "4", "a": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "F = 12")

    def test_kinetic_energy(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "kinetic-energy"}),
            {"m": "2", "v": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "KE = 9")

    def test_pressure(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "pressure"}),
            {"F": "100", "A": "20"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "p = 5")

    def test_ohms_voltage(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "ohms-law-voltage"}),
            {"I": "2", "R": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V = 20")

    def test_ohms_current_error(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "ohms-law-current"}),
            {"V": "10", "R": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "must not be zero")

    def test_wave_speed(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "wave-speed"}),
            {"f": "5", "lam": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "v = 10")

    def test_frequency_from_period(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "frequency-from-period"}),
            {"T": "0.5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "f = 2")

    def test_snells_theta2(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "snells-law-theta2"}),
            {"n1": "1", "theta1": "30", "n2": "1.5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "theta2")

    def test_mirror_focal_length(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "mirror-focal-length"}),
            {"u": "30", "v": "30"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "f = 15")

    def test_heat_energy(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "heat-energy"}),
            {"m": "2", "c": "4", "dT": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Q = 40")

    def test_ideal_gas_pressure(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "ideal-gas-pressure"}),
            {"n": "1", "T": "300", "V": "0.1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "P =")

    def test_centripetal_force(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "centripetal-force"}),
            {"m": "2", "v": "3", "r": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fc = 18")

    def test_projectile_range(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "projectile-range"}),
            {"v0": "10", "theta": "45", "g": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "R = 10")

    def test_projectile_max_height(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "projectile-max-height"}),
            {"v0": "10", "theta": "30", "g": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "H = 1.25")

    def test_triangle_angle_from_sides(self):
        response = self.client.post(
            reverse("physics:calculate", kwargs={"slug": "triangle-angle-from-sides"}),
            {"a": "3", "b": "4", "c": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "C = 90 deg")
