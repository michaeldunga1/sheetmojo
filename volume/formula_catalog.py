from math import pi


VOLUME_FORMULAS = {
    "volume-of-cube": {
        "title": "Volume of Cube",
        "latex": r"V = s^3",
        "fields": [
            {"name": "side", "label": "Side Length (s)", "min": 0},
        ],
        "compute": lambda d: d["side"] ** 3,
        "substitute": lambda d: f"V = ({d['side']})^3",
    },
    "volume-of-rectangular-prism": {
        "title": "Volume of Rectangular Prism",
        "latex": r"V = l \times w \times h",
        "fields": [
            {"name": "length", "label": "Length (l)", "min": 0},
            {"name": "width", "label": "Width (w)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
        ],
        "compute": lambda d: d["length"] * d["width"] * d["height"],
        "substitute": lambda d: f"V = ({d['length']}) * ({d['width']}) * ({d['height']})",
    },
    "volume-of-sphere": {
        "title": "Volume of Sphere",
        "latex": r"V = \frac{4}{3}\pi r^3",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
        ],
        "compute": lambda d: (4.0 / 3.0) * pi * (d["radius"] ** 3),
        "substitute": lambda d: f"V = (4/3) * pi * ({d['radius']})^3",
    },
    "volume-of-cylinder": {
        "title": "Volume of Cylinder",
        "latex": r"V = \pi r^2 h",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
        ],
        "compute": lambda d: pi * (d["radius"] ** 2) * d["height"],
        "substitute": lambda d: f"V = pi * ({d['radius']})^2 * ({d['height']})",
    },
    "volume-of-cone": {
        "title": "Volume of Cone",
        "latex": r"V = \frac{1}{3}\pi r^2 h",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
        ],
        "compute": lambda d: (1.0 / 3.0) * pi * (d["radius"] ** 2) * d["height"],
        "substitute": lambda d: f"V = (1/3) * pi * ({d['radius']})^2 * ({d['height']})",
    },
    "volume-of-pyramid": {
        "title": "Volume of Pyramid",
        "latex": r"V = \frac{1}{3}Bh",
        "fields": [
            {"name": "base_area", "label": "Base Area (B)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
        ],
        "compute": lambda d: (1.0 / 3.0) * d["base_area"] * d["height"],
        "substitute": lambda d: f"V = (1/3) * ({d['base_area']}) * ({d['height']})",
    },
    "volume-of-ellipsoid": {
        "title": "Volume of Ellipsoid",
        "latex": r"V = \frac{4}{3}\pi abc",
        "fields": [
            {"name": "a", "label": "Semi-axis a", "min": 0},
            {"name": "b", "label": "Semi-axis b", "min": 0},
            {"name": "c", "label": "Semi-axis c", "min": 0},
        ],
        "compute": lambda d: (4.0 / 3.0) * pi * d["a"] * d["b"] * d["c"],
        "substitute": lambda d: f"V = (4/3) * pi * ({d['a']}) * ({d['b']}) * ({d['c']})",
    },
    "volume-of-torus": {
        "title": "Volume of Torus",
        "latex": r"V = 2\pi^2 Rr^2",
        "fields": [
            {"name": "major_radius", "label": "Major Radius (R)", "min": 0},
            {"name": "minor_radius", "label": "Minor Radius (r)", "min": 0},
        ],
        "compute": lambda d: 2.0 * (pi ** 2) * d["major_radius"] * (d["minor_radius"] ** 2),
        "substitute": lambda d: f"V = 2 * pi^2 * ({d['major_radius']}) * ({d['minor_radius']})^2",
    },
}


VOLUME_FORMULA_GROUPS = [{"title": "All Formulas", "slugs": list(VOLUME_FORMULAS.keys())}]


VOLUME_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in VOLUME_FORMULAS.items()
}
