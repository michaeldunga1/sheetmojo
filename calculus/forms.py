from django import forms


class CalculusFormulaForm(forms.Form):
    def __init__(self, *args, field_specs=None, **kwargs):
        super().__init__(*args, **kwargs)
        for spec in field_specs or []:
            self.fields[spec["name"]] = forms.FloatField(
                label=spec["label"],
                min_value=spec.get("min"),
                required=True,
                widget=forms.NumberInput(
                    attrs={
                        "class": "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2",
                        "step": "any",
                        "placeholder": f"Enter {spec['label']}",
                    }
                ),
            )
