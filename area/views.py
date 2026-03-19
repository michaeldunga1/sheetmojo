from django.http import Http404
from django.shortcuts import render

from .formula_catalog import AREA_FORMULA_DESCRIPTIONS, AREA_FORMULA_GROUPS, AREA_FORMULAS
from .forms import AreaFormulaForm


def _get_formula(slug):
    formula = AREA_FORMULAS.get(slug)
    if not formula:
        raise Http404("Unknown area formula")
    return formula


def _build_formula_groups():
    grouped = []
    for group in AREA_FORMULA_GROUPS:
        options = [
            {
                "slug": slug,
                "title": AREA_FORMULAS[slug]["title"],
                "description": AREA_FORMULA_DESCRIPTIONS.get(slug, ""),
            }
            for slug in group["slugs"]
            if slug in AREA_FORMULAS
        ]
        if options:
            grouped.append({"title": group["title"], "options": options})
    return grouped


def index(request):
    formula_slug = request.GET.get("formula") or next(iter(AREA_FORMULAS.keys()))
    formula = _get_formula(formula_slug)
    form = AreaFormulaForm(field_specs=formula["fields"])
    context = {
        "formula_slug": formula_slug,
        "formula": formula,
        "formula_options": AREA_FORMULAS,
        "formula_groups": _build_formula_groups(),
        "form": form,
        "result": None,
    }
    return render(request, "area/index.html", context)


def load_form(request):
    slug = request.GET.get("formula") or next(iter(AREA_FORMULAS.keys()))
    formula = _get_formula(slug)
    form = AreaFormulaForm(field_specs=formula["fields"])
    return render(
        request,
        "area/partials/calculator_form.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": None,
        },
    )


def calculate(request, slug):
    formula = _get_formula(slug)
    form = AreaFormulaForm(request.POST or None, field_specs=formula["fields"])
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
                ("Answer", f"A = {answer}"),
            ],
        }

    return render(
        request,
        "area/partials/calculator_result.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": result,
        },
    )
