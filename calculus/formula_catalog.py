from math import cos, exp, log, pi, sin, tan


def format_number(value):
    rounded = round(value, 10)
    if float(rounded).is_integer():
        return str(int(rounded))
    return f"{rounded:.10f}".rstrip("0").rstrip(".")


def derivative_power(values):
    return values["coefficient"] * values["exponent"] * (values["x_value"] ** (values["exponent"] - 1))


def second_derivative_power(values):
    return (
        values["coefficient"]
        * values["exponent"]
        * (values["exponent"] - 1)
        * (values["x_value"] ** (values["exponent"] - 2))
    )


def definite_integral_power(values):
    antiderivative_exponent = values["exponent"] + 1
    coefficient = values["coefficient"] / antiderivative_exponent
    upper_value = coefficient * (values["upper_bound"] ** antiderivative_exponent)
    lower_value = coefficient * (values["lower_bound"] ** antiderivative_exponent)
    return upper_value - lower_value


def derivative_sine(values):
    return values["amplitude"] * cos(values["x_value"])


def derivative_cosine(values):
    return -values["amplitude"] * sin(values["x_value"])


def definite_integral_sine(values):
    return values["amplitude"] * (-cos(values["upper_bound"]) + cos(values["lower_bound"]))


def definite_integral_cosine(values):
    return values["amplitude"] * (sin(values["upper_bound"]) - sin(values["lower_bound"]))


def tangent_slope_quadratic(values):
    return 2 * values["a"] * values["x_value"] + values["b"]


def tangent_line_quadratic(values):
    slope = tangent_slope_quadratic(values)
    y_value = values["a"] * (values["x_value"] ** 2) + values["b"] * values["x_value"] + values["c"]
    return (
        f"y = {format_number(slope)}(x - {format_number(values['x_value'])}) + {format_number(y_value)}"
    )


def definite_integral_linear(values):
    upper = (values["a"] / 2.0) * (values["upper_bound"] ** 2) + values["b"] * values["upper_bound"]
    lower = (values["a"] / 2.0) * (values["lower_bound"] ** 2) + values["b"] * values["lower_bound"]
    return upper - lower


def limit_of_quadratic(values):
    x_value = values["x_value"]
    return values["a"] * (x_value**2) + values["b"] * x_value + values["c"]


def average_rate_of_change_quadratic(values):
    x1 = values["x1"]
    x2 = values["x2"]
    f_x1 = values["a"] * (x1**2) + values["b"] * x1 + values["c"]
    f_x2 = values["a"] * (x2**2) + values["b"] * x2 + values["c"]
    return (f_x2 - f_x1) / (x2 - x1)


def vertex_x_quadratic(values):
    return -values["b"] / (2.0 * values["a"])


def quadratic_extremum(values):
    x_vertex = vertex_x_quadratic(values)
    y_vertex = values["a"] * (x_vertex**2) + values["b"] * x_vertex + values["c"]
    kind = "Minimum" if values["a"] > 0 else "Maximum"
    return {"kind": kind, "x": x_vertex, "y": y_vertex}


def related_rates_circle_area(values):
    return 2.0 * pi * values["radius"] * values["radius_rate"]


def related_rates_sphere_volume(values):
    return 4.0 * pi * (values["radius"] ** 2) * values["radius_rate"]


def derivative_exponential(values):
    return values["coefficient"] * values["rate"] * exp(values["rate"] * values["x_value"])


def definite_integral_exponential(values):
    rate = values["rate"]
    coefficient = values["coefficient"] / rate
    upper = coefficient * exp(rate * values["upper_bound"])
    lower = coefficient * exp(rate * values["lower_bound"])
    return upper - lower


def maximum_area_fixed_perimeter(values):
    side = values["perimeter"] / 4.0
    return {"side": side, "area": side**2}


def maximum_volume_open_top_box(values):
    cut = values["sheet_side"] / 6.0
    volume = (values["sheet_side"] - 2 * cut) ** 2 * cut
    return {"cut": cut, "volume": volume}


def related_rates_cylinder_volume(values):
    return (
        2.0 * pi * values["radius"] * values["height"] * values["radius_rate"]
        + pi * (values["radius"] ** 2) * values["height_rate"]
    )


def related_rates_sphere_surface_area(values):
    return 8.0 * pi * values["radius"] * values["radius_rate"]


def derivative_natural_log(values):
    return values["coefficient"] / values["x_value"]


def definite_integral_reciprocal(values):
    return values["coefficient"] * log(values["upper_bound"] / values["lower_bound"])


def limit_of_rational_by_cancellation(values):
    return values["coefficient"] * (2.0 * values["approach_value"])


def maximum_area_along_wall(values):
    width = values["fencing"] / 4.0
    length = values["fencing"] / 2.0
    return {"width": width, "length": length, "area": width * length}


