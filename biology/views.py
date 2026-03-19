from django.http import Http404
from django.shortcuts import render

from .formula_catalog import (
    BIOLOGY_FORMULA_DESCRIPTIONS,
    BIOLOGY_FORMULA_GROUPS,
    BIOLOGY_FORMULAS,
)
from .forms import BiologyFormulaForm


def _get_formula(slug):
    formula = BIOLOGY_FORMULAS.get(slug)
    if not formula:
        raise Http404("Unknown biology formula")
    return formula


def _build_formula_groups():
    grouped = []
    for group in BIOLOGY_FORMULA_GROUPS:
        options = [
            {
                "slug": slug,
                "title": BIOLOGY_FORMULAS[slug]["title"],
                "description": BIOLOGY_FORMULA_DESCRIPTIONS.get(slug, ""),
            }
            for slug in group["slugs"]
            if slug in BIOLOGY_FORMULAS
        ]
        if options:
            grouped.append({"title": group["title"], "options": options})
    return grouped


def index(request):
    formula_slug = request.GET.get("formula") or next(iter(BIOLOGY_FORMULAS.keys()))
    formula = _get_formula(formula_slug)
    form = BiologyFormulaForm(field_specs=formula["fields"])
    context = {
        "formula_slug": formula_slug,
        "formula": formula,
        "formula_options": BIOLOGY_FORMULAS,
        "formula_groups": _build_formula_groups(),
        "form": form,
        "result": None,
    }
    return render(request, "biology/index.html", context)


def load_form(request):
    slug = request.GET.get("formula") or next(iter(BIOLOGY_FORMULAS.keys()))
    formula = _get_formula(slug)
    form = BiologyFormulaForm(field_specs=formula["fields"])
    return render(
        request,
        "biology/partials/calculator_form.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": None,
        },
    )


def calculate(request, slug):
    formula = _get_formula(slug)
    form = BiologyFormulaForm(request.POST or None, field_specs=formula["fields"])
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
        "biology/partials/calculator_result.html",
        {
            "formula_slug": slug,
            "formula": formula,
            "form": form,
            "result": result,
        },
    )
