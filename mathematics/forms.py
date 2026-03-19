from django import forms


class MathematicsFormulaForm(forms.Form):
    def __init__(self, *args, field_specs=None, **kwargs):
        super().__init__(*args, **kwargs)
        for spec in field_specs or []:
            field_type = spec.get("type", "float")

            if field_type == "integer":
                field_class = forms.IntegerField
                widget = forms.NumberInput(
                    attrs={
                        "class": "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2",
                        "step": "1",
                        "placeholder": f"Enter {spec['label']}",
                    }
                )
                field_kwargs = {
                    "min_value": spec.get("min"),
                    "max_value": spec.get("max"),
                }
            else:
                field_class = forms.FloatField
                widget = forms.NumberInput(
                    attrs={
                        "class": "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2",
                        "step": "any",
                        "placeholder": f"Enter {spec['label']}",
                    }
                )
                field_kwargs = {
                    "min_value": spec.get("min"),
                    "max_value": spec.get("max"),
                }

            self.fields[spec["name"]] = field_class(
                label=spec["label"],
                required=True,
                widget=widget,
                **field_kwargs,
            )
