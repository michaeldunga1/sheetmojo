from math import sqrt


def format_number(value):
    rounded = round(value, 10)
    if float(rounded).is_integer():
        return str(int(rounded))
    return f"{rounded:.10f}".rstrip("0").rstrip(".")


def arithmetic_mean(values):
    return (values["x1"] + values["x2"] + values["x3"] + values["x4"] + values["x5"]) / 5.0


def weighted_mean(values):
    numerator = (
        values["x1"] * values["w1"]
        + values["x2"] * values["w2"]
        + values["x3"] * values["w3"]
    )
    denominator = values["w1"] + values["w2"] + values["w3"]
    return numerator / denominator


def median_five(values):
    data = sorted([values["x1"], values["x2"], values["x3"], values["x4"], values["x5"]])
    return data[2]


def data_range(values):
    data = [values["x1"], values["x2"], values["x3"], values["x4"], values["x5"]]
    return max(data) - min(data)


def population_variance(values):
    data = [values["x1"], values["x2"], values["x3"], values["x4"], values["x5"]]
    mean = sum(data) / len(data)
    return sum((value - mean) ** 2 for value in data) / len(data)


def population_standard_deviation(values):
    return sqrt(population_variance(values))


def z_score(values):
    return (values["x"] - values["mean"]) / values["std_dev"]


def confidence_interval_mean(values):
    margin = values["z_value"] * values["std_dev"] / sqrt(values["sample_size"])
    return {"lower": values["sample_mean"] - margin, "upper": values["sample_mean"] + margin}


def probability_complement(values):
    return 1.0 - values["probability"]


def expected_value_discrete(values):
    return (
        values["x1"] * values["p1"]
        + values["x2"] * values["p2"]
        + values["x3"] * values["p3"]
    )


def linear_regression_slope(values):
    numerator = (values["n"] * values["sum_xy"]) - (values["sum_x"] * values["sum_y"])
    denominator = (values["n"] * values["sum_x2"]) - (values["sum_x"] ** 2)
    return numerator / denominator


