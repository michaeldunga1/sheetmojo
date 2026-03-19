from django import forms


class BiologyFormulaForm(forms.Form):
    def __init__(self, *args, field_specs=None, **kwargs):
        super().__init__(*args, **kwargs)
        for spec in field_specs or []:
            field_type = spec.get("type", "float")
            field_class = forms.IntegerField if field_type == "integer" else forms.FloatField
            self.fields[spec["name"]] = field_class(
                label=spec["label"],
                min_value=spec.get("min"),
                max_value=spec.get("max"),
                required=True,
                widget=forms.NumberInput(
                    attrs={
                        "class": "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2",
                        "step": "1" if field_type == "integer" else "any",
                        "placeholder": f"Enter {spec['label']}",
                    }
                ),
            )
