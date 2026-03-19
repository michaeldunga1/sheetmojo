from django.http import Http404
from django.shortcuts import render

from .formula_catalog import (
    MATRIX_FORMULA_DESCRIPTIONS,
    MATRIX_FORMULA_GROUPS,
    MATRIX_FORMULAS,
)
from .forms import MatrixFormulaForm


def _get_formula(slug):
    formula = MATRIX_FORMULAS.get(slug)
    if not formula:
        raise Http404("Unknown matrix formula")
    return formula


def _fmt_value(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return int(round(value))
    return value


def _build_formula_groups():
    grouped = []
    for group in MATRIX_FORMULA_GROUPS:
        options = [
            {
                "slug": slug,
                "title": MATRIX_FORMULAS[slug]["title"],
                "description": MATRIX_FORMULA_DESCRIPTIONS.get(slug, ""),
            }
            for slug in group["slugs"]
            if slug in MATRIX_FORMULAS
        ]
        if options:
            grouped.append({"title": group["title"], "options": options})
    return grouped


def index(request):
    formula_slug = request.GET.get("formula") or next(iter(MATRIX_FORMULAS.keys()))
    formula = _get_formula(formula_slug)
    form = MatrixFormulaForm(field_specs=formula["fields"])
    context = {
        "formula_slug": formula_slug,
        "formula": formula,
        "formula_options": MATRIX_FORMULAS,
        "formula_groups": _build_formula_groups(),
        "form": form,
        "result": None,
    }
    return render(request, "matrix/index.html", context)


def load_form(request):
    slug = request.GET.get("formula") or next(iter(MATRIX_FORMULAS.keys()))
    formula = _get_formula(slug)
    form = MatrixFormulaForm(field_specs=formula["fields"])
    return render(
        request,
        "matrix/partials/calculator_form.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": None,
        },
    )


def calculate(request, slug):
    formula = _get_formula(slug)
    form = MatrixFormulaForm(request.POST or None, field_specs=formula["fields"])
    result = None

    if form.is_valid():
        values = form.cleaned_data
        try:
            answer = formula["compute"](values)
            definitions = ", ".join(
                f"{field['label']} = {_fmt_value(values[field['name']])}"
                for field in formula["fields"]
            )
            formatter = formula.get("format_answer", lambda value: str(value))
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
        "matrix/partials/calculator_result.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": result,
        },
    )
