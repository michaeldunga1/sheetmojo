import importlib

from django.db import migrations

# (app_module, url_prefix, domain_display, formulas_attr, descriptions_attr)
APP_CONFIGS = [
    ("volume",           "volume",           "Volume",          "VOLUME_FORMULAS",           "VOLUME_FORMULA_DESCRIPTIONS"),
    ("area",             "area",             "Area",            "AREA_FORMULAS",             "AREA_FORMULA_DESCRIPTIONS"),
    ("calculus",         "calculus",         "Calculus",        "CALCULUS_FORMULAS",         "CALCULUS_FORMULA_DESCRIPTIONS"),
    ("algebra",          "algebra",          "Algebra",         "ALGEBRA_FORMULAS",          "ALGEBRA_FORMULA_DESCRIPTIONS"),
    ("statistics_app",   "statistics",       "Statistics",      "STATISTICS_FORMULAS",       "STATISTICS_FORMULA_DESCRIPTIONS"),
    ("matrix",           "matrix",           "Matrix",          "MATRIX_FORMULAS",           "MATRIX_FORMULA_DESCRIPTIONS"),
    ("geometry",         "geometry",         "Geometry",        "GEOMETRY_FORMULAS",         "GEOMETRY_FORMULA_DESCRIPTIONS"),
    ("trigonometry",     "trigonometry",     "Trigonometry",    "TRIGONOMETRY_FORMULAS",     "TRIGONOMETRY_FORMULA_DESCRIPTIONS"),
    ("physics",          "physics",          "Physics",         "PHYSICS_FORMULAS",          "PHYSICS_FORMULA_DESCRIPTIONS"),
    ("chemistry",        "chemistry",        "Chemistry",       "CHEMISTRY_FORMULAS",        "CHEMISTRY_FORMULA_DESCRIPTIONS"),
    ("geography",        "geography",        "Geography",       "GEOGRAPHY_FORMULAS",        "GEOGRAPHY_FORMULA_DESCRIPTIONS"),
    ("business",         "business",         "Business",        "BUSINESS_FORMULAS",         "BUSINESS_FORMULA_DESCRIPTIONS"),
    ("agriculture",      "agriculture",      "Agriculture",     "AGRICULTURE_FORMULAS",      "AGRICULTURE_FORMULA_DESCRIPTIONS"),
    ("biology",          "biology",          "Biology",         "BIOLOGY_FORMULAS",          "BIOLOGY_FORMULA_DESCRIPTIONS"),
    ("engineering",      "engineering",      "Engineering",     "ENGINEERING_FORMULAS",      "ENGINEERING_FORMULA_DESCRIPTIONS"),
    ("computing",        "computing",        "Computing",       "COMPUTING_FORMULAS",        "COMPUTING_FORMULA_DESCRIPTIONS"),
    ("cosmology",        "cosmology",        "Cosmology",       "COSMOLOGY_FORMULAS",        "COSMOLOGY_FORMULA_DESCRIPTIONS"),
    ("mathematics",      "mathematics",      "Mathematics",     "MATHEMATICS_FORMULAS",      "MATHEMATICS_FORMULA_DESCRIPTIONS"),
    ("mechanics",        "mechanics",        "Mechanics",       "MECHANICS_FORMULAS",        "MECHANICS_FORMULA_DESCRIPTIONS"),
    ("aviation",         "aviation",         "Aviation",        "AVIATION_FORMULAS",         "AVIATION_FORMULA_DESCRIPTIONS"),
    ("electronics",      "electronics",      "Electronics",     "ELECTRONICS_FORMULAS",      "ELECTRONICS_FORMULA_DESCRIPTIONS"),
    ("telecomunications","telecomunications","Telecommunications","TELECOMUNICATIONS_FORMULAS","TELECOMUNICATIONS_FORMULA_DESCRIPTIONS"),
]

_STOP_WORDS = {
    "of", "a", "an", "the", "from", "to", "in", "at", "and", "or",
    "for", "per", "by", "on", "as", "is", "its", "with",
}


def _make_tags(domain_lower, slug):
    """Build a comma-separated tags string from domain + slug words."""
    words = [w for w in slug.split("-") if w not in _STOP_WORDS and len(w) > 1]
    parts = [domain_lower] + words
    seen = set()
    result = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return ", ".join(result)[:255]


def populate_calculators(apps, schema_editor):
    Calculator = apps.get_model("home", "Calculator")
    User = apps.get_model("auth", "User")

    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        return

    for (app_module, url_prefix, domain, formulas_attr, descriptions_attr) in APP_CONFIGS:
        catalog = importlib.import_module(f"{app_module}.formula_catalog")
        formulas = getattr(catalog, formulas_attr, {})
        descriptions = getattr(catalog, descriptions_attr, {})
        domain_lower = domain.lower()

        for slug, data in formulas.items():
            title = data.get("title", slug)
            description = descriptions.get(slug) or title
            url = f"/{url_prefix}/calculate/{slug}/"
            tags = _make_tags(domain_lower, slug)

            Calculator.objects.get_or_create(
                url=url,
                defaults={
                    "calculator_name": title,
                    "domain": domain,
                    "tags": tags,
                    "description": description,
                    "created_by": superuser,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_alter_calculator_table"),
    ]

    operations = [
        migrations.RunPython(populate_calculators, migrations.RunPython.noop),
    ]
