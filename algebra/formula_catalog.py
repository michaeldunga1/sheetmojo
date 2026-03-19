from math import sqrt, log


def _fmt(value):
    """Format a float cleanly: drop trailing zeros, show int when whole."""
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.6f}".rstrip("0").rstrip(".")


# ── helpers ────────────────────────────────────────────────────────────────────

def _quadratic_roots(d):
    a, b, c = d["a"], d["b"], d["c"]
    if abs(a) < 1e-12:
        raise ValueError("Coefficient a must be non-zero for a quadratic equation.")
    disc = b ** 2 - 4 * a * c
    if disc < 0:
        real = -b / (2 * a)
        imag = sqrt(-disc) / (2 * a)
        return f"x₁ = {_fmt(real)} + {_fmt(imag)}i,  x₂ = {_fmt(real)} − {_fmt(imag)}i"
    elif abs(disc) < 1e-12:
        x = -b / (2 * a)
        return f"x = {_fmt(x)}  (double root)"
    else:
        x1 = (-b + sqrt(disc)) / (2 * a)
        x2 = (-b - sqrt(disc)) / (2 * a)
        return f"x₁ = {_fmt(x1)},  x₂ = {_fmt(x2)}"


def _vertex(d):
    a, b, c = d["a"], d["b"], d["c"]
    if abs(a) < 1e-12:
        raise ValueError("Coefficient a must be non-zero.")
    h = -b / (2 * a)
    k = c - b ** 2 / (4 * a)
    return f"({_fmt(h)}, {_fmt(k)})"


def _slope(d):
    if abs(d["x2"] - d["x1"]) < 1e-12:
        raise ValueError("Slope is undefined (vertical line: x₁ = x₂).")
    return (d["y2"] - d["y1"]) / (d["x2"] - d["x1"])


def _midpoint(d):
    mx = (d["x1"] + d["x2"]) / 2
    my = (d["y1"] + d["y2"]) / 2
    return f"({_fmt(mx)}, {_fmt(my)})"


def _solve_linear(d):
    if abs(d["a"]) < 1e-12:
        raise ValueError("Coefficient a must be non-zero.")
    return -d["b"] / d["a"]


def _geo_series(d):
    a, r, n = d["a1"], d["r"], int(d["n"])
    if abs(r - 1) < 1e-12:
        return float(a * n)
    return a * (1 - r ** n) / (1 - r)


def _change_of_base(d):
    if d["x"] <= 0:
        raise ValueError("Argument x must be positive.")
    if d["b"] <= 0 or abs(d["b"] - 1) < 1e-12:
        raise ValueError("Base b must be positive and not equal to 1.")
    return log(d["x"]) / log(d["b"])


def _pct_change(d):
    if abs(d["old_value"]) < 1e-12:
        raise ValueError("Old value must not be zero.")
    return (d["new_value"] - d["old_value"]) / d["old_value"] * 100


# ── catalog ────────────────────────────────────────────────────────────────────

