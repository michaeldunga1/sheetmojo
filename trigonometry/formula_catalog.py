from math import sin, cos, tan, asin, acos, atan, radians, degrees, pi, sqrt


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.6f}".rstrip("0").rstrip(".")


# ── helpers ────────────────────────────────────────────────────────────────────

def _sin_rad(d):
    return sin(d["angle"])


def _cos_rad(d):
    return cos(d["angle"])


def _tan_rad(d):
    if abs(cos(d["angle"])) < 1e-12:
        raise ValueError("tan is undefined when cos(θ) = 0 (at 90°, 270°, etc.)")
    return tan(d["angle"])


def _sin_deg(d):
    return sin(radians(d["angle"]))


def _cos_deg(d):
    return cos(radians(d["angle"]))


def _tan_deg(d):
    rad = radians(d["angle"])
    if abs(cos(rad)) < 1e-12:
        raise ValueError("tan is undefined when cos(θ) = 0 (at 90°, 270°, etc.)")
    return tan(rad)


def _asin_result(d):
    if d["value"] < -1 or d["value"] > 1:
        raise ValueError("Input must be between -1 and 1.")
    return degrees(asin(d["value"]))


def _acos_result(d):
    if d["value"] < -1 or d["value"] > 1:
        raise ValueError("Input must be between -1 and 1.")
    return degrees(acos(d["value"]))


def _atan_result(d):
    return degrees(atan(d["value"]))


def _law_of_sines_side(d):
    if d["A"] <= 0 or d["A"] >= 180:
        raise ValueError("Angle A must be between 0° and 180°.")
    if d["C"] <= 0 or d["C"] >= 180:
        raise ValueError("Angle C must be between 0° and 180°.")
    a_rad = radians(d["A"])
    c_rad = radians(d["C"])
    return d["c"] * sin(a_rad) / sin(c_rad)


def _law_of_sines_angle(d):
    if d["A"] <= 0 or d["A"] >= 180:
        raise ValueError("Angle A must be between 0° and 180°.")
    sin_val = d["b"] * sin(radians(d["A"])) / d["a"]
    if sin_val < -1 or sin_val > 1:
        raise ValueError("Invalid triangle: sin(B) out of range.")
    return degrees(asin(sin_val))


def _law_of_cosines_side(d):
    a, b = d["a"], d["b"]
    C = radians(d["C"])
    return sqrt(a ** 2 + b ** 2 - 2 * a * b * cos(C))


def _law_of_cosines_angle(d):
    a, b, c = d["a"], d["b"], d["c"]
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("Invalid triangle: side lengths do not satisfy triangle inequality.")
    val = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
    if val < -1 or val > 1:
        raise ValueError("Invalid triangle.")
    return degrees(acos(val))


def _triangle_area_sine(d):
    if d["A"] <= 0 or d["A"] >= 180:
        raise ValueError("Angle A must be between 0° and 180°.")
    return 0.5 * d["b"] * d["c"] * sin(radians(d["A"]))


def _pythagorean_identity_sin2_plus_cos2(d):
    sin_val = sin(radians(d["angle"]))
    cos_val = cos(radians(d["angle"]))
    return sin_val ** 2 + cos_val ** 2


def _sum_formula_sin(d):
    a = radians(d["A"])
    b = radians(d["B"])
    return sin(a) * cos(b) + cos(a) * sin(b)


def _sum_formula_cos(d):
    a = radians(d["A"])
    b = radians(d["B"])
    return cos(a) * cos(b) - sin(a) * sin(b)


def _difference_formula_sin(d):
    a = radians(d["A"])
    b = radians(d["B"])
    return sin(a) * cos(b) - cos(a) * sin(b)


def _difference_formula_cos(d):
    a = radians(d["A"])
    b = radians(d["B"])
    return cos(a) * cos(b) + sin(a) * sin(b)


def _double_angle_sin(d):
    angle = radians(d["angle"])
    return 2 * sin(angle) * cos(angle)


def _double_angle_cos(d):
    angle = radians(d["angle"])
    return cos(angle) ** 2 - sin(angle) ** 2


def _double_angle_tan(d):
    angle = radians(d["angle"])
    cos_val = cos(angle)
    if abs(cos_val ** 2 - sin(angle) ** 2) < 1e-12:
        raise ValueError("tan(2θ) is undefined at this angle.")
    return 2 * tan(angle) / (1 - tan(angle) ** 2)


def _half_angle_sin(d):
    angle = radians(d["angle"])
    return sqrt(abs((1 - cos(angle)) / 2))


def _half_angle_cos(d):
    angle = radians(d["angle"])
    return sqrt(abs((1 + cos(angle)) / 2))


def _complementary_angle(d):
    return 90 - d["angle"]