def related_rates_sliding_ladder(values):
    x_value = values["base_distance"]
    ladder_length = values["ladder_length"]
    y_value = (ladder_length**2 - x_value**2) ** 0.5
    y_rate = -(x_value / y_value) * values["base_rate"]
    return {"height": y_value, "height_rate": y_rate}


def definite_integral_by_parts_x_exp(values):
    coefficient = values["coefficient"]
    rate = values["rate"]

    def antiderivative(x_value):
        return coefficient * exp(rate * x_value) * ((x_value / rate) - (1.0 / (rate**2)))

    return antiderivative(values["upper_bound"]) - antiderivative(values["lower_bound"])


def definite_integral_by_substitution(values):
    outer_coefficient = values["outer_coefficient"]
    inner_coefficient = values["inner_coefficient"]
    constant = values["constant"]
    exponent = values["exponent"]

    scale = outer_coefficient / (2.0 * inner_coefficient * (exponent + 1.0))

    def transformed(x_value):
        return scale * ((inner_coefficient * (x_value**2) + constant) ** (exponent + 1.0))

    return transformed(values["upper_bound"]) - transformed(values["lower_bound"])


def one_sided_limit_reciprocal(values, direction):
    coefficient = values["coefficient"]
    if direction == "left":
        return "-infinity" if coefficient > 0 else "infinity"
    return "infinity" if coefficient > 0 else "-infinity"


def related_rates_cone_volume(values):
    return (
        pi / 3.0 * (
            2.0 * values["radius"] * values["height"] * values["radius_rate"]
            + (values["radius"] ** 2) * values["height_rate"]
        )
    )


def water_level_rate_in_cylinder(values):
    return values["volume_rate"] / (pi * (values["radius"] ** 2))


def definite_integral_sec_squared(values):
    return (
        values["coefficient"] / values["rate"]
        * (tan(values["rate"] * values["upper_bound"]) - tan(values["rate"] * values["lower_bound"]))
    )


def definite_integral_sine_cosine(values):
    return (
        values["coefficient"] / (2.0 * values["rate"])
        * ((sin(values["rate"] * values["upper_bound"]) ** 2) - (sin(values["rate"] * values["lower_bound"]) ** 2))
    )


def one_sided_limit_absolute_quotient(direction):
    return -1 if direction == "left" else 1


def maximum_volume_closed_cylinder(values):
    radius = (values["surface_area"] / (6.0 * pi)) ** 0.5
    height = 2.0 * radius
    volume = pi * (radius**2) * height
    return {"radius": radius, "height": height, "volume": volume}


def water_level_rate_in_conical_tank(values):
    ratio = values["tank_radius"] / values["tank_height"]
    denominator = pi * (ratio**2) * (values["water_depth"] ** 2)
    return values["volume_rate"] / denominator


def definite_integral_sine_squared(values):
    rate = values["rate"]
    coefficient = values["coefficient"]

    def antiderivative(x_value):
        return coefficient * ((x_value / 2.0) - (sin(2.0 * rate * x_value) / (4.0 * rate)))

    return antiderivative(values["upper_bound"]) - antiderivative(values["lower_bound"])


def definite_integral_cosine_squared(values):
    rate = values["rate"]
    coefficient = values["coefficient"]

    def antiderivative(x_value):
        return coefficient * ((x_value / 2.0) + (sin(2.0 * rate * x_value) / (4.0 * rate)))

    return antiderivative(values["upper_bound"]) - antiderivative(values["lower_bound"])


def definite_integral_sec_tan(values):
    return (
        values["coefficient"] / values["rate"]
        * ((1.0 / cos(values["rate"] * values["upper_bound"])) - (1.0 / cos(values["rate"] * values["lower_bound"])))
    )


