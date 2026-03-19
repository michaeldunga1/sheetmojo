from math import pi, sqrt, tan, radians


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.6f}".rstrip("0").rstrip(".")


# ── helpers ────────────────────────────────────────────────────────────────────

def _triangle_hypotenuse(d):
    return sqrt(d["a"] ** 2 + d["b"] ** 2)


def _triangle_leg(d):
    if d["c"] <= d["a"]:
        raise ValueError("Hypotenuse c must be greater than leg a.")
    return sqrt(d["c"] ** 2 - d["a"] ** 2)


def _heron(d):
    a, b, c = d["a"], d["b"], d["c"]
    s = (a + b + c) / 2
    val = s * (s - a) * (s - b) * (s - c)
    if val < 0:
        raise ValueError("The given side lengths do not form a valid triangle.")
    return sqrt(val)


def _sphere_surface(d):
    return 4 * pi * d["r"] ** 2


def _sphere_volume(d):
    return (4 / 3) * pi * d["r"] ** 3


def _cylinder_lateral(d):
    return 2 * pi * d["r"] * d["h"]


def _cylinder_total(d):
    return 2 * pi * d["r"] * (d["r"] + d["h"])


def _cylinder_volume(d):
    return pi * d["r"] ** 2 * d["h"]


def _cone_slant(d):
    return sqrt(d["r"] ** 2 + d["h"] ** 2)


def _cone_lateral(d):
    return pi * d["r"] * _cone_slant(d)


def _cone_total(d):
    return pi * d["r"] * (d["r"] + _cone_slant(d))


def _cone_volume(d):
    return (1 / 3) * pi * d["r"] ** 2 * d["h"]


def _regular_polygon_perimeter(d):
    return d["n"] * d["s"]


def _regular_polygon_area(d):
    n = d["n"]
    s = d["s"]
    return (n * s ** 2) / (4 * tan(pi / n))


def _arc_length(d):
    if d["theta"] <= 0 or d["theta"] > 360:
        raise ValueError("Angle θ must be between 0° and 360°.")
    return (d["theta"] / 360) * 2 * pi * d["r"]


def _sector_area(d):
    if d["theta"] <= 0 or d["theta"] > 360:
        raise ValueError("Angle θ must be between 0° and 360°.")
    return (d["theta"] / 360) * pi * d["r"] ** 2


def _diagonal_rectangle(d):
    return sqrt(d["l"] ** 2 + d["w"] ** 2)


def _diagonal_cuboid(d):
    return sqrt(d["l"] ** 2 + d["w"] ** 2 + d["h"] ** 2)


def _surface_area_cube(d):
    return 6 * d["a"] ** 2


def _volume_cube(d):
    return d["a"] ** 3


def _surface_area_cuboid(d):
    l, w, h = d["l"], d["w"], d["h"]
    return 2 * (l * w + l * h + w * h)


def _volume_cuboid(d):
    return d["l"] * d["w"] * d["h"]


def _volume_pyramid(d):
    return (1 / 3) * d["b"] * d["h"]


def _circumference(d):
    return 2 * pi * d["r"]


def _inscribed_circle_radius(d):
    a, b, c = d["a"], d["b"], d["c"]
    s = (a + b + c) / 2
    area = _heron({"a": a, "b": b, "c": c})
    return area / s


def _circumscribed_circle_radius(d):
    a, b, c = d["a"], d["b"], d["c"]
    area = _heron({"a": a, "b": b, "c": c})
    if abs(area) < 1e-12:
        raise ValueError("Degenerate triangle: area is zero.")
    return (a * b * c) / (4 * area)


# ── catalog ────────────────────────────────────────────────────────────────────