STATISTICS_FORMULAS = {
    "arithmetic-mean-of-five-values": {
        "title": "Arithmetic Mean of Five Values",
        "latex": r"\bar{x} = \frac{x_1+x_2+x_3+x_4+x_5}{5}",
        "fields": [
            {"name": "x1", "label": "Value x_1"},
            {"name": "x2", "label": "Value x_2"},
            {"name": "x3", "label": "Value x_3"},
            {"name": "x4", "label": "Value x_4"},
            {"name": "x5", "label": "Value x_5"},
        ],
        "compute": arithmetic_mean,
        "substitute": lambda d: (
            f"Mean = ({format_number(d['x1'])} + {format_number(d['x2'])} + {format_number(d['x3'])} + {format_number(d['x4'])} + {format_number(d['x5'])}) / 5"
        ),
        "answer": lambda d, answer: f"Mean = {format_number(answer)}",
    },
    "weighted-mean-of-three-values": {
        "title": "Weighted Mean of Three Values",
        "latex": r"\bar{x}_w = \frac{\sum x_i w_i}{\sum w_i}",
        "fields": [
            {"name": "x1", "label": "Value x_1"},
            {"name": "w1", "label": "Weight w_1", "min": 0},
            {"name": "x2", "label": "Value x_2"},
            {"name": "w2", "label": "Weight w_2", "min": 0},
            {"name": "x3", "label": "Value x_3"},
            {"name": "w3", "label": "Weight w_3", "min": 0},
        ],
        "compute": weighted_mean,
        "substitute": lambda d: (
            f"Weighted mean = (({format_number(d['x1'])})({format_number(d['w1'])}) + ({format_number(d['x2'])})({format_number(d['w2'])}) + ({format_number(d['x3'])})({format_number(d['w3'])})) / ({format_number(d['w1'])} + {format_number(d['w2'])} + {format_number(d['w3'])})"
        ),
        "answer": lambda d, answer: f"Weighted mean = {format_number(answer)}",
    },
    "median-of-five-values": {
        "title": "Median of Five Values",
        "latex": r"\text{Median} = \text{middle value after sorting}",
        "fields": [
            {"name": "x1", "label": "Value x_1"},
            {"name": "x2", "label": "Value x_2"},
            {"name": "x3", "label": "Value x_3"},
            {"name": "x4", "label": "Value x_4"},
            {"name": "x5", "label": "Value x_5"},
        ],
        "compute": median_five,
        "substitute": lambda d: (
            "Sort the five values and take the third value"
        ),
        "answer": lambda d, answer: f"Median = {format_number(answer)}",
    },
    "range-of-five-values": {
        "title": "Range of Five Values",
        "latex": r"\text{Range} = x_{\max} - x_{\min}",
        "fields": [
            {"name": "x1", "label": "Value x_1"},
            {"name": "x2", "label": "Value x_2"},
            {"name": "x3", "label": "Value x_3"},
            {"name": "x4", "label": "Value x_4"},
            {"name": "x5", "label": "Value x_5"},
        ],
        "compute": data_range,
        "substitute": lambda d: "Range = maximum value - minimum value",
        "answer": lambda d, answer: f"Range = {format_number(answer)}",
    },
    "population-variance-of-five-values": {
        "title": "Population Variance of Five Values",
        "latex": r"\sigma^2 = \frac{\sum (x_i-\mu)^2}{N}",
        "fields": [
            {"name": "x1", "label": "Value x_1"},
            {"name": "x2", "label": "Value x_2"},
            {"name": "x3", "label": "Value x_3"},
            {"name": "x4", "label": "Value x_4"},
            {"name": "x5", "label": "Value x_5"},
        ],
        "compute": population_variance,
        "substitute": lambda d: "Variance = average squared deviation from the mean",
        "answer": lambda d, answer: f"Population variance = {format_number(answer)}",
    },
    "population-standard-deviation-of-five-values": {
        "title": "Population Standard Deviation of Five Values",
        "latex": r"\sigma = \sqrt{\sigma^2}",
        "fields": [
            {"name": "x1", "label": "Value x_1"},
            {"name": "x2", "label": "Value x_2"},
            {"name": "x3", "label": "Value x_3"},
            {"name": "x4", "label": "Value x_4"},
            {"name": "x5", "label": "Value x_5"},
        ],
        "compute": population_standard_deviation,
        "substitute": lambda d: "Standard deviation = square root of population variance",
        "answer": lambda d, answer: f"Population standard deviation = {format_number(answer)}",
    },
    "z-score-of-a-value": {
        "title": "Z-Score of a Value",
        "latex": r"z = \frac{x-\mu}{\sigma}",
        "fields": [
            {"name": "x", "label": "Observed Value x"},
            {"name": "mean", "label": "Mean μ"},
            {"name": "std_dev", "label": "Standard Deviation σ", "min": 0.000001},
        ],
        "compute": z_score,
        "substitute": lambda d: (
            f"z = ({format_number(d['x'])} - {format_number(d['mean'])}) / {format_number(d['std_dev'])}"
        ),
        "answer": lambda d, answer: f"z-score = {format_number(answer)}",
    },
    "confidence-interval-for-mean": {
        "title": "Confidence Interval for a Mean",
        "latex": r"\bar{x} \pm z\frac{\sigma}{\sqrt{n}}",
        "fields": [
            {"name": "sample_mean", "label": "Sample Mean x̄"},
            {"name": "std_dev", "label": "Known Standard Deviation σ", "min": 0.000001},
            {"name": "sample_size", "label": "Sample Size n", "min": 1},
            {"name": "z_value", "label": "Critical z-Value", "min": 0},
        ],
        "compute": confidence_interval_mean,
        "substitute": lambda d: (
            f"CI = {format_number(d['sample_mean'])} ± {format_number(d['z_value'])} * {format_number(d['std_dev'])} / √{format_number(d['sample_size'])}"
        ),
        "answer": lambda d, answer: (
            f"Confidence interval = [{format_number(answer['lower'])}, {format_number(answer['upper'])}]"
        ),
    },
    "complement-of-a-probability": {
        "title": "Complement of a Probability",
        "latex": r"P(A^c) = 1 - P(A)",
        "fields": [
            {"name": "probability", "label": "Probability P(A)", "min": 0},
        ],
        "compute": probability_complement,
        "substitute": lambda d: f"P(A^c) = 1 - {format_number(d['probability'])}",
        "answer": lambda d, answer: f"Complement probability = {format_number(answer)}",
    },
    "expected-value-of-a-discrete-distribution": {
        "title": "Expected Value of a Discrete Distribution",
        "latex": r"E(X) = \sum x_i p_i",
        "fields": [
            {"name": "x1", "label": "Value x_1"},
            {"name": "p1", "label": "Probability p_1", "min": 0},
            {"name": "x2", "label": "Value x_2"},
            {"name": "p2", "label": "Probability p_2", "min": 0},
            {"name": "x3", "label": "Value x_3"},
            {"name": "p3", "label": "Probability p_3", "min": 0},
        ],
        "compute": expected_value_discrete,
        "substitute": lambda d: (
            f"E(X) = ({format_number(d['x1'])})({format_number(d['p1'])}) + ({format_number(d['x2'])})({format_number(d['p2'])}) + ({format_number(d['x3'])})({format_number(d['p3'])})"
        ),
        "answer": lambda d, answer: f"Expected value = {format_number(answer)}",
    },
    "slope-of-simple-linear-regression": {
        "title": "Slope of Simple Linear Regression",
        "latex": r"b_1 = \frac{n\sum xy - (\sum x)(\sum y)}{n\sum x^2 - (\sum x)^2}",
        "fields": [
            {"name": "n", "label": "Number of Points n", "min": 1},
            {"name": "sum_x", "label": "Sum of x Values Σx"},
            {"name": "sum_y", "label": "Sum of y Values Σy"},
            {"name": "sum_xy", "label": "Sum of Products Σxy"},
            {"name": "sum_x2", "label": "Sum of Squares Σx²"},
        ],
        "compute": linear_regression_slope,
        "substitute": lambda d: (
            f"b1 = ({format_number(d['n'])}*{format_number(d['sum_xy'])} - {format_number(d['sum_x'])}*{format_number(d['sum_y'])}) / ({format_number(d['n'])}*{format_number(d['sum_x2'])} - ({format_number(d['sum_x'])})^2)"
        ),
        "answer": lambda d, answer: f"Regression slope = {format_number(answer)}",
    },
}


STATISTICS_FORMULA_GROUPS = [
    {"title": "All Formulas", "slugs": list(STATISTICS_FORMULAS.keys())}
]


STATISTICS_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in STATISTICS_FORMULAS.items()
}
