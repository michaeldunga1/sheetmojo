from django.http import Http404
from django.shortcuts import render

from .formula_catalog import (
    VOLUME_FORMULA_DESCRIPTIONS,
    VOLUME_FORMULA_GROUPS,
    VOLUME_FORMULAS,
)
from .forms import VolumeFormulaForm


def _get_formula(slug):
    formula = VOLUME_FORMULAS.get(slug)
    if not formula:
        raise Http404("Unknown volume formula")
    return formula


def _build_formula_groups():
    grouped = []
    for group in VOLUME_FORMULA_GROUPS:
        options = [
            {
                "slug": slug,
                "title": VOLUME_FORMULAS[slug]["title"],
                "description": VOLUME_FORMULA_DESCRIPTIONS.get(slug, ""),
            }
            for slug in group["slugs"]
            if slug in VOLUME_FORMULAS
        ]
        if options:
            grouped.append({"title": group["title"], "options": options})
    return grouped


def index(request):
    formula_slug = request.GET.get("formula") or next(iter(VOLUME_FORMULAS.keys()))
    formula = _get_formula(formula_slug)
    form = VolumeFormulaForm(field_specs=formula["fields"])
    context = {
        "formula_slug": formula_slug,
        "formula": formula,
        "formula_options": VOLUME_FORMULAS,
        "formula_groups": _build_formula_groups(),
        "form": form,
        "result": None,
    }
    return render(request, "volume/index.html", context)


def load_form(request):
    slug = request.GET.get("formula") or next(iter(VOLUME_FORMULAS.keys()))
    formula = _get_formula(slug)
    form = VolumeFormulaForm(field_specs=formula["fields"])
    return render(
        request,
        "volume/partials/calculator_form.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": None,
        },
    )


def calculate(request, slug):
    formula = _get_formula(slug)
    form = VolumeFormulaForm(request.POST or None, field_specs=formula["fields"])
    result = None

    if form.is_valid():
        values = form.cleaned_data
        answer = formula["compute"](values)
        definitions = ", ".join(
            f"{field['label']} = {values[field['name']]}" for field in formula["fields"]
        )
        result = {
            "answer": answer,
            "steps": [
                ("Variables & Constants", definitions),
                ("Substitution", formula["substitute"](values)),
                ("Answer", f"V = {answer}"),
            ],
        }

    return render(
        request,
        "volume/partials/calculator_result.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": result,
        },
    )
