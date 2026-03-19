from math import pi, sqrt


AREA_FORMULAS = {
    "area-of-circle": {
        "title": "Area of Circle",
        "latex": r"A = \pi r^2",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
        ],
        "compute": lambda d: pi * d["radius"] ** 2,
        "substitute": lambda d: f"A = π * ({d['radius']})²",
    },
    "area-of-square": {
        "title": "Area of Square",
        "latex": r"A = s^2",
        "fields": [
            {"name": "side", "label": "Side (s)", "min": 0},
        ],
        "compute": lambda d: d["side"] ** 2,
        "substitute": lambda d: f"A = ({d['side']})²",
    },
    "area-of-rectangle": {
        "title": "Area of Rectangle",
        "latex": r"A = l \times w",
        "fields": [
            {"name": "length", "label": "Length (l)", "min": 0},
            {"name": "width", "label": "Width (w)", "min": 0},
        ],
        "compute": lambda d: d["length"] * d["width"],
        "substitute": lambda d: f"A = ({d['length']}) * ({d['width']})",
    },
    "area-of-triangle": {
        "title": "Area of Triangle",
        "latex": r"A = \frac{1}{2}bh",
        "fields": [
            {"name": "base", "label": "Base (b)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
        ],
        "compute": lambda d: 0.5 * d["base"] * d["height"],
        "substitute": lambda d: f"A = (1/2) * ({d['base']}) * ({d['height']})",
    },
    "area-of-trapezoid": {
        "title": "Area of Trapezoid",
        "latex": r"A = \frac{1}{2}(a + b)h",
        "fields": [
            {"name": "base1", "label": "Base 1 (a)", "min": 0},
            {"name": "base2", "label": "Base 2 (b)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
        ],
        "compute": lambda d: 0.5 * (d["base1"] + d["base2"]) * d["height"],
        "substitute": lambda d: f"A = (1/2) * (({d['base1']}) + ({d['base2']})) * ({d['height']})",
    },
    "area-of-parallelogram": {
        "title": "Area of Parallelogram",
        "latex": r"A = b \times h",
        "fields": [
            {"name": "base", "label": "Base (b)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
        ],
        "compute": lambda d: d["base"] * d["height"],
        "substitute": lambda d: f"A = ({d['base']}) * ({d['height']})",
    },
    "area-of-ellipse": {
        "title": "Area of Ellipse",
        "latex": r"A = \pi a b",
        "fields": [
            {"name": "semi_a", "label": "Semi-axis a", "min": 0},
            {"name": "semi_b", "label": "Semi-axis b", "min": 0},
        ],
        "compute": lambda d: pi * d["semi_a"] * d["semi_b"],
        "substitute": lambda d: f"A = π * ({d['semi_a']}) * ({d['semi_b']})",
    },
    "area-of-rhombus": {
        "title": "Area of Rhombus",
        "latex": r"A = \frac{d_1 \times d_2}{2}",
        "fields": [
            {"name": "diag1", "label": "Diagonal 1 (d₁)", "min": 0},
            {"name": "diag2", "label": "Diagonal 2 (d₂)", "min": 0},
        ],
        "compute": lambda d: 0.5 * d["diag1"] * d["diag2"],
        "substitute": lambda d: f"A = ({d['diag1']}) * ({d['diag2']}) / 2",
    },
    "area-of-regular-hexagon": {
        "title": "Area of Regular Hexagon",
        "latex": r"A = \frac{3\sqrt{3}}{2} s^2",
        "fields": [
            {"name": "side", "label": "Side Length (s)", "min": 0},
        ],
        "compute": lambda d: (3 * sqrt(3) / 2) * d["side"] ** 2,
        "substitute": lambda d: f"A = (3√3 / 2) * ({d['side']})²",
    },
    "area-of-sector": {
        "title": "Area of Sector",
        "latex": r"A = \frac{1}{2} r^2 \theta",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "angle", "label": "Angle θ (radians)", "min": 0},
        ],
        "compute": lambda d: 0.5 * d["radius"] ** 2 * d["angle"],
        "substitute": lambda d: f"A = (1/2) * ({d['radius']})² * ({d['angle']})",
    },
}


AREA_FORMULA_GROUPS = [{"title": "All Formulas", "slugs": list(AREA_FORMULAS.keys())}]


AREA_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in AREA_FORMULAS.items()
}