ALGEBRA_FORMULAS = {
    # ── Quadratic ──────────────────────────────────────────────────────────────
    "quadratic-formula": {
        "title": "Quadratic Formula",
        "latex": r"x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
        "fields": [
            {"name": "a", "label": "a (x² coefficient)"},
            {"name": "b", "label": "b (x coefficient)"},
            {"name": "c", "label": "c (constant)"},
        ],
        "compute": _quadratic_roots,
        "substitute": lambda d: (
            f"x = (−({_fmt(d['b'])}) ± √(({_fmt(d['b'])})² − 4·({_fmt(d['a'])})·({_fmt(d['c'])})))"
            f" / (2·({_fmt(d['a'])}))"
        ),
        "answer_label": "Roots",
        "format_answer": lambda v: v,   # already a formatted string
    },
    "discriminant": {
        "title": "Discriminant",
        "latex": r"\Delta = b^2 - 4ac",
        "fields": [
            {"name": "a", "label": "a (x² coefficient)"},
            {"name": "b", "label": "b (x coefficient)"},
            {"name": "c", "label": "c (constant)"},
        ],
        "compute": lambda d: d["b"] ** 2 - 4 * d["a"] * d["c"],
        "substitute": lambda d: f"Δ = ({_fmt(d['b'])})² − 4·({_fmt(d['a'])})·({_fmt(d['c'])})",
        "answer_label": "Δ",
        "format_answer": _fmt,
    },
    "vertex-of-parabola": {
        "title": "Vertex of Parabola",
        "latex": r"V = \left(-\dfrac{b}{2a},\; c - \dfrac{b^2}{4a}\right)",
        "fields": [
            {"name": "a", "label": "a (x² coefficient)"},
            {"name": "b", "label": "b (x coefficient)"},
            {"name": "c", "label": "c (constant)"},
        ],
        "compute": _vertex,
        "substitute": lambda d: f"h = −({_fmt(d['b'])}) / (2·({_fmt(d['a'])})),  k = ({_fmt(d['c'])}) − ({_fmt(d['b'])})² / (4·({_fmt(d['a'])}))",
        "answer_label": "Vertex",
        "format_answer": lambda v: v,
    },
    # ── Linear ────────────────────────────────────────────────────────────────
    "solve-linear-equation": {
        "title": "Solve Linear Equation  ax + b = 0",
        "latex": r"x = -\dfrac{b}{a}",
        "fields": [
            {"name": "a", "label": "a (coefficient of x)"},
            {"name": "b", "label": "b (constant)"},
        ],
        "compute": _solve_linear,
        "substitute": lambda d: f"x = −({_fmt(d['b'])}) / ({_fmt(d['a'])})",
        "answer_label": "x",
        "format_answer": _fmt,
    },
    "slope-of-line": {
        "title": "Slope of a Line",
        "latex": r"m = \dfrac{y_2 - y_1}{x_2 - x_1}",
        "fields": [
            {"name": "x1", "label": "x₁"},
            {"name": "y1", "label": "y₁"},
            {"name": "x2", "label": "x₂"},
            {"name": "y2", "label": "y₂"},
        ],
        "compute": _slope,
        "substitute": lambda d: f"m = ({_fmt(d['y2'])} − {_fmt(d['y1'])}) / ({_fmt(d['x2'])} − {_fmt(d['x1'])})",
        "answer_label": "m",
        "format_answer": _fmt,
    },
    "distance-between-two-points": {
        "title": "Distance Between Two Points",
        "latex": r"d = \sqrt{(x_2-x_1)^2+(y_2-y_1)^2}",
        "fields": [
            {"name": "x1", "label": "x₁"},
            {"name": "y1", "label": "y₁"},
            {"name": "x2", "label": "x₂"},
            {"name": "y2", "label": "y₂"},
        ],
        "compute": lambda d: sqrt((d["x2"] - d["x1"]) ** 2 + (d["y2"] - d["y1"]) ** 2),
        "substitute": lambda d: f"d = √(({_fmt(d['x2'])} − {_fmt(d['x1'])})² + ({_fmt(d['y2'])} − {_fmt(d['y1'])})²)",
        "answer_label": "d",
        "format_answer": _fmt,
    },
    "midpoint": {
        "title": "Midpoint Formula",
        "latex": r"M = \left(\dfrac{x_1+x_2}{2},\;\dfrac{y_1+y_2}{2}\right)",
        "fields": [
            {"name": "x1", "label": "x₁"},
            {"name": "y1", "label": "y₁"},
            {"name": "x2", "label": "x₂"},
            {"name": "y2", "label": "y₂"},
        ],
        "compute": _midpoint,
        "substitute": lambda d: f"M = (({_fmt(d['x1'])} + {_fmt(d['x2'])}) / 2, ({_fmt(d['y1'])} + {_fmt(d['y2'])}) / 2)",
        "answer_label": "M",
        "format_answer": lambda v: v,
    },
    "slope-intercept-form": {
        "title": "Slope-Intercept Form  y = mx + b",
        "latex": r"y = mx + b",
        "fields": [
            {"name": "m", "label": "m (slope)"},
            {"name": "b", "label": "b (y-intercept)"},
            {"name": "x", "label": "x (input value)"},
        ],
        "compute": lambda d: d["m"] * d["x"] + d["b"],
        "substitute": lambda d: f"y = ({_fmt(d['m'])})·({_fmt(d['x'])}) + ({_fmt(d['b'])})",
        "answer_label": "y",
        "format_answer": _fmt,
    },
    # ── Sequences & Series ────────────────────────────────────────────────────
    "arithmetic-sequence-nth-term": {
        "title": "Arithmetic Sequence — nth Term",
        "latex": r"a_n = a_1 + (n-1)d",
        "fields": [
            {"name": "a1", "label": "a₁ (first term)"},
            {"name": "d", "label": "d (common difference)"},
            {"name": "n", "label": "n (term number)", "type": "integer", "min": 1},
        ],
        "compute": lambda d: d["a1"] + (d["n"] - 1) * d["d"],
        "substitute": lambda d: f"a_{d['n']} = ({_fmt(d['a1'])}) + ({d['n']} − 1)·({_fmt(d['d'])})",
        "answer_label": "aₙ",
        "format_answer": _fmt,
    },
    "arithmetic-series-sum": {
        "title": "Arithmetic Series — Sum of n Terms",
        "latex": r"S_n = \dfrac{n}{2}\left(2a_1 + (n-1)d\right)",
        "fields": [
            {"name": "a1", "label": "a₁ (first term)"},
            {"name": "d", "label": "d (common difference)"},
            {"name": "n", "label": "n (number of terms)", "type": "integer", "min": 1},
        ],
        "compute": lambda d: d["n"] / 2 * (2 * d["a1"] + (d["n"] - 1) * d["d"]),
        "substitute": lambda d: f"S_{d['n']} = ({d['n']} / 2) · (2·({_fmt(d['a1'])}) + ({d['n']} − 1)·({_fmt(d['d'])}))",
        "answer_label": "Sₙ",
        "format_answer": _fmt,
    },
    "geometric-sequence-nth-term": {
        "title": "Geometric Sequence — nth Term",
        "latex": r"a_n = a_1 \cdot r^{\,n-1}",
        "fields": [
            {"name": "a1", "label": "a₁ (first term)"},
            {"name": "r", "label": "r (common ratio)"},
            {"name": "n", "label": "n (term number)", "type": "integer", "min": 1},
        ],
        "compute": lambda d: d["a1"] * (d["r"] ** (d["n"] - 1)),
        "substitute": lambda d: f"a_{d['n']} = ({_fmt(d['a1'])}) · ({_fmt(d['r'])})^({d['n']} − 1)",
        "answer_label": "aₙ",
        "format_answer": _fmt,
    },
    "geometric-series-sum": {
        "title": "Geometric Series — Sum of n Terms",
        "latex": r"S_n = a_1 \cdot \dfrac{1 - r^n}{1 - r}",
        "fields": [
            {"name": "a1", "label": "a₁ (first term)"},
            {"name": "r", "label": "r (common ratio)"},
            {"name": "n", "label": "n (number of terms)", "type": "integer", "min": 1},
        ],
        "compute": _geo_series,
        "substitute": lambda d: f"S_{d['n']} = ({_fmt(d['a1'])}) · (1 − ({_fmt(d['r'])})^{d['n']}) / (1 − ({_fmt(d['r'])}))",
        "answer_label": "Sₙ",
        "format_answer": _fmt,
    },
    # ── Finance ───────────────────────────────────────────────────────────────
    "simple-interest": {
        "title": "Simple Interest",
        "latex": r"I = P \cdot r \cdot t",
        "fields": [
            {"name": "P", "label": "P (principal)", "min": 0},
            {"name": "r", "label": "r (annual rate, e.g. 0.05 for 5%)", "min": 0},
            {"name": "t", "label": "t (time in years)", "min": 0},
        ],
        "compute": lambda d: d["P"] * d["r"] * d["t"],
        "substitute": lambda d: f"I = ({_fmt(d['P'])}) · ({_fmt(d['r'])}) · ({_fmt(d['t'])})",
        "answer_label": "I",
        "format_answer": _fmt,
    },
    "compound-interest": {
        "title": "Compound Interest",
        "latex": r"A = P\!\left(1 + \dfrac{r}{n}\right)^{\!nt}",
        "fields": [
            {"name": "P", "label": "P (principal)", "min": 0},
            {"name": "r", "label": "r (annual rate, e.g. 0.05 for 5%)", "min": 0},
            {"name": "n", "label": "n (compounds per year)", "type": "integer", "min": 1},
            {"name": "t", "label": "t (time in years)", "min": 0},
        ],
        "compute": lambda d: d["P"] * (1 + d["r"] / d["n"]) ** (d["n"] * d["t"]),
        "substitute": lambda d: f"A = ({_fmt(d['P'])}) · (1 + {_fmt(d['r'])} / {d['n']})^({d['n']} · {_fmt(d['t'])})",
        "answer_label": "A",
        "format_answer": _fmt,
    },
    # ── Logarithms & Exponents ────────────────────────────────────────────────
    "change-of-base-logarithm": {
        "title": "Change of Base — Logarithm",
        "latex": r"\log_b x = \dfrac{\ln x}{\ln b}",
        "fields": [
            {"name": "x", "label": "x (argument)", "min": 0},
            {"name": "b", "label": "b (new base)", "min": 0},
        ],
        "compute": _change_of_base,
        "substitute": lambda d: f"log_{_fmt(d['b'])}({_fmt(d['x'])}) = ln({_fmt(d['x'])}) / ln({_fmt(d['b'])})",
        "answer_label": "log_b(x)",
        "format_answer": _fmt,
    },
    # ── Summation Formulas ────────────────────────────────────────────────────
    "sum-of-natural-numbers": {
        "title": "Sum of First n Natural Numbers",
        "latex": r"S = \dfrac{n(n+1)}{2}",
        "fields": [
            {"name": "n", "label": "n", "type": "integer", "min": 1},
        ],
        "compute": lambda d: d["n"] * (d["n"] + 1) // 2,
        "substitute": lambda d: f"S = {d['n']} · ({d['n']} + 1) / 2",
        "answer_label": "S",
        "format_answer": str,
    },
    "sum-of-squares": {
        "title": "Sum of Squares of First n Natural Numbers",
        "latex": r"S = \dfrac{n(n+1)(2n+1)}{6}",
        "fields": [
            {"name": "n", "label": "n", "type": "integer", "min": 1},
        ],
        "compute": lambda d: d["n"] * (d["n"] + 1) * (2 * d["n"] + 1) // 6,
        "substitute": lambda d: f"S = {d['n']} · ({d['n']} + 1) · (2·{d['n']} + 1) / 6",
        "answer_label": "S",
        "format_answer": str,
    },
    "sum-of-cubes": {
        "title": "Sum of Cubes of First n Natural Numbers",
        "latex": r"S = \left[\dfrac{n(n+1)}{2}\right]^2",
        "fields": [
            {"name": "n", "label": "n", "type": "integer", "min": 1},
        ],
        "compute": lambda d: (d["n"] * (d["n"] + 1) // 2) ** 2,
        "substitute": lambda d: f"S = ({d['n']} · ({d['n']} + 1) / 2)²",
        "answer_label": "S",
        "format_answer": str,
    },
    # ── Binomial / Factoring ──────────────────────────────────────────────────
    "binomial-square": {
        "title": "Binomial Square  (a + b)²",
        "latex": r"(a+b)^2 = a^2 + 2ab + b^2",
        "fields": [
            {"name": "a", "label": "a"},
            {"name": "b", "label": "b"},
        ],
        "compute": lambda d: (d["a"] + d["b"]) ** 2,
        "substitute": lambda d: f"({_fmt(d['a'])})² + 2·({_fmt(d['a'])})·({_fmt(d['b'])}) + ({_fmt(d['b'])})² = ({_fmt(d['a'])} + {_fmt(d['b'])})²",
        "answer_label": "(a+b)²",
        "format_answer": _fmt,
    },
    "binomial-difference-square": {
        "title": "Binomial Difference Square  (a − b)²",
        "latex": r"(a-b)^2 = a^2 - 2ab + b^2",
        "fields": [
            {"name": "a", "label": "a"},
            {"name": "b", "label": "b"},
        ],
        "compute": lambda d: (d["a"] - d["b"]) ** 2,
        "substitute": lambda d: f"({_fmt(d['a'])})² − 2·({_fmt(d['a'])})·({_fmt(d['b'])}) + ({_fmt(d['b'])})²",
        "answer_label": "(a−b)²",
        "format_answer": _fmt,
    },
    "difference-of-squares": {
        "title": "Difference of Squares  a² − b²",
        "latex": r"a^2 - b^2 = (a+b)(a-b)",
        "fields": [
            {"name": "a", "label": "a"},
            {"name": "b", "label": "b"},
        ],
        "compute": lambda d: (d["a"] + d["b"]) * (d["a"] - d["b"]),
        "substitute": lambda d: f"({_fmt(d['a'])} + {_fmt(d['b'])}) · ({_fmt(d['a'])} − {_fmt(d['b'])})",
        "answer_label": "a²−b²",
        "format_answer": _fmt,
    },
    # ── Percentages ───────────────────────────────────────────────────────────
    "percentage-change": {
        "title": "Percentage Change",
        "latex": r"\%\,\text{change} = \dfrac{\text{new} - \text{old}}{\text{old}} \times 100",
        "fields": [
            {"name": "old_value", "label": "Old value"},
            {"name": "new_value", "label": "New value"},
        ],
        "compute": _pct_change,
        "substitute": lambda d: f"% change = (({_fmt(d['new_value'])}) − ({_fmt(d['old_value'])})) / ({_fmt(d['old_value'])}) × 100",
        "answer_label": "% change",
        "format_answer": lambda v: f"{_fmt(v)} %",
    },
    "percentage-of-a-number": {
        "title": "Percentage of a Number",
        "latex": r"R = \dfrac{p}{100} \times x",
        "fields": [
            {"name": "p", "label": "p (percent, e.g. 25 for 25%)"},
            {"name": "x", "label": "x (the number)"},
        ],
        "compute": lambda d: d["p"] / 100 * d["x"],
        "substitute": lambda d: f"R = ({_fmt(d['p'])} / 100) × {_fmt(d['x'])}",
        "answer_label": "R",
        "format_answer": _fmt,
    },
}


ALGEBRA_FORMULA_GROUPS = [
    {
        "title": "Quadratics & Polynomials",
        "slugs": [
            "quadratic-formula",
            "discriminant",
            "vertex-of-parabola",
            "binomial-square",
            "binomial-difference-square",
            "difference-of-squares",
        ],
    },
    {
        "title": "Linear & Coordinate Geometry",
        "slugs": [
            "solve-linear-equation",
            "slope-of-line",
            "distance-between-two-points",
            "midpoint",
            "slope-intercept-form",
        ],
    },
    {
        "title": "Sequences & Summations",
        "slugs": [
            "arithmetic-sequence-nth-term",
            "arithmetic-series-sum",
            "geometric-sequence-nth-term",
            "geometric-series-sum",
            "sum-of-natural-numbers",
            "sum-of-squares",
            "sum-of-cubes",
        ],
    },
    {
        "title": "Finance & Percentages",
        "slugs": [
            "simple-interest",
            "compound-interest",
            "percentage-change",
            "percentage-of-a-number",
        ],
    },
    {
        "title": "Logs & Exponents",
        "slugs": [
            "change-of-base-logarithm",
        ],
    },
]


ALGEBRA_FORMULA_DESCRIPTIONS = {
    "quadratic-formula": "Solve second-degree equations from coefficients a, b, and c.",
    "discriminant": "Check root behavior using b squared minus 4ac.",
    "vertex-of-parabola": "Find the turning point of a quadratic graph.",
    "solve-linear-equation": "Solve the linear form ax plus b equals zero.",
    "slope-of-line": "Compute the rate of change between two points.",
    "distance-between-two-points": "Measure straight-line distance in the plane.",
    "midpoint": "Find the center point between two coordinates.",
    "slope-intercept-form": "Evaluate y from slope, intercept, and x.",
    "arithmetic-sequence-nth-term": "Get the nth term of an arithmetic progression.",
    "arithmetic-series-sum": "Sum the first n terms of an arithmetic sequence.",
    "geometric-sequence-nth-term": "Get the nth term of a geometric progression.",
    "geometric-series-sum": "Sum the first n terms of a geometric series.",
    "simple-interest": "Compute interest without compounding.",
    "compound-interest": "Compute accumulated value with periodic compounding.",
    "change-of-base-logarithm": "Rewrite logarithms in a new base.",
    "sum-of-natural-numbers": "Add the first n counting numbers quickly.",
    "sum-of-squares": "Sum the squares of the first n natural numbers.",
    "sum-of-cubes": "Sum the cubes of the first n natural numbers.",
    "binomial-square": "Expand or evaluate the square of a sum.",
    "binomial-difference-square": "Expand or evaluate the square of a difference.",
    "difference-of-squares": "Factor or evaluate a squared difference identity.",
    "percentage-change": "Measure relative increase or decrease as a percent.",
    "percentage-of-a-number": "Find a given percent of any value.",
}
