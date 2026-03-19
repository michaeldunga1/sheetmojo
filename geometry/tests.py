from math import pi, sqrt
from django.test import TestCase
from django.urls import reverse


class GeometryAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("geometry:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Geometry Calculators")

    def test_load_form(self):
        response = self.client.get(
            reverse("geometry:load-form"), {"formula": "circumference-of-circle"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Circumference")

    # ── Circle ────────────────────────────────────────────────────────────────
    def test_circumference(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "circumference-of-circle"}),
            {"r": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "C =")

    def test_arc_length(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "arc-length"}),
            {"r": "6", "theta": "90"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "L =")

    def test_sector_area(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "sector-area"}),
            {"r": "4", "theta": "180"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A =")

    # ── Triangles ─────────────────────────────────────────────────────────────
    def test_pythagorean_hypotenuse(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "pythagorean-theorem-hypotenuse"}),
            {"a": "3", "b": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "c = 5")

    def test_pythagorean_leg(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "pythagorean-theorem-leg"}),
            {"c": "5", "a": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "b = 4")

    def test_pythagorean_leg_invalid(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "pythagorean-theorem-leg"}),
            {"c": "3", "a": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hypotenuse c must be greater than leg a")

    def test_heron_area(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "heron-triangle-area"}),
            {"a": "3", "b": "4", "c": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A = 6")

    def test_inscribed_circle(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "inscribed-circle-radius"}),
            {"a": "3", "b": "4", "c": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "r = 1")

    def test_circumscribed_circle(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "circumscribed-circle-radius"}),
            {"a": "3", "b": "4", "c": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "R = 2.5")

    # ── Rectangles ────────────────────────────────────────────────────────────
    def test_diagonal_rectangle(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "diagonal-of-rectangle"}),
            {"l": "3", "w": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "d = 5")

    # ── Polygons ──────────────────────────────────────────────────────────────
    def test_polygon_perimeter(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "regular-polygon-perimeter"}),
            {"n": "6", "s": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "P = 30")

    def test_interior_angles_sum(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "interior-angles-polygon"}),
            {"n": "6"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "S = 720°")

    def test_each_interior_angle(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "each-interior-angle-regular-polygon"}),
            {"n": "6"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "θ = 120°")

    def test_exterior_angle(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "exterior-angle-regular-polygon"}),
            {"n": "6"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "θ = 60°")

    # ── Cube ──────────────────────────────────────────────────────────────────
    def test_surface_area_cube(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "surface-area-cube"}),
            {"a": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SA = 54")

    def test_volume_cube(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "volume-cube"}),
            {"a": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V = 27")

    # ── Cuboid ────────────────────────────────────────────────────────────────
    def test_surface_area_cuboid(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "surface-area-cuboid"}),
            {"l": "2", "w": "3", "h": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SA = 52")

    def test_volume_cuboid(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "volume-cuboid"}),
            {"l": "2", "w": "3", "h": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V = 24")

    def test_diagonal_cuboid(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "diagonal-cuboid"}),
            {"l": "1", "w": "2", "h": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "d = 3")

    # ── Sphere ────────────────────────────────────────────────────────────────
    def test_surface_area_sphere(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "surface-area-sphere"}),
            {"r": "1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SA =")

    def test_volume_sphere(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "volume-sphere"}),
            {"r": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V =")

    # ── Cylinder ──────────────────────────────────────────────────────────────
    def test_lateral_surface_cylinder(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "lateral-surface-area-cylinder"}),
            {"r": "3", "h": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LSA =")

    def test_total_surface_cylinder(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "total-surface-area-cylinder"}),
            {"r": "3", "h": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TSA =")

    def test_volume_cylinder(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "volume-cylinder"}),
            {"r": "3", "h": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V =")

    # ── Cone ──────────────────────────────────────────────────────────────────
    def test_slant_height_cone(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "slant-height-cone"}),
            {"r": "3", "h": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "l = 5")

    def test_lateral_surface_cone(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "lateral-surface-area-cone"}),
            {"r": "3", "h": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LSA =")

    def test_total_surface_cone(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "total-surface-area-cone"}),
            {"r": "3", "h": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TSA =")

    def test_volume_cone(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "volume-cone"}),
            {"r": "3", "h": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V =")

    # ── Pyramid ───────────────────────────────────────────────────────────────
    def test_volume_pyramid(self):
        response = self.client.post(
            reverse("geometry:calculate", kwargs={"slug": "volume-pyramid"}),
            {"b": "12", "h": "5"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V = 20")
