from django.http import Http404
from django.shortcuts import render

from .formula_catalog import (
    CALCULUS_FORMULA_DESCRIPTIONS,
    CALCULUS_FORMULA_GROUPS,
    CALCULUS_FORMULAS,
)
from .forms import CalculusFormulaForm


def _get_formula(slug):
    formula = CALCULUS_FORMULAS.get(slug)
    if not formula:
        raise Http404("Unknown calculus formula")
    return formula


def _build_formula_groups():
    grouped = []
    for group in CALCULUS_FORMULA_GROUPS:
        options = [
            {
                "slug": slug,
                "title": CALCULUS_FORMULAS[slug]["title"],
                "description": CALCULUS_FORMULA_DESCRIPTIONS.get(slug, ""),
            }
            for slug in group["slugs"]
            if slug in CALCULUS_FORMULAS
        ]
        if options:
            grouped.append({"title": group["title"], "options": options})
    return grouped


def index(request):
    formula_slug = request.GET.get("formula") or next(iter(CALCULUS_FORMULAS.keys()))
    formula = _get_formula(formula_slug)
    form = CalculusFormulaForm(field_specs=formula["fields"])
    context = {
        "formula_slug": formula_slug,
        "formula": formula,
        "formula_options": CALCULUS_FORMULAS,
        "formula_groups": _build_formula_groups(),
        "form": form,
        "result": None,
    }
    return render(request, "calculus/index.html", context)


def load_form(request):
    slug = request.GET.get("formula") or next(iter(CALCULUS_FORMULAS.keys()))
    formula = _get_formula(slug)
    form = CalculusFormulaForm(field_specs=formula["fields"])
    return render(
        request,
        "calculus/partials/calculator_form.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": None,
        },
    )


def calculate(request, slug):
    formula = _get_formula(slug)
    form = CalculusFormulaForm(request.POST or None, field_specs=formula["fields"])
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
                ("Answer", formula["answer"](values, answer)),
            ],
        }

    return render(
        request,
        "calculus/partials/calculator_result.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": result,
        },
    )
