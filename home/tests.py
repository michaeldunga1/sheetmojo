from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Calculator


class HomeAppTests(TestCase):
    def test_home_loads(self):
        response = self.client.get(reverse("home:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Explore Calculator Apps")
        self.assertContains(response, "Volume")
        self.assertContains(response, "Agriculture")

    def test_list_view_mode(self):
        response = self.client.get(reverse("home:index"), {"view": "list"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List View")
        self.assertContains(response, "Open App")

    def test_invalid_view_defaults_to_grid(self):
        response = self.client.get(reverse("home:index"), {"view": "unknown"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grid View")

    def test_add_calculator_requires_login(self):
        response = self.client.get(reverse("add-calculator"))
        self.assertEqual(response.status_code, 302)

    def test_add_calculator_forbidden_for_non_superuser(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="regular", password="pass12345")
        self.client.force_login(user)

        response = self.client.get(reverse("add-calculator"))
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_add_calculator(self):
        user_model = get_user_model()
        admin = user_model.objects.create_superuser(
            username="admin",
            password="pass12345",
            email="admin@example.com",
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse("add-calculator"),
            {
                "calculator_name": "Ohms Law",
                "url": "/electronics/ohms-law/",
                "domain": "electronics",
                "tags": "ohm,voltage,current",
                "description": "Basic circuit calculator.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Calculator.objects.count(), 1)
        calc = Calculator.objects.get()
        self.assertEqual(calc.created_by, admin)

    def test_update_calculator_forbidden_for_non_superuser(self):
        user_model = get_user_model()
        admin = user_model.objects.create_superuser(
            username="admin2",
            password="pass12345",
            email="admin2@example.com",
        )
        regular = user_model.objects.create_user(username="regular2", password="pass12345")
        calc = Calculator.objects.create(
            calculator_name="Original Name",
            url="/original/",
            domain="physics",
            tags="force",
            description="Original description",
            created_by=admin,
        )

        self.client.force_login(regular)
        response = self.client.get(reverse("update-calculator", kwargs={"pk": calc.pk}))
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_update_calculator(self):
        user_model = get_user_model()
        admin = user_model.objects.create_superuser(
            username="admin3",
            password="pass12345",
            email="admin3@example.com",
        )
        calc = Calculator.objects.create(
            calculator_name="Before",
            url="/before/",
            domain="math",
            tags="algebra",
            description="Before description",
            created_by=admin,
        )

        self.client.force_login(admin)
        response = self.client.post(
            reverse("update-calculator", kwargs={"pk": calc.pk}),
            {
                "calculator_name": "After",
                "url": "/after/",
                "domain": "mathematics",
                "tags": "algebra,updated",
                "description": "After description",
            },
        )

        self.assertEqual(response.status_code, 302)
        calc.refresh_from_db()
        self.assertEqual(calc.calculator_name, "After")
        self.assertEqual(calc.url, "/after/")

    def test_calculator_list_requires_login(self):
        response = self.client.get(reverse("calculator-list"))
        self.assertEqual(response.status_code, 302)

    def test_calculator_list_forbidden_for_non_superuser(self):
        user_model = get_user_model()
        regular = user_model.objects.create_user(username="regular3", password="pass12345")
        self.client.force_login(regular)

        response = self.client.get(reverse("calculator-list"))
        self.assertEqual(response.status_code, 403)

    def test_calculator_list_visible_to_superuser(self):
        user_model = get_user_model()
        admin = user_model.objects.create_superuser(
            username="admin4",
            password="pass12345",
            email="admin4@example.com",
        )
        Calculator.objects.create(
            calculator_name="BMI",
            url="/health/bmi/",
            domain="health",
            tags="bmi,weight,height",
            description="Body mass index calculator",
            created_by=admin,
        )

        self.client.force_login(admin)
        response = self.client.get(reverse("calculator-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage Calculators")
        self.assertContains(response, "BMI")

    def test_delete_calculator_requires_login(self):
        user_model = get_user_model()
        admin = user_model.objects.create_superuser(
            username="admin5",
            password="pass12345",
            email="admin5@example.com",
        )
        calc = Calculator.objects.create(
            calculator_name="Delete Me",
            url="/delete-me/",
            domain="misc",
            tags="delete",
            description="Delete target",
            created_by=admin,
        )

        response = self.client.get(reverse("delete-calculator", kwargs={"pk": calc.pk}))
        self.assertEqual(response.status_code, 302)

    def test_delete_calculator_forbidden_for_non_superuser(self):
        user_model = get_user_model()
        admin = user_model.objects.create_superuser(
            username="admin6",
            password="pass12345",
            email="admin6@example.com",
        )
        regular = user_model.objects.create_user(username="regular4", password="pass12345")
        calc = Calculator.objects.create(
            calculator_name="Cannot Delete",
            url="/cannot-delete/",
            domain="misc",
            tags="deny",
            description="Permission check",
            created_by=admin,
        )

        self.client.force_login(regular)
        response = self.client.get(reverse("delete-calculator", kwargs={"pk": calc.pk}))
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_delete_calculator(self):
        user_model = get_user_model()
        admin = user_model.objects.create_superuser(
            username="admin7",
            password="pass12345",
            email="admin7@example.com",
        )
        calc = Calculator.objects.create(
            calculator_name="Transient",
            url="/transient/",
            domain="misc",
            tags="temp",
            description="Temporary calculator",
            created_by=admin,
        )

        self.client.force_login(admin)
        confirm_response = self.client.get(reverse("delete-calculator", kwargs={"pk": calc.pk}))
        self.assertEqual(confirm_response.status_code, 200)
        self.assertContains(confirm_response, "Delete Calculator")
        self.assertContains(confirm_response, "Transient")

        delete_response = self.client.post(reverse("delete-calculator", kwargs={"pk": calc.pk}))
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(Calculator.objects.filter(pk=calc.pk).exists())