def _supplementary_angle(d):
    return 180 - d["angle"]


def _reference_angle(d):
    angle = d["angle"] % 360
    if 0 <= angle <= 90:
        return angle
    elif 90 < angle <= 180:
        return 180 - angle
    elif 180 < angle <= 270:
        return angle - 180
    else:
        return 360 - angle


# ── catalog ────────────────────────────────────────────────────────────────────

TRIGONOMETRY_FORMULAS = {
    # ── Basic Trig Functions ───────────────────────────────────────────────────
    "sine-radians": {
        "title": "Sine Function (Radians)",
        "latex": r"\sin(\theta)",
        "fields": [{"name": "angle", "label": "Angle θ (radians)"}],
        "compute": _sin_rad,
        "substitute": lambda d: f"sin({_fmt(d['angle'])}) radians",
        "answer_label": "sin(θ)",
        "format_answer": _fmt,
    },
    "cosine-radians": {
        "title": "Cosine Function (Radians)",
        "latex": r"\cos(\theta)",
        "fields": [{"name": "angle", "label": "Angle θ (radians)"}],
        "compute": _cos_rad,
        "substitute": lambda d: f"cos({_fmt(d['angle'])}) radians",
        "answer_label": "cos(θ)",
        "format_answer": _fmt,
    },
    "tangent-radians": {
        "title": "Tangent Function (Radians)",
        "latex": r"\tan(\theta) = \dfrac{\sin(\theta)}{\cos(\theta)}",
        "fields": [{"name": "angle", "label": "Angle θ (radians)"}],
        "compute": _tan_rad,
        "substitute": lambda d: f"tan({_fmt(d['angle'])}) = sin / cos",
        "answer_label": "tan(θ)",
        "format_answer": _fmt,
    },
    "sine-degrees": {
        "title": "Sine Function (Degrees)",
        "latex": r"\sin(\theta°)",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _sin_deg,
        "substitute": lambda d: f"sin({_fmt(d['angle'])}°)",
        "answer_label": "sin(θ°)",
        "format_answer": _fmt,
    },
    "cosine-degrees": {
        "title": "Cosine Function (Degrees)",
        "latex": r"\cos(\theta°)",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _cos_deg,
        "substitute": lambda d: f"cos({_fmt(d['angle'])}°)",
        "answer_label": "cos(θ°)",
        "format_answer": _fmt,
    },
    "tangent-degrees": {
        "title": "Tangent Function (Degrees)",
        "latex": r"\tan(\theta°) = \dfrac{\sin(\theta°)}{\cos(\theta°)}",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _tan_deg,
        "substitute": lambda d: f"tan({_fmt(d['angle'])}°) = sin / cos",
        "answer_label": "tan(θ°)",
        "format_answer": _fmt,
    },
    # ── Inverse Trig Functions ─────────────────────────────────────────────────
    "arcsine": {
        "title": "Arcsine (Inverse Sine) — Degrees",
        "latex": r"\theta = \arcsin(x)",
        "fields": [{"name": "value", "label": "Value (−1 to 1)"}],
        "compute": _asin_result,
        "substitute": lambda d: f"θ = arcsin({_fmt(d['value'])})",
        "answer_label": "θ",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    "arccosine": {
        "title": "Arccosine (Inverse Cosine) — Degrees",
        "latex": r"\theta = \arccos(x)",
        "fields": [{"name": "value", "label": "Value (−1 to 1)"}],
        "compute": _acos_result,
        "substitute": lambda d: f"θ = arccos({_fmt(d['value'])})",
        "answer_label": "θ",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    "arctangent": {
        "title": "Arctangent (Inverse Tangent) — Degrees",
        "latex": r"\theta = \arctan(x)",
        "fields": [{"name": "value", "label": "Value (any real number)"}],
        "compute": _atan_result,
        "substitute": lambda d: f"θ = arctan({_fmt(d['value'])})",
        "answer_label": "θ",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    # ── Identity ───────────────────────────────────────────────────────────────
    "pythagorean-identity": {
        "title": "Pythagorean Identity: sin²(θ) + cos²(θ)",
        "latex": r"\sin^2(\theta) + \cos^2(\theta) = 1",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _pythagorean_identity_sin2_plus_cos2,
        "substitute": lambda d: f"sin²({_fmt(d['angle'])}°) + cos²({_fmt(d['angle'])}°)",
        "answer_label": "Result",
        "format_answer": _fmt,
    },
    # ── Sum & Difference Formulas ──────────────────────────────────────────────
    "sum-formula-sine": {
        "title": "Sum Formula: sin(A + B)",
        "latex": r"\sin(A+B) = \sin A \cos B + \cos A \sin B",
        "fields": [
            {"name": "A", "label": "Angle A (degrees)"},
            {"name": "B", "label": "Angle B (degrees)"},
        ],
        "compute": _sum_formula_sin,
        "substitute": lambda d: f"sin({_fmt(d['A'])}° + {_fmt(d['B'])}°) = sin(A)cos(B) + cos(A)sin(B)",
        "answer_label": "sin(A+B)",
        "format_answer": _fmt,
    },
    "sum-formula-cosine": {
        "title": "Sum Formula: cos(A + B)",
        "latex": r"\cos(A+B) = \cos A \cos B - \sin A \sin B",
        "fields": [
            {"name": "A", "label": "Angle A (degrees)"},
            {"name": "B", "label": "Angle B (degrees)"},
        ],
        "compute": _sum_formula_cos,
        "substitute": lambda d: f"cos({_fmt(d['A'])}° + {_fmt(d['B'])}°) = cos(A)cos(B) − sin(A)sin(B)",
        "answer_label": "cos(A+B)",
        "format_answer": _fmt,
    },
    "difference-formula-sine": {
        "title": "Difference Formula: sin(A − B)",
        "latex": r"\sin(A-B) = \sin A \cos B - \cos A \sin B",
        "fields": [
            {"name": "A", "label": "Angle A (degrees)"},
            {"name": "B", "label": "Angle B (degrees)"},
        ],
        "compute": _difference_formula_sin,
        "substitute": lambda d: f"sin({_fmt(d['A'])}° − {_fmt(d['B'])}°) = sin(A)cos(B) − cos(A)sin(B)",
        "answer_label": "sin(A−B)",
        "format_answer": _fmt,
    },
    "difference-formula-cosine": {
        "title": "Difference Formula: cos(A − B)",
        "latex": r"\cos(A-B) = \cos A \cos B + \sin A \sin B",
        "fields": [
            {"name": "A", "label": "Angle A (degrees)"},
            {"name": "B", "label": "Angle B (degrees)"},
        ],
        "compute": _difference_formula_cos,
        "substitute": lambda d: f"cos({_fmt(d['A'])}° − {_fmt(d['B'])}°) = cos(A)cos(B) + sin(A)sin(B)",
        "answer_label": "cos(A−B)",
        "format_answer": _fmt,
    },
    # ── Double Angle Formulas ──────────────────────────────────────────────────
    "double-angle-sine": {
        "title": "Double Angle Formula: sin(2θ)",
        "latex": r"\sin(2\theta) = 2\sin(\theta)\cos(\theta)",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _double_angle_sin,
        "substitute": lambda d: f"sin(2 × {_fmt(d['angle'])}°) = 2·sin(θ)·cos(θ)",
        "answer_label": "sin(2θ)",
        "format_answer": _fmt,
    },
    "double-angle-cosine": {
        "title": "Double Angle Formula: cos(2θ)",
        "latex": r"\cos(2\theta) = \cos^2(\theta) - \sin^2(\theta)",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _double_angle_cos,
        "substitute": lambda d: f"cos(2 × {_fmt(d['angle'])}°) = cos²(θ) − sin²(θ)",
        "answer_label": "cos(2θ)",
        "format_answer": _fmt,
    },
    "double-angle-tangent": {
        "title": "Double Angle Formula: tan(2θ)",
        "latex": r"\tan(2\theta) = \dfrac{2\tan(\theta)}{1-\tan^2(\theta)}",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _double_angle_tan,
        "substitute": lambda d: f"tan(2 × {_fmt(d['angle'])}°) = 2·tan(θ) / (1 − tan²(θ))",
        "answer_label": "tan(2θ)",
        "format_answer": _fmt,
    },
    # ── Half Angle Formulas ────────────────────────────────────────────────────
    "half-angle-sine": {
        "title": "Half Angle Formula: sin(θ/2)",
        "latex": r"\sin(\theta/2) = \sqrt{\dfrac{1-\cos(\theta)}{2}}",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _half_angle_sin,
        "substitute": lambda d: f"sin({_fmt(d['angle'])}° / 2) = √((1 − cos(θ)) / 2)",
        "answer_label": "sin(θ/2)",
        "format_answer": _fmt,
    },
    "half-angle-cosine": {
        "title": "Half Angle Formula: cos(θ/2)",
        "latex": r"\cos(\theta/2) = \sqrt{\dfrac{1+\cos(\theta)}{2}}",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _half_angle_cos,
        "substitute": lambda d: f"cos({_fmt(d['angle'])}° / 2) = √((1 + cos(θ)) / 2)",
        "answer_label": "cos(θ/2)",
        "format_answer": _fmt,
    },
    # ── Special Angles ────────────────────────────────────────────────────────
    "complementary-angle": {
        "title": "Complementary Angle",
        "latex": r"\text{Complement} = 90° - \theta",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _complementary_angle,
        "substitute": lambda d: f"Complement = 90° − {_fmt(d['angle'])}°",
        "answer_label": "Complement",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    "supplementary-angle": {
        "title": "Supplementary Angle",
        "latex": r"\text{Supplement} = 180° - \theta",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _supplementary_angle,
        "substitute": lambda d: f"Supplement = 180° − {_fmt(d['angle'])}°",
        "answer_label": "Supplement",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    "reference-angle": {
        "title": "Reference Angle",
        "latex": r"\text{Ref angle depends on quadrant}",
        "fields": [{"name": "angle", "label": "Angle θ (degrees)"}],
        "compute": _reference_angle,
        "substitute": lambda d: f"Reference angle for {_fmt(d['angle'])}°",
        "answer_label": "Reference angle",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    # ── Triangle Solving ──────────────────────────────────────────────────────
    "law-of-sines-side": {
        "title": "Law of Sines — Find Side",
        "latex": r"\dfrac{a}{\sin A} = \dfrac{c}{\sin C}  \Rightarrow  a = \dfrac{c \sin A}{\sin C}",
        "fields": [
            {"name": "A", "label": "Angle A (degrees)", "min": 0},
            {"name": "c", "label": "Side c (opposite to C)", "min": 0},
            {"name": "C", "label": "Angle C (degrees)", "min": 0},
        ],
        "compute": _law_of_sines_side,
        "substitute": lambda d: f"a = ({_fmt(d['c'])}) · sin({_fmt(d['A'])}°) / sin({_fmt(d['C'])}°)",
        "answer_label": "Side a",
        "format_answer": _fmt,
    },
    "law-of-sines-angle": {
        "title": "Law of Sines — Find Angle",
        "latex": r"\sin B = \dfrac{b \sin A}{a}",
        "fields": [
            {"name": "A", "label": "Angle A (degrees)", "min": 0},
            {"name": "a", "label": "Side a (opposite to A)", "min": 0},
            {"name": "b", "label": "Side b", "min": 0},
        ],
        "compute": _law_of_sines_angle,
        "substitute": lambda d: f"B = arcsin(({_fmt(d['b'])}) · sin({_fmt(d['A'])}°) / ({_fmt(d['a'])}))",
        "answer_label": "Angle B",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    "law-of-cosines-side": {
        "title": "Law of Cosines — Find Side",
        "latex": r"c = \sqrt{a^2 + b^2 - 2ab\cos C}",
        "fields": [
            {"name": "a", "label": "Side a", "min": 0},
            {"name": "b", "label": "Side b", "min": 0},
            {"name": "C", "label": "Angle C (degrees)", "min": 0},
        ],
        "compute": _law_of_cosines_side,
        "substitute": lambda d: f"c = √(({_fmt(d['a'])})² + ({_fmt(d['b'])})² − 2·({_fmt(d['a'])})·({_fmt(d['b'])})·cos({_fmt(d['C'])}°))",
        "answer_label": "Side c",
        "format_answer": _fmt,
    },
    "law-of-cosines-angle": {
        "title": "Law of Cosines — Find Angle",
        "latex": r"C = \arccos\left(\dfrac{a^2 + b^2 - c^2}{2ab}\right)",
        "fields": [
            {"name": "a", "label": "Side a", "min": 0},
            {"name": "b", "label": "Side b", "min": 0},
            {"name": "c", "label": "Side c", "min": 0},
        ],
        "compute": _law_of_cosines_angle,
        "substitute": lambda d: f"C = arccos((({_fmt(d['a'])})² + ({_fmt(d['b'])})² − ({_fmt(d['c'])})²) / (2·({_fmt(d['a'])})·({_fmt(d['b'])})))",
        "answer_label": "Angle C",
        "format_answer": lambda v: f"{_fmt(v)}°",
    },
    "triangle-area-sine": {
        "title": "Triangle Area Using Sine",
        "latex": r"A = \dfrac{1}{2}bc\sin A",
        "fields": [
            {"name": "A", "label": "Angle A (degrees)"},
            {"name": "b", "label": "Side b (one side)"},
            {"name": "c", "label": "Side c (other side)"},
        ],
        "compute": _triangle_area_sine,
        "substitute": lambda d: f"A = (1/2) · ({_fmt(d['b'])}) · ({_fmt(d['c'])}) · sin({_fmt(d['A'])}°)",
        "answer_label": "Area",
        "format_answer": _fmt,
    },
}


TRIGONOMETRY_FORMULA_GROUPS = [
    {"title": "All Formulas", "slugs": list(TRIGONOMETRY_FORMULAS.keys())}
]


TRIGONOMETRY_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in TRIGONOMETRY_FORMULAS.items()
}
