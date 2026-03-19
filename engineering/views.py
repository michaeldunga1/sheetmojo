from django.http import Http404
from django.shortcuts import render

from .formula_catalog import (
    ENGINEERING_FORMULA_DESCRIPTIONS,
    ENGINEERING_FORMULA_GROUPS,
    ENGINEERING_FORMULAS,
)
from .forms import EngineeringFormulaForm


def _get_formula(slug):
    formula = ENGINEERING_FORMULAS.get(slug)
    if not formula:
        raise Http404("Unknown engineering formula")
    return formula


def _build_formula_groups():
    grouped = []
    for group in ENGINEERING_FORMULA_GROUPS:
        options = [
            {
                "slug": slug,
                "title": ENGINEERING_FORMULAS[slug]["title"],
                "description": ENGINEERING_FORMULA_DESCRIPTIONS.get(slug, ""),
            }
            for slug in group["slugs"]
            if slug in ENGINEERING_FORMULAS
        ]
        if options:
            grouped.append({"title": group["title"], "options": options})
    return grouped


def index(request):
    formula_slug = request.GET.get("formula") or next(iter(ENGINEERING_FORMULAS.keys()))
    formula = _get_formula(formula_slug)
    form = EngineeringFormulaForm(field_specs=formula["fields"])
    context = {
        "formula_slug": formula_slug,
        "formula": formula,
        "formula_options": ENGINEERING_FORMULAS,
        "formula_groups": _build_formula_groups(),
        "form": form,
        "result": None,
    }
    return render(request, "engineering/index.html", context)


def load_form(request):
    slug = request.GET.get("formula") or next(iter(ENGINEERING_FORMULAS.keys()))
    formula = _get_formula(slug)
    form = EngineeringFormulaForm(field_specs=formula["fields"])
    return render(
        request,
        "engineering/partials/calculator_form.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": None,
        },
    )


def calculate(request, slug):
    formula = _get_formula(slug)
    form = EngineeringFormulaForm(request.POST or None, field_specs=formula["fields"])
    result = None

    if form.is_valid():
        values = form.cleaned_data
        try:
            answer = formula["compute"](values)
            definitions = ", ".join(
                f"{field['label']} = {values[field['name']]}"
                for field in formula["fields"]
            )
            formatter = formula.get("format_answer", lambda v: str(v))
            answer_label = formula.get("answer_label", "Result")
            result = {
                "answer": answer,
                "steps": [
                    ("Variables & Constants", definitions),
                    ("Substitution", formula["substitute"](values)),
                    ("Answer", f"{answer_label} = {formatter(answer)}"),
                ],
            }
        except ValueError as exc:
            form.add_error(None, str(exc))

    return render(
        request,
        "engineering/partials/calculator_result.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": result,
        },
    )
