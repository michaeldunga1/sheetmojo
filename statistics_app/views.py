from django.http import Http404
from django.shortcuts import render

from .formula_catalog import (
    STATISTICS_FORMULA_DESCRIPTIONS,
    STATISTICS_FORMULA_GROUPS,
    STATISTICS_FORMULAS,
)
from .forms import StatisticsFormulaForm


def _get_formula(slug):
    formula = STATISTICS_FORMULAS.get(slug)
    if not formula:
        raise Http404("Unknown statistics formula")
    return formula


def _build_formula_groups():
    grouped = []
    for group in STATISTICS_FORMULA_GROUPS:
        options = [
            {
                "slug": slug,
                "title": STATISTICS_FORMULAS[slug]["title"],
                "description": STATISTICS_FORMULA_DESCRIPTIONS.get(slug, ""),
            }
            for slug in group["slugs"]
            if slug in STATISTICS_FORMULAS
        ]
        if options:
            grouped.append({"title": group["title"], "options": options})
    return grouped


def index(request):
    formula_slug = request.GET.get("formula") or next(iter(STATISTICS_FORMULAS.keys()))
    formula = _get_formula(formula_slug)
    form = StatisticsFormulaForm(field_specs=formula["fields"])
    context = {
        "formula_slug": formula_slug,
        "formula": formula,
        "formula_options": STATISTICS_FORMULAS,
        "formula_groups": _build_formula_groups(),
        "form": form,
        "result": None,
    }
    return render(request, "statistics/index.html", context)


def load_form(request):
    slug = request.GET.get("formula") or next(iter(STATISTICS_FORMULAS.keys()))
    formula = _get_formula(slug)
    form = StatisticsFormulaForm(field_specs=formula["fields"])
    return render(
        request,
        "statistics/partials/calculator_form.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": None,
        },
    )


def calculate(request, slug):
    formula = _get_formula(slug)
    form = StatisticsFormulaForm(request.POST or None, field_specs=formula["fields"])
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
        "statistics/partials/calculator_result.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": result,
        },
    )
