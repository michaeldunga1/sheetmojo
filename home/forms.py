from django import forms

from .models import Calculator


class CalculatorForm(forms.ModelForm):
    class Meta:
        model = Calculator
        fields = ["calculator_name", "url", "domain", "tags", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
