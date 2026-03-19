from django.test import TestCase
from django.urls import reverse


class BusinessAppTests(TestCase):
    def test_index_loads(self):
        response = self.client.get(reverse("business:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Business Calculators")
        self.assertContains(response, "Search Formulas")
        self.assertContains(response, "Profitability &amp; Pricing")
        self.assertContains(response, "Profit")

    def test_profit(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "profit"}),
            {"revenue": "1000", "cost": "700"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Profit = 300")

    def test_revenue(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "revenue"}),
            {"price": "10", "quantity": "25"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Revenue = 250")

    def test_break_even_units(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "break-even-units"}),
            {"fixed_cost": "1000", "selling_price": "20", "variable_cost_per_unit": "10"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Break-even units = 100")

    def test_gross_profit_margin(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "gross-profit-margin"}),
            {"revenue": "1000", "cogs": "600"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "GPM = 40 %")

    def test_roi(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "roi"}),
            {"gain": "1300", "investment_cost": "1000"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "ROI = 30 %")

    def test_current_ratio(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "current-ratio"}),
            {"current_assets": "500", "current_liabilities": "250"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "CR = 2")

    def test_inventory_turnover(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "inventory-turnover"}),
            {"cogs": "1200", "average_inventory": "300"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "IT = 4")

    def test_simple_interest(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "simple-interest"}),
            {"P": "1000", "r": "0.1", "t": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "I = 200")

    def test_compound_amount(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "compound-amount"}),
            {"P": "1000", "r": "0.1", "n": "1", "t": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "A = 1210")

    def test_future_value_lump_sum(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "future-value-lump-sum"}),
            {"PV": "1000", "r": "0.1", "n": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "FV = 1210")

    def test_present_value_lump_sum(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "present-value-lump-sum"}),
            {"FV": "1210", "r": "0.1", "n": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "PV = 1000")

    def test_cagr(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "cagr"}),
            {"begin_value": "100", "end_value": "121", "n": "2"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "CAGR = 10 %")

    def test_payback_period(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "payback-period"}),
            {"initial_investment": "1000", "annual_cash_inflow": "200"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "Payback period = 5")

    def test_npv(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "npv-3-period"}),
            {"cf0": "-1000", "cf1": "500", "cf2": "500", "cf3": "500", "r": "0.1"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "NPV")

    def test_error_rendered(self):
        response = self.client.post(
            reverse("business:calculate", kwargs={"slug": "current-ratio"}),
            {"current_assets": "100", "current_liabilities": "0"},
            HTTP_HX_REQUEST="true",
        )
        self.assertContains(response, "must not be zero")
