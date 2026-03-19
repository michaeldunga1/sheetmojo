def _fmt_number(value):
    if abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _format_matrix(matrix):
    rows = ["[" + ", ".join(_fmt_number(v) for v in row) + "]" for row in matrix]
    return "[" + "; ".join(rows) + "]"


def _matrix(values, prefix, rows, cols):
    return [
        [values[f"{prefix}{r}{c}"] for c in range(1, cols + 1)]
        for r in range(1, rows + 1)
    ]


def _matrix_fields(prefix, label, rows, cols):
    return [
        {"name": f"{prefix}{r}{c}", "label": f"{label}{r}{c}"}
        for r in range(1, rows + 1)
        for c in range(1, cols + 1)
    ]


def _add(a, b):
    return [[a[r][c] + b[r][c] for c in range(len(a[0]))] for r in range(len(a))]


def _subtract(a, b):
    return [[a[r][c] - b[r][c] for c in range(len(a[0]))] for r in range(len(a))]


def _multiply(a, b):
    rows = len(a)
    cols = len(b[0])
    inner = len(b)
    out = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(sum(a[r][k] * b[k][c] for k in range(inner)))
        out.append(row)
    return out


def _transpose(m):
    return [list(col) for col in zip(*m)]


def _det2(m):
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def _det3(m):
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _inverse2(m):
    det = _det2(m)
    if abs(det) < 1e-12:
        raise ValueError("This matrix is singular, so the inverse does not exist.")
    return [
        [m[1][1] / det, -m[0][1] / det],
        [-m[1][0] / det, m[0][0] / det],
    ]


def _rank2(m):
    det = _det2(m)
    if abs(det) > 1e-12:
        return 2
    if all(abs(v) < 1e-12 for row in m for v in row):
        return 0
    return 1


def _identity(n):
    if n < 1 or n > 6:
        raise ValueError("Use an order n from 1 to 6.")
    return [[1 if r == c else 0 for c in range(n)] for r in range(n)]


_MATRIX_2X2_A_FIELDS = _matrix_fields("a", "A", 2, 2)
_MATRIX_2X2_B_FIELDS = _matrix_fields("b", "B", 2, 2)
_MATRIX_3X3_A_FIELDS = _matrix_fields("a", "A", 3, 3)