CALCULUS_FORMULAS = {
    "derivative-of-power-function-at-a-point": {
        "title": "Derivative of Power Function at a Point",
        "latex": r"f(x) = ax^n,\quad f'(x) = anx^{n-1}",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (a)"},
            {"name": "exponent", "label": "Exponent (n)", "min": 1},
            {"name": "x_value", "label": "Point x"},
        ],
        "compute": derivative_power,
        "substitute": lambda d: (
            f"f'({format_number(d['x_value'])}) = ({format_number(d['coefficient'])})"
            f"({format_number(d['exponent'])})({format_number(d['x_value'])})^({format_number(d['exponent'] - 1)})"
        ),
        "answer": lambda d, answer: f"f'({format_number(d['x_value'])}) = {format_number(answer)}",
    },
    "second-derivative-of-power-function-at-a-point": {
        "title": "Second Derivative of Power Function at a Point",
        "latex": r"f(x) = ax^n,\quad f''(x) = an(n-1)x^{n-2}",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (a)"},
            {"name": "exponent", "label": "Exponent (n)", "min": 2},
            {"name": "x_value", "label": "Point x"},
        ],
        "compute": second_derivative_power,
        "substitute": lambda d: (
            f"f''({format_number(d['x_value'])}) = ({format_number(d['coefficient'])})"
            f"({format_number(d['exponent'])})({format_number(d['exponent'] - 1)})"
            f"({format_number(d['x_value'])})^({format_number(d['exponent'] - 2)})"
        ),
        "answer": lambda d, answer: f"f''({format_number(d['x_value'])}) = {format_number(answer)}",
    },
    "definite-integral-of-power-function": {
        "title": "Definite Integral of Power Function",
        "latex": r"\int_a^b cx^n\,dx = \frac{c}{n+1}(b^{n+1} - a^{n+1})",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "exponent", "label": "Exponent (n)", "min": 0},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_power,
        "substitute": lambda d: (
            f"Integral = ({format_number(d['coefficient'])}/({format_number(d['exponent'])}+1))"
            f"(({format_number(d['upper_bound'])})^({format_number(d['exponent'] + 1)}) - "
            f"({format_number(d['lower_bound'])})^({format_number(d['exponent'] + 1)}))"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "derivative-of-sine-at-a-point": {
        "title": "Derivative of Sine at a Point",
        "latex": r"f(x) = a\sin(x),\quad f'(x) = a\cos(x)",
        "fields": [
            {"name": "amplitude", "label": "Amplitude (a)"},
            {"name": "x_value", "label": "Point x (radians)"},
        ],
        "compute": derivative_sine,
        "substitute": lambda d: (
            f"f'({format_number(d['x_value'])}) = ({format_number(d['amplitude'])})cos({format_number(d['x_value'])})"
        ),
        "answer": lambda d, answer: f"f'({format_number(d['x_value'])}) = {format_number(answer)}",
    },
    "derivative-of-cosine-at-a-point": {
        "title": "Derivative of Cosine at a Point",
        "latex": r"f(x) = a\cos(x),\quad f'(x) = -a\sin(x)",
        "fields": [
            {"name": "amplitude", "label": "Amplitude (a)"},
            {"name": "x_value", "label": "Point x (radians)"},
        ],
        "compute": derivative_cosine,
        "substitute": lambda d: (
            f"f'({format_number(d['x_value'])}) = -({format_number(d['amplitude'])})sin({format_number(d['x_value'])})"
        ),
        "answer": lambda d, answer: f"f'({format_number(d['x_value'])}) = {format_number(answer)}",
    },
    "definite-integral-of-sine": {
        "title": "Definite Integral of Sine",
        "latex": r"\int_a^b c\sin(x)\,dx = c[-\cos(x)]_a^b",
        "fields": [
            {"name": "amplitude", "label": "Amplitude (c)"},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_sine,
        "substitute": lambda d: (
            f"Integral = ({format_number(d['amplitude'])})(-cos({format_number(d['upper_bound'])}) + cos({format_number(d['lower_bound'])}))"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "definite-integral-of-cosine": {
        "title": "Definite Integral of Cosine",
        "latex": r"\int_a^b c\cos(x)\,dx = c[\sin(x)]_a^b",
        "fields": [
            {"name": "amplitude", "label": "Amplitude (c)"},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_cosine,
        "substitute": lambda d: (
            f"Integral = ({format_number(d['amplitude'])})(sin({format_number(d['upper_bound'])}) - sin({format_number(d['lower_bound'])}))"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "slope-of-tangent-to-quadratic": {
        "title": "Slope of Tangent to a Quadratic",
        "latex": r"f(x) = ax^2 + bx + c,\quad f'(x) = 2ax + b",
        "fields": [
            {"name": "a", "label": "Quadratic Coefficient (a)"},
            {"name": "b", "label": "Linear Coefficient (b)"},
            {"name": "c", "label": "Constant (c)"},
            {"name": "x_value", "label": "Point x"},
        ],
        "compute": tangent_slope_quadratic,
        "substitute": lambda d: (
            f"f'({format_number(d['x_value'])}) = 2({format_number(d['a'])})({format_number(d['x_value'])}) + {format_number(d['b'])}"
        ),
        "answer": lambda d, answer: f"Slope = {format_number(answer)}",
    },
    "tangent-line-to-quadratic": {
        "title": "Tangent Line to a Quadratic",
        "latex": r"y - f(x_0) = f'(x_0)(x - x_0)",
        "fields": [
            {"name": "a", "label": "Quadratic Coefficient (a)"},
            {"name": "b", "label": "Linear Coefficient (b)"},
            {"name": "c", "label": "Constant (c)"},
            {"name": "x_value", "label": "Point x_0"},
        ],
        "compute": tangent_line_quadratic,
        "substitute": lambda d: (
            f"Use slope f'({format_number(d['x_value'])}) = 2({format_number(d['a'])})({format_number(d['x_value'])}) + {format_number(d['b'])}"
        ),
        "answer": lambda d, answer: answer,
    },
    "definite-integral-of-linear-function": {
        "title": "Definite Integral of Linear Function",
        "latex": r"\int_m^n (ax+b)\,dx = \left[\frac{a}{2}x^2 + bx\right]_m^n",
        "fields": [
            {"name": "a", "label": "Coefficient (a)"},
            {"name": "b", "label": "Constant (b)"},
            {"name": "lower_bound", "label": "Lower Bound (m)"},
            {"name": "upper_bound", "label": "Upper Bound (n)"},
        ],
        "compute": definite_integral_linear,
        "substitute": lambda d: (
            f"Integral = [({format_number(d['a'])}/2)x^2 + ({format_number(d['b'])})x]_{{{format_number(d['lower_bound'])}}}^{{{format_number(d['upper_bound'])}}}"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "limit-of-quadratic-at-a-point": {
        "title": "Limit of a Quadratic at a Point",
        "latex": r"\lim_{x \to k}(ax^2 + bx + c) = ak^2 + bk + c",
        "fields": [
            {"name": "a", "label": "Quadratic Coefficient (a)"},
            {"name": "b", "label": "Linear Coefficient (b)"},
            {"name": "c", "label": "Constant (c)"},
            {"name": "x_value", "label": "Point k"},
        ],
        "compute": limit_of_quadratic,
        "substitute": lambda d: (
            f"lim x→{format_number(d['x_value'])}: ({format_number(d['a'])})({format_number(d['x_value'])})^2 + "
            f"({format_number(d['b'])})({format_number(d['x_value'])}) + {format_number(d['c'])}"
        ),
        "answer": lambda d, answer: f"Limit = {format_number(answer)}",
    },
    "average-rate-of-change-of-quadratic": {
        "title": "Average Rate of Change of a Quadratic",
        "latex": r"\frac{f(x_2) - f(x_1)}{x_2 - x_1}",
        "fields": [
            {"name": "a", "label": "Quadratic Coefficient (a)"},
            {"name": "b", "label": "Linear Coefficient (b)"},
            {"name": "c", "label": "Constant (c)"},
            {"name": "x1", "label": "First Point x_1"},
            {"name": "x2", "label": "Second Point x_2"},
        ],
        "compute": average_rate_of_change_quadratic,
        "substitute": lambda d: (
            f"Average rate = (f({format_number(d['x2'])}) - f({format_number(d['x1'])})) / "
            f"({format_number(d['x2'])} - {format_number(d['x1'])})"
        ),
        "answer": lambda d, answer: f"Average rate of change = {format_number(answer)}",
    },
    "vertex-of-quadratic": {
        "title": "Vertex of a Quadratic",
        "latex": r"x_v = -\frac{b}{2a}",
        "fields": [
            {"name": "a", "label": "Quadratic Coefficient (a)"},
            {"name": "b", "label": "Linear Coefficient (b)"},
            {"name": "c", "label": "Constant (c)"},
        ],
        "compute": quadratic_extremum,
        "substitute": lambda d: (
            f"x_v = -({format_number(d['b'])}) / (2({format_number(d['a'])}))"
        ),
        "answer": lambda d, answer: (
            f"{answer['kind']} at ({format_number(answer['x'])}, {format_number(answer['y'])})"
        ),
    },
    "related-rates-area-of-circle": {
        "title": "Related Rates for Area of a Circle",
        "latex": r"A = \pi r^2,\quad \frac{dA}{dt} = 2\pi r \frac{dr}{dt}",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "radius_rate", "label": "Rate dr/dt"},
        ],
        "compute": related_rates_circle_area,
        "substitute": lambda d: (
            f"dA/dt = 2π({format_number(d['radius'])})({format_number(d['radius_rate'])})"
        ),
        "answer": lambda d, answer: f"dA/dt = {format_number(answer)}",
    },
    "related-rates-volume-of-sphere": {
        "title": "Related Rates for Volume of a Sphere",
        "latex": r"V = \frac{4}{3}\pi r^3,\quad \frac{dV}{dt} = 4\pi r^2 \frac{dr}{dt}",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "radius_rate", "label": "Rate dr/dt"},
        ],
        "compute": related_rates_sphere_volume,
        "substitute": lambda d: (
            f"dV/dt = 4π({format_number(d['radius'])})^2({format_number(d['radius_rate'])})"
        ),
        "answer": lambda d, answer: f"dV/dt = {format_number(answer)}",
    },
    "derivative-of-exponential-at-a-point": {
        "title": "Derivative of an Exponential at a Point",
        "latex": r"f(x) = ae^{kx},\quad f'(x) = ake^{kx}",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (a)"},
            {"name": "rate", "label": "Exponent Rate (k)"},
            {"name": "x_value", "label": "Point x"},
        ],
        "compute": derivative_exponential,
        "substitute": lambda d: (
            f"f'({format_number(d['x_value'])}) = ({format_number(d['coefficient'])})({format_number(d['rate'])})"
            f"e^({format_number(d['rate'])}{format_number(d['x_value'])})"
        ),
        "answer": lambda d, answer: f"f'({format_number(d['x_value'])}) = {format_number(answer)}",
    },
    "definite-integral-of-exponential-function": {
        "title": "Definite Integral of an Exponential Function",
        "latex": r"\int_m^n ae^{kx}\,dx = \frac{a}{k}[e^{kx}]_m^n",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (a)"},
            {"name": "rate", "label": "Exponent Rate (k)"},
            {"name": "lower_bound", "label": "Lower Bound (m)"},
            {"name": "upper_bound", "label": "Upper Bound (n)"},
        ],
        "compute": definite_integral_exponential,
        "substitute": lambda d: (
            f"Integral = ({format_number(d['coefficient'])}/{format_number(d['rate'])})"
            f"(e^({format_number(d['rate'])}{format_number(d['upper_bound'])}) - "
            f"e^({format_number(d['rate'])}{format_number(d['lower_bound'])}))"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "maximum-area-of-rectangle-with-fixed-perimeter": {
        "title": "Maximum Area of a Rectangle with Fixed Perimeter",
        "latex": r"P = 2l + 2w,\quad A = lw,\quad A_{\max} \text{ when } l=w=\frac{P}{4}",
        "fields": [
            {"name": "perimeter", "label": "Perimeter (P)", "min": 0},
        ],
        "compute": maximum_area_fixed_perimeter,
        "substitute": lambda d: f"Side = {format_number(d['perimeter'])} / 4",
        "answer": lambda d, answer: (
            f"Maximum area = {format_number(answer['area'])} with l = w = {format_number(answer['side'])}"
        ),
    },
    "maximum-volume-of-open-top-box": {
        "title": "Maximum Volume of an Open-Top Box from a Square Sheet",
        "latex": r"V(x) = x(s-2x)^2,\quad V_{\max} \text{ at } x = \frac{s}{6}",
        "fields": [
            {"name": "sheet_side", "label": "Sheet Side Length (s)", "min": 0},
        ],
        "compute": maximum_volume_open_top_box,
        "substitute": lambda d: f"Cut size x = {format_number(d['sheet_side'])} / 6",
        "answer": lambda d, answer: (
            f"Maximum volume = {format_number(answer['volume'])} with cut size {format_number(answer['cut'])}"
        ),
    },
    "related-rates-volume-of-cylinder": {
        "title": "Related Rates for Volume of a Cylinder",
        "latex": r"V = \pi r^2 h,\quad \frac{dV}{dt} = 2\pi rh\frac{dr}{dt} + \pi r^2\frac{dh}{dt}",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
            {"name": "radius_rate", "label": "Rate dr/dt"},
            {"name": "height_rate", "label": "Rate dh/dt"},
        ],
        "compute": related_rates_cylinder_volume,
        "substitute": lambda d: (
            f"dV/dt = 2π({format_number(d['radius'])})({format_number(d['height'])})({format_number(d['radius_rate'])}) + "
            f"π({format_number(d['radius'])})^2({format_number(d['height_rate'])})"
        ),
        "answer": lambda d, answer: f"dV/dt = {format_number(answer)}",
    },
    "related-rates-surface-area-of-sphere": {
        "title": "Related Rates for Surface Area of a Sphere",
        "latex": r"A = 4\pi r^2,\quad \frac{dA}{dt} = 8\pi r\frac{dr}{dt}",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "radius_rate", "label": "Rate dr/dt"},
        ],
        "compute": related_rates_sphere_surface_area,
        "substitute": lambda d: (
            f"dA/dt = 8π({format_number(d['radius'])})({format_number(d['radius_rate'])})"
        ),
        "answer": lambda d, answer: f"dA/dt = {format_number(answer)}",
    },
    "derivative-of-natural-logarithm-at-a-point": {
        "title": "Derivative of a Natural Logarithm at a Point",
        "latex": r"f(x) = a\ln(x),\quad f'(x) = \frac{a}{x}",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (a)"},
            {"name": "x_value", "label": "Point x", "min": 0.000001},
        ],
        "compute": derivative_natural_log,
        "substitute": lambda d: (
            f"f'({format_number(d['x_value'])}) = {format_number(d['coefficient'])} / {format_number(d['x_value'])}"
        ),
        "answer": lambda d, answer: f"f'({format_number(d['x_value'])}) = {format_number(answer)}",
    },
    "definite-integral-of-reciprocal-function": {
        "title": "Definite Integral of a Reciprocal Function",
        "latex": r"\int_a^b \frac{c}{x}\,dx = c\ln\left(\frac{b}{a}\right)",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "lower_bound", "label": "Lower Bound (a)", "min": 0.000001},
            {"name": "upper_bound", "label": "Upper Bound (b)", "min": 0.000001},
        ],
        "compute": definite_integral_reciprocal,
        "substitute": lambda d: (
            f"Integral = {format_number(d['coefficient'])} ln({format_number(d['upper_bound'])} / {format_number(d['lower_bound'])})"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "limit-of-rational-function-by-cancellation": {
        "title": "Limit of a Rational Function by Cancellation",
        "latex": r"\lim_{x \to k} \frac{a(x^2-k^2)}{x-k} = a(2k)",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (a)"},
            {"name": "approach_value", "label": "Approach Value (k)"},
        ],
        "compute": limit_of_rational_by_cancellation,
        "substitute": lambda d: (
            f"After cancellation: {format_number(d['coefficient'])}(x + {format_number(d['approach_value'])}), x → {format_number(d['approach_value'])}"
        ),
        "answer": lambda d, answer: f"Limit = {format_number(answer)}",
    },
    "maximum-area-of-rectangle-along-a-wall": {
        "title": "Maximum Area of a Rectangle Along a Wall",
        "latex": r"A = x(P-2x),\quad A_{\max} \text{ when } x = \frac{P}{4}",
        "fields": [
            {"name": "fencing", "label": "Available Fencing (P)", "min": 0},
        ],
        "compute": maximum_area_along_wall,
        "substitute": lambda d: f"Width = {format_number(d['fencing'])} / 4, Length = {format_number(d['fencing'])} / 2",
        "answer": lambda d, answer: (
            f"Maximum area = {format_number(answer['area'])} with width {format_number(answer['width'])} and length {format_number(answer['length'])}"
        ),
    },
    "related-rates-sliding-ladder": {
        "title": "Related Rates for a Sliding Ladder",
        "latex": r"x^2 + y^2 = L^2,\quad x\frac{dx}{dt} + y\frac{dy}{dt} = 0",
        "fields": [
            {"name": "ladder_length", "label": "Ladder Length (L)", "min": 0},
            {"name": "base_distance", "label": "Base Distance from Wall (x)", "min": 0},
            {"name": "base_rate", "label": "Rate dx/dt"},
        ],
        "compute": related_rates_sliding_ladder,
        "substitute": lambda d: (
            f"dy/dt = -(x/y)(dx/dt) with x = {format_number(d['base_distance'])}"
        ),
        "answer": lambda d, answer: (
            f"Height = {format_number(answer['height'])}, d y/dt = {format_number(answer['height_rate'])}"
        ),
    },
    "definite-integral-by-parts-of-xe-to-kx": {
        "title": "Definite Integral by Parts of x e^(kx)",
        "latex": r"\int_a^b cxe^{kx}\,dx = c\left[e^{kx}\left(\frac{x}{k} - \frac{1}{k^2}\right)\right]_a^b",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "rate", "label": "Exponent Rate (k)"},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_by_parts_x_exp,
        "substitute": lambda d: (
            f"Integral = {format_number(d['coefficient'])}[e^({format_number(d['rate'])}x)(x/{format_number(d['rate'])} - 1/{format_number(d['rate'])}^2)]"
            f" from {format_number(d['lower_bound'])} to {format_number(d['upper_bound'])}"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "definite-integral-by-substitution-of-x-times-quadratic-power": {
        "title": "Definite Integral by Substitution of x(ax^2 + c)^n",
        "latex": r"\int_m^n b x(ax^2+c)^p\,dx = \frac{b}{2a(p+1)}[(ax^2+c)^{p+1}]_m^n",
        "fields": [
            {"name": "outer_coefficient", "label": "Outer Coefficient (b)"},
            {"name": "inner_coefficient", "label": "Inner Coefficient (a)"},
            {"name": "constant", "label": "Constant (c)"},
            {"name": "exponent", "label": "Power (p)", "min": 0},
            {"name": "lower_bound", "label": "Lower Bound (m)"},
            {"name": "upper_bound", "label": "Upper Bound (n)"},
        ],
        "compute": definite_integral_by_substitution,
        "substitute": lambda d: (
            f"Integral = ({format_number(d['outer_coefficient'])})/(2*{format_number(d['inner_coefficient'])}*({format_number(d['exponent'])}+1))"
            f"[(( {format_number(d['inner_coefficient'])}x^2 + {format_number(d['constant'])} ))^({format_number(d['exponent'] + 1)})]"
            f" from {format_number(d['lower_bound'])} to {format_number(d['upper_bound'])}"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "left-hand-limit-of-reciprocal-at-vertical-asymptote": {
        "title": "Left-Hand Limit of a Reciprocal at a Vertical Asymptote",
        "latex": r"\lim_{x \to a^-} \frac{c}{x-a}",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "asymptote", "label": "Vertical Asymptote (a)"},
        ],
        "compute": lambda d: one_sided_limit_reciprocal(d, "left"),
        "substitute": lambda d: (
            f"As x approaches {format_number(d['asymptote'])} from the left, x - a is a small negative value"
        ),
        "answer": lambda d, answer: f"Limit = {answer}",
    },
    "right-hand-limit-of-reciprocal-at-vertical-asymptote": {
        "title": "Right-Hand Limit of a Reciprocal at a Vertical Asymptote",
        "latex": r"\lim_{x \to a^+} \frac{c}{x-a}",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "asymptote", "label": "Vertical Asymptote (a)"},
        ],
        "compute": lambda d: one_sided_limit_reciprocal(d, "right"),
        "substitute": lambda d: (
            f"As x approaches {format_number(d['asymptote'])} from the right, x - a is a small positive value"
        ),
        "answer": lambda d, answer: f"Limit = {answer}",
    },
    "related-rates-volume-of-cone": {
        "title": "Related Rates for Volume of a Cone",
        "latex": r"V = \frac{1}{3}\pi r^2 h,\quad \frac{dV}{dt} = \frac{\pi}{3}\left(2rh\frac{dr}{dt} + r^2\frac{dh}{dt}\right)",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "height", "label": "Height (h)", "min": 0},
            {"name": "radius_rate", "label": "Rate dr/dt"},
            {"name": "height_rate", "label": "Rate dh/dt"},
        ],
        "compute": related_rates_cone_volume,
        "substitute": lambda d: (
            f"dV/dt = (π/3)(2({format_number(d['radius'])})({format_number(d['height'])})({format_number(d['radius_rate'])}) + "
            f"({format_number(d['radius'])})^2({format_number(d['height_rate'])}))"
        ),
        "answer": lambda d, answer: f"dV/dt = {format_number(answer)}",
    },
    "water-level-rate-in-cylinder": {
        "title": "Water Level Rate in a Cylinder",
        "latex": r"V = \pi r^2 h,\quad \frac{dh}{dt} = \frac{1}{\pi r^2}\frac{dV}{dt}",
        "fields": [
            {"name": "radius", "label": "Radius (r)", "min": 0},
            {"name": "volume_rate", "label": "Rate dV/dt"},
        ],
        "compute": water_level_rate_in_cylinder,
        "substitute": lambda d: (
            f"dh/dt = {format_number(d['volume_rate'])} / (π({format_number(d['radius'])})^2)"
        ),
        "answer": lambda d, answer: f"dh/dt = {format_number(answer)}",
    },
    "definite-integral-of-sec-squared": {
        "title": "Definite Integral of sec^2(kx)",
        "latex": r"\int_a^b c\sec^2(kx)\,dx = \frac{c}{k}[\tan(kx)]_a^b",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "rate", "label": "Frequency (k)"},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_sec_squared,
        "substitute": lambda d: (
            f"Integral = ({format_number(d['coefficient'])}/{format_number(d['rate'])})"
            f"(tan({format_number(d['rate'])}{format_number(d['upper_bound'])}) - tan({format_number(d['rate'])}{format_number(d['lower_bound'])}))"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "definite-integral-of-sine-times-cosine": {
        "title": "Definite Integral of sin(kx) cos(kx)",
        "latex": r"\int_a^b c\sin(kx)\cos(kx)\,dx = \frac{c}{2k}[\sin^2(kx)]_a^b",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "rate", "label": "Frequency (k)"},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_sine_cosine,
        "substitute": lambda d: (
            f"Integral = ({format_number(d['coefficient'])}/(2*{format_number(d['rate'])}))"
            f"(sin^2({format_number(d['rate'])}{format_number(d['upper_bound'])}) - "
            f"sin^2({format_number(d['rate'])}{format_number(d['lower_bound'])}))"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "left-hand-limit-of-absolute-value-quotient": {
        "title": "Left-Hand Limit of |x-a|/(x-a)",
        "latex": r"\lim_{x \to a^-}\frac{|x-a|}{x-a} = -1",
        "fields": [
            {"name": "point", "label": "Point a"},
        ],
        "compute": lambda d: one_sided_limit_absolute_quotient("left"),
        "substitute": lambda d: (
            f"For x < {format_number(d['point'])}, |x-a| = -(x-a)"
        ),
        "answer": lambda d, answer: f"Limit = {format_number(answer)}",
    },
    "right-hand-limit-of-absolute-value-quotient": {
        "title": "Right-Hand Limit of |x-a|/(x-a)",
        "latex": r"\lim_{x \to a^+}\frac{|x-a|}{x-a} = 1",
        "fields": [
            {"name": "point", "label": "Point a"},
        ],
        "compute": lambda d: one_sided_limit_absolute_quotient("right"),
        "substitute": lambda d: (
            f"For x > {format_number(d['point'])}, |x-a| = x-a"
        ),
        "answer": lambda d, answer: f"Limit = {format_number(answer)}",
    },
    "maximum-volume-of-closed-cylinder-with-fixed-surface-area": {
        "title": "Maximum Volume of a Closed Cylinder with Fixed Surface Area",
        "latex": r"S = 2\pi r^2 + 2\pi rh,\quad V_{\max} \text{ when } h = 2r",
        "fields": [
            {"name": "surface_area", "label": "Surface Area (S)", "min": 0},
        ],
        "compute": maximum_volume_closed_cylinder,
        "substitute": lambda d: (
            f"At optimum, r = sqrt({format_number(d['surface_area'])} / (6π)) and h = 2r"
        ),
        "answer": lambda d, answer: (
            f"Maximum volume = {format_number(answer['volume'])} with r = {format_number(answer['radius'])} and h = {format_number(answer['height'])}"
        ),
    },
    "water-level-rate-in-conical-tank": {
        "title": "Water Level Rate in a Conical Tank",
        "latex": r"\frac{dh}{dt} = \frac{1}{\pi (R/H)^2 h^2}\frac{dV}{dt}",
        "fields": [
            {"name": "tank_radius", "label": "Full Tank Radius (R)", "min": 0},
            {"name": "tank_height", "label": "Full Tank Height (H)", "min": 0},
            {"name": "water_depth", "label": "Current Water Depth (h)", "min": 0},
            {"name": "volume_rate", "label": "Rate dV/dt"},
        ],
        "compute": water_level_rate_in_conical_tank,
        "substitute": lambda d: (
            f"dh/dt = {format_number(d['volume_rate'])} / (π({format_number(d['tank_radius'])}/{format_number(d['tank_height'])})^2({format_number(d['water_depth'])})^2)"
        ),
        "answer": lambda d, answer: f"dh/dt = {format_number(answer)}",
    },
    "definite-integral-of-sine-squared": {
        "title": "Definite Integral of sin^2(kx)",
        "latex": r"\int_a^b c\sin^2(kx)\,dx = c\left[\frac{x}{2} - \frac{\sin(2kx)}{4k}\right]_a^b",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "rate", "label": "Frequency (k)"},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_sine_squared,
        "substitute": lambda d: (
            f"Integral = {format_number(d['coefficient'])}[x/2 - sin(2*{format_number(d['rate'])}x)/(4*{format_number(d['rate'])})]"
            f" from {format_number(d['lower_bound'])} to {format_number(d['upper_bound'])}"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "definite-integral-of-cosine-squared": {
        "title": "Definite Integral of cos^2(kx)",
        "latex": r"\int_a^b c\cos^2(kx)\,dx = c\left[\frac{x}{2} + \frac{\sin(2kx)}{4k}\right]_a^b",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "rate", "label": "Frequency (k)"},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_cosine_squared,
        "substitute": lambda d: (
            f"Integral = {format_number(d['coefficient'])}[x/2 + sin(2*{format_number(d['rate'])}x)/(4*{format_number(d['rate'])})]"
            f" from {format_number(d['lower_bound'])} to {format_number(d['upper_bound'])}"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
    "definite-integral-of-secant-times-tangent": {
        "title": "Definite Integral of sec(kx) tan(kx)",
        "latex": r"\int_a^b c\sec(kx)\tan(kx)\,dx = \frac{c}{k}[\sec(kx)]_a^b",
        "fields": [
            {"name": "coefficient", "label": "Coefficient (c)"},
            {"name": "rate", "label": "Frequency (k)"},
            {"name": "lower_bound", "label": "Lower Bound (a)"},
            {"name": "upper_bound", "label": "Upper Bound (b)"},
        ],
        "compute": definite_integral_sec_tan,
        "substitute": lambda d: (
            f"Integral = ({format_number(d['coefficient'])}/{format_number(d['rate'])})"
            f"(sec({format_number(d['rate'])}{format_number(d['upper_bound'])}) - sec({format_number(d['rate'])}{format_number(d['lower_bound'])}))"
        ),
        "answer": lambda d, answer: f"Integral = {format_number(answer)}",
    },
}


CALCULUS_FORMULA_GROUPS = [
    {"title": "All Formulas", "slugs": list(CALCULUS_FORMULAS.keys())}
]


CALCULUS_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in CALCULUS_FORMULAS.items()
}
