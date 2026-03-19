from django import forms


class CosmologyFormulaForm(forms.Form):
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
            elif field_type == "text":
                field_class = forms.CharField
                widget = forms.TextInput(
                    attrs={
                        "class": "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2",
                        "placeholder": spec.get("placeholder", f"Enter {spec['label']}"),
                        "spellcheck": "false",
                        "autocomplete": "off",
                    }
                )
                field_kwargs = {
                    "min_length": spec.get("min_length"),
                    "max_length": spec.get("max_length"),
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