MATRIX_FORMULAS = {
    "matrix-addition-2x2": {
        "title": "Matrix Addition (2x2)",
        "latex": r"C = A + B",
        "fields": _MATRIX_2X2_A_FIELDS + _MATRIX_2X2_B_FIELDS,
        "compute": lambda d: _add(_matrix(d, "a", 2, 2), _matrix(d, "b", 2, 2)),
        "substitute": lambda d: "C = A + B",
        "answer_label": "C",
        "format_answer": _format_matrix,
    },
    "matrix-subtraction-2x2": {
        "title": "Matrix Subtraction (2x2)",
        "latex": r"C = A - B",
        "fields": _MATRIX_2X2_A_FIELDS + _MATRIX_2X2_B_FIELDS,
        "compute": lambda d: _subtract(_matrix(d, "a", 2, 2), _matrix(d, "b", 2, 2)),
        "substitute": lambda d: "C = A - B",
        "answer_label": "C",
        "format_answer": _format_matrix,
    },
    "matrix-multiplication-2x2": {
        "title": "Matrix Multiplication (2x2)",
        "latex": r"C = AB",
        "fields": _MATRIX_2X2_A_FIELDS + _MATRIX_2X2_B_FIELDS,
        "compute": lambda d: _multiply(_matrix(d, "a", 2, 2), _matrix(d, "b", 2, 2)),
        "substitute": lambda d: "C = AB",
        "answer_label": "C",
        "format_answer": _format_matrix,
    },
    "determinant-of-2x2-matrix": {
        "title": "Determinant of 2x2 Matrix",
        "latex": r"\det(A) = ad - bc",
        "fields": _MATRIX_2X2_A_FIELDS,
        "compute": lambda d: _det2(_matrix(d, "a", 2, 2)),
        "substitute": lambda d: "det(A) = A11*A22 - A12*A21",
        "answer_label": "det(A)",
        "format_answer": _fmt_number,
    },
    "determinant-of-3x3-matrix": {
        "title": "Determinant of 3x3 Matrix",
        "latex": r"\det(A) = a(ei - fh) - b(di - fg) + c(dh - eg)",
        "fields": _MATRIX_3X3_A_FIELDS,
        "compute": lambda d: _det3(_matrix(d, "a", 3, 3)),
        "substitute": lambda d: "det(A) via first-row expansion",
        "answer_label": "det(A)",
        "format_answer": _fmt_number,
    },
    "inverse-of-2x2-matrix": {
        "title": "Inverse of 2x2 Matrix",
        "latex": r"A^{-1} = \frac{1}{\det(A)}\begin{bmatrix}d & -b \\ -c & a\end{bmatrix}",
        "fields": _MATRIX_2X2_A_FIELDS,
        "compute": lambda d: _inverse2(_matrix(d, "a", 2, 2)),
        "substitute": lambda d: "A^-1 = (1/det(A)) * adj(A)",
        "answer_label": "A^-1",
        "format_answer": _format_matrix,
    },
    "transpose-of-3x3-matrix": {
        "title": "Transpose of 3x3 Matrix",
        "latex": r"A^T",
        "fields": _MATRIX_3X3_A_FIELDS,
        "compute": lambda d: _transpose(_matrix(d, "a", 3, 3)),
        "substitute": lambda d: "A^T is formed by swapping rows and columns",
        "answer_label": "A^T",
        "format_answer": _format_matrix,
    },
    "trace-of-3x3-matrix": {
        "title": "Trace of 3x3 Matrix",
        "latex": r"\operatorname{tr}(A) = a_{11}+a_{22}+a_{33}",
        "fields": _MATRIX_3X3_A_FIELDS,
        "compute": lambda d: d["a11"] + d["a22"] + d["a33"],
        "substitute": lambda d: "tr(A) = A11 + A22 + A33",
        "answer_label": "tr(A)",
        "format_answer": _fmt_number,
    },
    "scalar-multiplication-of-3x3-matrix": {
        "title": "Scalar Multiplication of 3x3 Matrix",
        "latex": r"B = kA",
        "fields": [{"name": "k", "label": "Scalar k"}] + _MATRIX_3X3_A_FIELDS,
        "compute": lambda d: [[d["k"] * v for v in row] for row in _matrix(d, "a", 3, 3)],
        "substitute": lambda d: "B = kA",
        "answer_label": "B",
        "format_answer": _format_matrix,
    },
    "rank-of-2x2-matrix": {
        "title": "Rank of 2x2 Matrix",
        "latex": r"\operatorname{rank}(A)",
        "fields": _MATRIX_2X2_A_FIELDS,
        "compute": lambda d: _rank2(_matrix(d, "a", 2, 2)),
        "substitute": lambda d: "rank determined by determinant and zero rows",
        "answer_label": "rank(A)",
        "format_answer": lambda value: str(int(value)),
    },
    "identity-matrix-of-order-n": {
        "title": "Identity Matrix of Order n",
        "latex": r"I_n",
        "fields": [{"name": "n", "label": "Order n", "type": "integer", "min": 1, "max": 6}],
        "compute": lambda d: _identity(d["n"]),
        "substitute": lambda d: "I_n has 1s on the main diagonal and 0s elsewhere",
        "answer_label": "I_n",
        "format_answer": _format_matrix,
    },
}


MATRIX_FORMULA_GROUPS = [{"title": "All Formulas", "slugs": list(MATRIX_FORMULAS.keys())}]


MATRIX_FORMULA_DESCRIPTIONS = {
    slug: formula["title"] for slug, formula in MATRIX_FORMULAS.items()
}
