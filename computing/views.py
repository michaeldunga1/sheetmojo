from django.http import Http404
from django.shortcuts import render

from .formula_catalog import (
    COMPUTING_FORMULA_DESCRIPTIONS,
    COMPUTING_FORMULA_GROUPS,
    COMPUTING_FORMULAS,
)
from .forms import ComputingFormulaForm


def _get_formula(slug):
    formula = COMPUTING_FORMULAS.get(slug)
    if not formula:
        raise Http404("Unknown computing formula")
    return formula


def _build_formula_groups():
    grouped = []
    for group in COMPUTING_FORMULA_GROUPS:
        options = [
            {
                "slug": slug,
                "title": COMPUTING_FORMULAS[slug]["title"],
                "description": COMPUTING_FORMULA_DESCRIPTIONS.get(slug, ""),
            }
            for slug in group["slugs"]
            if slug in COMPUTING_FORMULAS
        ]
        if options:
            grouped.append({"title": group["title"], "options": options})
    return grouped


def index(request):
    formula_slug = request.GET.get("formula") or next(iter(COMPUTING_FORMULAS.keys()))
    formula = _get_formula(formula_slug)
    form = ComputingFormulaForm(field_specs=formula["fields"])
    context = {
        "formula_slug": formula_slug,
        "formula": formula,
        "formula_options": COMPUTING_FORMULAS,
        "formula_groups": _build_formula_groups(),
        "form": form,
        "result": None,
    }
    return render(request, "computing/index.html", context)


def load_form(request):
    slug = request.GET.get("formula") or next(iter(COMPUTING_FORMULAS.keys()))
    formula = _get_formula(slug)
    form = ComputingFormulaForm(field_specs=formula["fields"])
    return render(
        request,
        "computing/partials/calculator_form.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": None,
        },
    )


def calculate(request, slug):
    formula = _get_formula(slug)
    form = ComputingFormulaForm(request.POST or None, field_specs=formula["fields"])
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
        "computing/partials/calculator_result.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": result,
        },
    )
