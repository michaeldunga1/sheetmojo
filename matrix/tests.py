from django.test import TestCase
from django.urls import reverse


class MatrixAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("matrix:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Matrix Calculators")

    def test_calculate_matrix_multiplication(self):
        response = self.client.post(
            reverse("matrix:calculate", kwargs={"slug": "matrix-multiplication-2x2"}),
            {
                "a11": "1",
                "a12": "2",
                "a21": "3",
                "a22": "4",
                "b11": "5",
                "b12": "6",
                "b21": "7",
                "b22": "8",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "C = [[19, 22]; [43, 50]]")

    def test_calculate_determinant_2x2(self):
        response = self.client.post(
            reverse("matrix:calculate", kwargs={"slug": "determinant-of-2x2-matrix"}),
            {"a11": "1", "a12": "2", "a21": "3", "a22": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "det(A) = -2")

    def test_inverse_of_singular_matrix_validation(self):
        response = self.client.post(
            reverse("matrix:calculate", kwargs={"slug": "inverse-of-2x2-matrix"}),
            {"a11": "1", "a12": "2", "a21": "2", "a22": "4"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This matrix is singular, so the inverse does not exist.")

    def test_identity_matrix_order_3(self):
        response = self.client.post(
            reverse("matrix:calculate", kwargs={"slug": "identity-matrix-of-order-n"}),
            {"n": "3"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "I_n = [[1, 0, 0]; [0, 1, 0]; [0, 0, 1]]")