GEOMETRY_FORMULAS = {
    # ── Circle ──────────────────────────────────────────────────────────────
    "circumference-of-circle": {
        "title": "Circumference of a Circle",
        "latex": r"C = 2\pi r",
        "fields": [{"name": "r", "label": "Radius (r)", "min": 0}],
        "compute": _circumference,
        "substitute": lambda d: f"C = 2π · ({_fmt(d['r'])})",
        "answer_label": "C",
        "format_answer": _fmt,
    },
    "arc-length": {
        "title": "Arc Length",
        "latex": r"L = \dfrac{\theta}{360} \cdot 2\pi r",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "theta", "label": "Central angle θ (degrees)", "min": 0},
        ],
        "compute": _arc_length,
        "substitute": lambda d: f"L = ({_fmt(d['theta'])} / 360) · 2π · ({_fmt(d['r'])})",
        "answer_label": "L",
        "format_answer": _fmt,
    },
    "sector-area": {
        "title": "Area of a Sector",
        "latex": r"A = \dfrac{\theta}{360} \cdot \pi r^2",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "theta", "label": "Central angle θ (degrees)", "min": 0},
        ],
        "compute": _sector_area,
        "substitute": lambda d: f"A = ({_fmt(d['theta'])} / 360) · π · ({_fmt(d['r'])})²",
        "answer_label": "A",
        "format_answer": _fmt,
    },
    # ── Triangles ────────────────────────────────────────────────────────────
    "pythagorean-theorem-hypotenuse": {
        "title": "Pythagorean Theorem — Find Hypotenuse",
        "latex": r"c = \sqrt{a^2 + b^2}",
        "fields": [
            {"name": "a", "label": "Leg a", "min": 0},
            {"name": "b", "label": "Leg b", "min": 0},
        ],
        "compute": _triangle_hypotenuse,
        "substitute": lambda d: f"c = √(({_fmt(d['a'])})² + ({_fmt(d['b'])})²)",
        "answer_label": "c",
        "format_answer": _fmt,
    },
    "pythagorean-theorem-leg": {
        "title": "Pythagorean Theorem — Find Missing Leg",
        "latex": r"b = \sqrt{c^2 - a^2}",
        "fields": [
            {"name": "c", "label": "Hypotenuse c", "min": 0},
            {"name": "a", "label": "Known leg a", "min": 0},
        ],
        "compute": _triangle_leg,
        "substitute": lambda d: f"b = √(({_fmt(d['c'])})² − ({_fmt(d['a'])})²)",
        "answer_label": "b",
        "format_answer": _fmt,
    },
    "heron-triangle-area": {
        "title": "Triangle Area — Heron's Formula",
        "latex": r"A = \sqrt{s(s-a)(s-b)(s-c)},\quad s = \tfrac{a+b+c}{2}",
        "fields": [
            {"name": "a", "label": "Side a", "min": 0},
            {"name": "b", "label": "Side b", "min": 0},
            {"name": "c", "label": "Side c", "min": 0},
        ],
        "compute": _heron,
        "substitute": lambda d: (
            f"s = ({_fmt(d['a'])} + {_fmt(d['b'])} + {_fmt(d['c'])}) / 2,  "
            f"A = √(s·(s−a)·(s−b)·(s−c))"
        ),
        "answer_label": "A",
        "format_answer": _fmt,
    },
    "inscribed-circle-radius": {
        "title": "Inscribed Circle Radius (Inradius)",
        "latex": r"r = \dfrac{A}{s}",
        "fields": [
            {"name": "a", "label": "Side a", "min": 0},
            {"name": "b", "label": "Side b", "min": 0},
            {"name": "c", "label": "Side c", "min": 0},
        ],
        "compute": _inscribed_circle_radius,
        "substitute": lambda d: "r = Area / s  (Heron's area and semi-perimeter)",
        "answer_label": "r",
        "format_answer": _fmt,
    },
    "circumscribed-circle-radius": {
        "title": "Circumscribed Circle Radius (Circumradius)",
        "latex": r"R = \dfrac{abc}{4A}",
        "fields": [
            {"name": "a", "label": "Side a", "min": 0},
            {"name": "b", "label": "Side b", "min": 0},
            {"name": "c", "label": "Side c", "min": 0},
        ],
        "compute": _circumscribed_circle_radius,
        "substitute": lambda d: f"R = ({_fmt(d['a'])} · {_fmt(d['b'])} · {_fmt(d['c'])}) / (4 · Area)",
        "answer_label": "R",
        "format_answer": _fmt,
    },
    # ── Rectangles / Squares ─────────────────────────────────────────────────
    "diagonal-of-rectangle": {
        "title": "Diagonal of a Rectangle",
        "latex": r"d = \sqrt{l^2 + w^2}",
        "fields": [
            {"name": "l", "label": "Length (l)", "min": 0},
            {"name": "w", "label": "Width (w)", "min": 0},
        ],
        "compute": _diagonal_rectangle,
        "substitute": lambda d: f"d = √(({_fmt(d['l'])})² + ({_fmt(d['w'])})²)",
        "answer_label": "d",
        "format_answer": _fmt,
    },
    # ── Regular Polygons ─────────────────────────────────────────────────────
    "regular-polygon-perimeter": {
        "title": "Perimeter of a Regular Polygon",
        "latex": r"P = n \cdot s",
        "fields": [
            {"name": "n", "label": "Number of sides (n)", "type": "integer", "min": 3},
            {"name": "s", "label": "Side length (s)", "min": 0},
        ],
        "compute": _regular_polygon_perimeter,
        "substitute": lambda d: f"P = {d['n']} · ({_fmt(d['s'])})",
        "answer_label": "P",
        "format_answer": _fmt,
    },
    "regular-polygon-area": {
        "title": "Area of a Regular Polygon",
        "latex": r"A = \dfrac{n s^2}{4 \tan(\pi/n)}",
        "fields": [
            {"name": "n", "label": "Number of sides (n)", "type": "integer", "min": 3},
            {"name": "s", "label": "Side length (s)", "min": 0},
        ],
        "compute": _regular_polygon_area,
        "substitute": lambda d: f"A = ({d['n']} · ({_fmt(d['s'])})²) / (4 · tan(π/{d['n']}))",
        "answer_label": "A",
        "format_answer": _fmt,
    },
    "interior-angles-polygon": {
        "title": "Sum of Interior Angles of a Polygon",
        "latex": r"S = (n - 2) \times 180°",
        "fields": [
            {"name": "n", "label": "Number of sides (n)", "type": "integer", "min": 3},
        ],
        "compute": lambda d: (d["n"] - 2) * 180,
        "substitute": lambda d: f"S = ({d['n']} − 2) × 180°",
        "answer_label": "S",
        "format_answer": lambda v: f"{v}°",
    },
    "each-interior-angle-regular-polygon": {
        "title": "Each Interior Angle of a Regular Polygon",
        "latex": r"\theta = \dfrac{(n-2) \times 180°}{n}",
        "fields": [
            {"name": "n", "label": "Number of sides (n)", "type": "integer", "min": 3},
        ],
        "compute": lambda d: (d["n"] - 2) * 180 / d["n"],
        "substitute": lambda d: f"θ = ({d['n']} − 2) × 180° / {d['n']}",
        "answer_label": "θ",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    "exterior-angle-regular-polygon": {
        "title": "Each Exterior Angle of a Regular Polygon",
        "latex": r"\theta = \dfrac{360°}{n}",
        "fields": [
            {"name": "n", "label": "Number of sides (n)", "type": "integer", "min": 3},
        ],
        "compute": lambda d: 360 / d["n"],
        "substitute": lambda d: f"θ = 360° / {d['n']}",
        "answer_label": "θ",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    # ── 3-D — Cube ────────────────────────────────────────────────────────────
    "surface-area-cube": {
        "title": "Surface Area of a Cube",
        "latex": r"SA = 6a^2",
        "fields": [{"name": "a", "label": "Edge length (a)", "min": 0}],
        "compute": _surface_area_cube,
        "substitute": lambda d: f"SA = 6 · ({_fmt(d['a'])})²",
        "answer_label": "SA",
        "format_answer": _fmt,
    },
    "volume-cube": {
        "title": "Volume of a Cube",
        "latex": r"V = a^3",
        "fields": [{"name": "a", "label": "Edge length (a)", "min": 0}],
        "compute": _volume_cube,
        "substitute": lambda d: f"V = ({_fmt(d['a'])})³",
        "answer_label": "V",
        "format_answer": _fmt,
    },
    # ── 3-D — Cuboid / Rectangular Prism ─────────────────────────────────────
    "surface-area-cuboid": {
        "title": "Surface Area of a Cuboid",
        "latex": r"SA = 2(lw + lh + wh)",
        "fields": [
            {"name": "l", "label": "Length (l)", "min": 0},
            {"name": "w", "label": "Width (w)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _surface_area_cuboid,
        "substitute": lambda d: f"SA = 2(({_fmt(d['l'])})·({_fmt(d['w'])}) + ({_fmt(d['l'])})·({_fmt(d['h'])}) + ({_fmt(d['w'])})·({_fmt(d['h'])}))",
        "answer_label": "SA",
        "format_answer": _fmt,
    },
    "volume-cuboid": {
        "title": "Volume of a Cuboid",
        "latex": r"V = l \times w \times h",
        "fields": [
            {"name": "l", "label": "Length (l)", "min": 0},
            {"name": "w", "label": "Width (w)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _volume_cuboid,
        "substitute": lambda d: f"V = ({_fmt(d['l'])}) × ({_fmt(d['w'])}) × ({_fmt(d['h'])})",
        "answer_label": "V",
        "format_answer": _fmt,
    },
    "diagonal-cuboid": {
        "title": "Space Diagonal of a Cuboid",
        "latex": r"d = \sqrt{l^2 + w^2 + h^2}",
        "fields": [
            {"name": "l", "label": "Length (l)", "min": 0},
            {"name": "w", "label": "Width (w)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _diagonal_cuboid,
        "substitute": lambda d: f"d = √(({_fmt(d['l'])})² + ({_fmt(d['w'])})² + ({_fmt(d['h'])})²)",
        "answer_label": "d",
        "format_answer": _fmt,
    },
    # ── 3-D — Sphere ─────────────────────────────────────────────────────────
    "surface-area-sphere": {
        "title": "Surface Area of a Sphere",
        "latex": r"SA = 4\pi r^2",
        "fields": [{"name": "r", "label": "Radius (r)", "min": 0}],
        "compute": _sphere_surface,
        "substitute": lambda d: f"SA = 4π · ({_fmt(d['r'])})²",
        "answer_label": "SA",
        "format_answer": _fmt,
    },
    "volume-sphere": {
        "title": "Volume of a Sphere",
        "latex": r"V = \dfrac{4}{3}\pi r^3",
        "fields": [{"name": "r", "label": "Radius (r)", "min": 0}],
        "compute": _sphere_volume,
        "substitute": lambda d: f"V = (4/3) · π · ({_fmt(d['r'])})³",
        "answer_label": "V",
        "format_answer": _fmt,
    },
    # ── 3-D — Cylinder ────────────────────────────────────────────────────────
    "lateral-surface-area-cylinder": {
        "title": "Lateral Surface Area of a Cylinder",
        "latex": r"LSA = 2\pi r h",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _cylinder_lateral,
        "substitute": lambda d: f"LSA = 2π · ({_fmt(d['r'])}) · ({_fmt(d['h'])})",
        "answer_label": "LSA",
        "format_answer": _fmt,
    },
    "total-surface-area-cylinder": {
        "title": "Total Surface Area of a Cylinder",
        "latex": r"TSA = 2\pi r(r + h)",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _cylinder_total,
        "substitute": lambda d: f"TSA = 2π · ({_fmt(d['r'])}) · (({_fmt(d['r'])}) + ({_fmt(d['h'])}))",
        "answer_label": "TSA",
        "format_answer": _fmt,
    },
    "volume-cylinder": {
        "title": "Volume of a Cylinder",
        "latex": r"V = \pi r^2 h",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _cylinder_volume,
        "substitute": lambda d: f"V = π · ({_fmt(d['r'])})² · ({_fmt(d['h'])})",
        "answer_label": "V",
        "format_answer": _fmt,
    },
    # ── 3-D — Cone ───────────────────────────────────────────────────────────
    "slant-height-cone": {
        "title": "Slant Height of a Cone",
        "latex": r"l = \sqrt{r^2 + h^2}",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _cone_slant,
        "substitute": lambda d: f"l = √(({_fmt(d['r'])})² + ({_fmt(d['h'])})²)",
        "answer_label": "l",
        "format_answer": _fmt,
    },
    "lateral-surface-area-cone": {
        "title": "Lateral Surface Area of a Cone",
        "latex": r"LSA = \pi r l",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _cone_lateral,
        "substitute": lambda d: f"LSA = π · ({_fmt(d['r'])}) · √(({_fmt(d['r'])})² + ({_fmt(d['h'])})²)",
        "answer_label": "LSA",
        "format_answer": _fmt,
    },
    "total-surface-area-cone": {
        "title": "Total Surface Area of a Cone",
        "latex": r"TSA = \pi r (r + l)",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _cone_total,
        "substitute": lambda d: f"TSA = π · ({_fmt(d['r'])}) · (({_fmt(d['r'])}) + l)",
        "answer_label": "TSA",
        "format_answer": _fmt,
    },
    "volume-cone": {
        "title": "Volume of a Cone",
        "latex": r"V = \dfrac{1}{3}\pi r^2 h",
        "fields": [
            {"name": "r", "label": "Radius (r)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _cone_volume,
        "substitute": lambda d: f"V = (1/3) · π · ({_fmt(d['r'])})² · ({_fmt(d['h'])})",
        "answer_label": "V",
        "format_answer": _fmt,
    },
    # ── 3-D — Pyramid ─────────────────────────────────────────────────────────
    "volume-pyramid": {
        "title": "Volume of a Pyramid",
        "latex": r"V = \dfrac{1}{3} B h",
        "fields": [
            {"name": "b", "label": "Base area (B)", "min": 0},
            {"name": "h", "label": "Height (h)", "min": 0},
        ],
        "compute": _volume_pyramid,
        "substitute": lambda d: f"V = (1/3) · ({_fmt(d['b'])}) · ({_fmt(d['h'])})",
        "answer_label": "V",
        "format_answer": _fmt,
    },
}


GEOMETRY_FORMULA_GROUPS = [
    {"title": "All Formulas", "slugs": list(GEOMETRY_FORMULAS.keys())}
]


GEOMETRY_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in GEOMETRY_FORMULAS.items()
}
