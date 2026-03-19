from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CalculatorForm
from .models import Calculator


APP_LINKS = [
    {"name": "Volume", "href": "/volume/", "description": "3D geometry and solid measurement calculators."},
    {"name": "Area", "href": "/area/", "description": "2D shape area formulas and calculators."},
    {"name": "Calculus", "href": "/calculus/", "description": "Derivatives, integrals, and tangent-line calculators."},
    {"name": "Statistics", "href": "/statistics/", "description": "Descriptive statistics and distribution helpers."},
    {"name": "Matrix", "href": "/matrix/", "description": "Matrix operations, determinants, inverses, and related tools."},
    {"name": "Algebra", "href": "/algebra/", "description": "Equations, sequences, percentages, and algebraic formulas."},
    {"name": "Geometry", "href": "/geometry/", "description": "Plane geometry, polygons, circles, and 3D measurements."},
    {"name": "Trigonometry", "href": "/trigonometry/", "description": "Trig identities, triangle solving, and inverse functions."},
    {"name": "Physics", "href": "/physics/", "description": "Mechanics, electricity, waves, optics, and thermodynamics."},
    {"name": "Chemistry", "href": "/chemistry/", "description": "Moles, gas laws, kinetics, equilibrium, and more."},
    {"name": "Geography", "href": "/geography/", "description": "Population, map scale, climatology, and physical geography tools."},
    {"name": "Business", "href": "/business/", "description": "Finance, accounting, profitability, and valuation calculators."},
    {"name": "Agriculture", "href": "/agriculture/", "description": "Crop, livestock, irrigation, soil, and farm management formulas."},
    {"name": "Biology", "href": "/biology/", "description": "Population dynamics, genetics, cells, microbiology, and ecology calculators."},
    {"name": "Engineering", "href": "/engineering/", "description": "Mechanical, civil, electrical, thermal, and fluids engineering calculators."},
    {"name": "Computing", "href": "/computing/", "description": "Number systems, architecture, networking, storage, and digital systems calculators."},
    {"name": "Cosmology", "href": "/cosmology/", "description": "Expansion, redshift, cosmic distances, and astrophysical parameter calculators."},
    {"name": "Mathematics", "href": "/mathematics/", "description": "Number theory, combinatorics, probability, series, and discrete mathematics calculators."},
    {"name": "Mechanics", "href": "/mechanics/", "description": "Kinematics, dynamics, energy, oscillations, and fluid mechanics calculators."},
    {"name": "Aviation", "href": "/aviation/", "description": "Aerodynamics, performance, atmosphere, and flight navigation calculators."},
    {"name": "Electronics", "href": "/electronics/", "description": "Circuit analysis, AC/reactive behavior, components, and electronics formulas."},
    {"name": "Telecomunications", "href": "/telecomunications/", "description": "Signal levels, link budgets, channel capacity, and transmission-line calculators."},
]


def index(request):
    view_mode = request.GET.get("view", "grid")
    if view_mode not in {"grid", "list"}:
        view_mode = "grid"

    return render(
        request,
        "home/index.html",
        {
            "apps": APP_LINKS,
            "view_mode": view_mode,
        },
    )


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "auth/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            for field in ("first_name", "last_name", "email"):
                setattr(request.user, field, form.cleaned_data[field])
            request.user.save(update_fields=["first_name", "last_name", "email"])
            return redirect("profile")
    else:
        form = ProfileForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            }
        )
    return render(request, "auth/profile.html", {"form": form})


@login_required
def dashboard(request):
    return render(
        request,
        "home/simple_page.html",
        {
            "title": "Dashboard",
            "message": "Your account dashboard will appear here.",
        },
    )


def calculator_directory(request):
    q = request.GET.get("q", "").strip()
    domain = request.GET.get("domain", "").strip()
    tag = request.GET.get("tag", "").strip()

    calculators = Calculator.objects.all()
    if q:
        from django.db.models import Q
        calculators = calculators.filter(
            Q(calculator_name__icontains=q) |
            Q(tags__icontains=q) |
            Q(description__icontains=q)
        )
    if domain:
        calculators = calculators.filter(domain__iexact=domain)
    if tag:
        calculators = calculators.filter(tags__icontains=tag)

    calculators = calculators.order_by("domain", "calculator_name")

    return render(
        request,
        "home/calculator_directory.html",
        {
            "calculators": calculators,
            "q": q,
            "active_domain": domain,
            "active_tag": tag,
            "total": calculators.count(),
        },
    )


def categories(request):
    from django.db.models import Count
    domain_counts = {
        row["domain"]: row["n"]
        for row in Calculator.objects.values("domain").annotate(n=Count("id"))
    }
    category_list = [
        {
            "name": app["name"],
            "href": app["href"],
            "description": app["description"],
            "count": domain_counts.get(app["name"], 0),
        }
        for app in APP_LINKS
    ]
    return render(
        request,
        "home/categories.html",
        {"categories": category_list},
    )


def tags(request):
    from collections import Counter
    all_tags = Calculator.objects.values_list("tags", flat=True)
    counter = Counter()
    for tag_string in all_tags:
        for t in tag_string.split(","):
            t = t.strip()
            if t:
                counter[t] += 1
    tag_list = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    return render(
        request,
        "home/tags.html",
        {"tags": tag_list},
    )


@login_required
def add_calculator(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        form = CalculatorForm(request.POST)
        if form.is_valid():
            calculator = form.save(commit=False)
            calculator.created_by = request.user
            calculator.save()
            messages.success(request, "Calculator created successfully.")
            return redirect("update-calculator", pk=calculator.pk)
    else:
        form = CalculatorForm()

    return render(
        request,
        "home/calculator_form.html",
        {
            "title": "Add Calculator",
            "submit_label": "Create Calculator",
            "form": form,
        },
    )


@login_required
def update_calculator(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied

    calculator = get_object_or_404(Calculator, pk=pk)
    if request.method == "POST":
        form = CalculatorForm(request.POST, instance=calculator)
        if form.is_valid():
            form.save()
            messages.success(request, "Calculator updated successfully.")
            return redirect("update-calculator", pk=calculator.pk)
    else:
        form = CalculatorForm(instance=calculator)

    return render(
        request,
        "home/calculator_form.html",
        {
            "title": "Update Calculator",
            "submit_label": "Update Calculator",
            "form": form,
            "calculator": calculator,
        },
    )


@login_required
def calculator_list(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    calculators = Calculator.objects.select_related("created_by").all()
    return render(
        request,
        "home/calculator_list.html",
        {
            "calculators": calculators,
        },
    )


@login_required
def delete_calculator(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied

    calculator = get_object_or_404(Calculator, pk=pk)
    if request.method == "POST":
        calculator.delete()
        messages.success(request, "Calculator deleted successfully.")
        return redirect("calculator-list")

    return render(
        request,
        "home/calculator_confirm_delete.html",
        {
            "calculator": calculator,
        },
    )


@login_required
def admin_users(request):
    return render(
        request,
        "home/simple_page.html",
        {
            "title": "User Administration",
            "message": "User administration tools will be available here.",
        },
    )


def terms_of_use(request):
    return render(request, "legal/terms.html")


def privacy_policy(request):
    return render(request, "legal/privacy.html")
