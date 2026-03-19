import math


def _fmt(value):
    if isinstance(value, float) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _positive_int(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be a positive integer.")


# ── Number Theory ──────────────────────────────────────────────────────────────

def _compute_gcd(d):
    return math.gcd(abs(int(d["a"])), abs(int(d["b"])))


def _compute_lcm(d):
    a, b = abs(int(d["a"])), abs(int(d["b"]))
    if a == 0 or b == 0:
        return 0
    return a * b // math.gcd(a, b)


def _compute_euler_totient(d):
    n = int(d["n"])
    _positive_int(n, "n")
    result = n
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def _compute_divisor_count(d):
    n = int(d["n"])
    _positive_int(n, "n")
    if n > 10 ** 9:
        raise ValueError("n must be at most 1,000,000,000 for this calculator.")
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 2
            if i * i == n:
                count -= 1
        i += 1
    return count


def _compute_sum_of_divisors(d):
    n = int(d["n"])
    _positive_int(n, "n")
    if n > 10 ** 9:
        raise ValueError("n must be at most 1,000,000,000 for this calculator.")
    total = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total


def _compute_modular_exp(d):
    a, b, m = int(d["a"]), int(d["b"]), int(d["m"])
    if m <= 1:
        raise ValueError("Modulus m must be greater than 1.")
    if b < 0:
        raise ValueError("Exponent b must be at least 0.")
    return pow(a, b, m)


def _compute_modular_inverse(d):
    a, m = int(d["a"]), int(d["m"])
    if m <= 1:
        raise ValueError("Modulus m must be greater than 1.")
    try:
        return pow(a, -1, m)
    except ValueError:
        raise ValueError(
            f"Modular inverse does not exist: gcd({a}, {m}) \u2260 1."
        )


# ── Combinatorics ──────────────────────────────────────────────────────────────

def _compute_permutations(d):
    n, r = int(d["n"]), int(d["r"])
    if n < 0 or r < 0:
        raise ValueError("n and r must be non-negative integers.")
    if r > n:
        raise ValueError("r cannot be greater than n.")
    return math.perm(n, r)


def _compute_combinations(d):
    n, r = int(d["n"]), int(d["r"])
    if n < 0 or r < 0:
        raise ValueError("n and r must be non-negative integers.")
    if r > n:
        raise ValueError("r cannot be greater than n.")
    return math.comb(n, r)


def _compute_derangements(d):
    n = int(d["n"])
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    if n == 0:
        return 1
    if n == 1:
        return 0
    total = 0.0
    sign = 1
    fact = 1
    for k in range(n + 1):
        if k > 0:
            fact *= k
        total += sign / fact
        sign = -sign
    return round(math.factorial(n) * total)


def _compute_catalan(d):
    n = int(d["n"])
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    return math.comb(2 * n, n) // (n + 1)


def _compute_fibonacci(d):
    n = int(d["n"])
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    if n > 500:
        raise ValueError("n must be at most 500 for this calculator.")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _compute_stars_and_bars(d):
    n, k = int(d["n"]), int(d["k"])
    if n < 1:
        raise ValueError("Number of bins n must be at least 1.")
    if k < 0:
        raise ValueError("Number of items k must be at least 0.")
    return math.comb(n + k - 1, k)


# ── Probability ────────────────────────────────────────────────────────────────

def _compute_classical_prob(d):
    fav, total = int(d["favorable"]), int(d["total"])
    if total <= 0:
        raise ValueError("Total outcomes must be greater than 0.")
    if fav < 0:
        raise ValueError("Favorable outcomes must be at least 0.")
    if fav > total:
        raise ValueError("Favorable outcomes cannot exceed total outcomes.")
    return fav / total


def _compute_complement_prob(d):
    p = d["prob_a"]
    if p < 0 or p > 1:
        raise ValueError("Probability must be between 0 and 1.")
    return 1.0 - p


def _compute_bayes(d):
    p_b_given_a, p_a, p_b = d["p_b_given_a"], d["p_a"], d["p_b"]
    if not (0 <= p_b_given_a <= 1 and 0 <= p_a <= 1):
        raise ValueError("All probabilities must be in [0, 1].")
    if p_b <= 0:
        raise ValueError("P(B) must be greater than 0.")
    return p_b_given_a * p_a / p_b


def _compute_binomial_pmf(d):
    n, k = int(d["n"]), int(d["k"])
    p = d["p"]
    if n < 1:
        raise ValueError("n must be at least 1.")
    if k < 0 or k > n:
        raise ValueError("k must satisfy 0 \u2264 k \u2264 n.")
    if p < 0 or p > 1:
        raise ValueError("Probability p must be between 0 and 1.")
    return math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))


def _compute_poisson_pmf(d):
    lam = d["lam"]
    k = int(d["k"])
    if lam <= 0:
        raise ValueError("\u03bb must be greater than 0.")
    if k < 0:
        raise ValueError("k must be a non-negative integer.")
    if k > 170:
        raise ValueError("k must be at most 170 for this calculator.")
    log_p = -lam + k * math.log(lam) - math.lgamma(k + 1)
    return math.exp(log_p)


def _compute_geometric_pmf(d):
    p = d["p"]
    k = int(d["k"])
    if p <= 0 or p > 1:
        raise ValueError("p must be in (0, 1].")
    if k < 1:
        raise ValueError("k must be at least 1.")
    return ((1 - p) ** (k - 1)) * p


# ── Series & Summations ────────────────────────────────────────────────────────

def _compute_arithmetic_series(d):
    a, diff, n = d["a"], d["diff"], int(d["n"])
    if n < 1:
        raise ValueError("n must be at least 1.")
    return n / 2 * (2 * a + (n - 1) * diff)


def _compute_geometric_series_finite(d):
    a, r, n = d["a"], d["r"], int(d["n"])
    if n < 1:
        raise ValueError("n must be at least 1.")
    if abs(r - 1) < 1e-12:
        return a * n
    return a * (1 - r ** n) / (1 - r)


def _compute_geometric_series_infinite(d):
    a, r = d["a"], d["r"]
    if abs(r) >= 1:
        raise ValueError("Series diverges: |r| must be strictly less than 1.")
    return a / (1 - r)


def _compute_power_sum(d):
    n = int(d["n"])
    if n < 1:
        raise ValueError("n must be at least 1.")
    return n * (n + 1) // 2


def _compute_sum_of_squares(d):
    n = int(d["n"])
    if n < 1:
        raise ValueError("n must be at least 1.")
    return n * (n + 1) * (2 * n + 1) // 6


def _compute_sum_of_cubes(d):
    n = int(d["n"])
    if n < 1:
        raise ValueError("n must be at least 1.")
    return (n * (n + 1) // 2) ** 2


# ── Discrete Mathematics ───────────────────────────────────────────────────────

def _compute_pigeonhole(d):
    n, m = int(d["n"]), int(d["m"])
    if n < 1:
        raise ValueError("Number of holes n must be at least 1.")
    if m < 2:
        raise ValueError("Guarantee m must be at least 2.")
    return n * (m - 1) + 1


def _compute_inclusion_exclusion(d):
    a, b, inter = int(d["a_size"]), int(d["b_size"]), int(d["intersection"])
    if a < 0 or b < 0 or inter < 0:
        raise ValueError("Set sizes must be non-negative.")
    if inter > min(a, b):
        raise ValueError("Intersection cannot exceed either set's size.")
    return a + b - inter


def _compute_stirling_approx(d):
    n = int(d["n"])
    if n < 1:
        raise ValueError("n must be at least 1.")
    result = math.sqrt(2 * math.pi * n) * (n / math.e) ** n
    if math.isinf(result):
        raise ValueError("Result overflows float precision. Try n \u2264 170.")
    return result


def _compute_birthday_prob(d):
    n, k = int(d["n"]), int(d["k"])
    if n < 1:
        raise ValueError("Year size n must be at least 1.")
    if k < 1:
        raise ValueError("Number of people k must be at least 1.")
    if k > n:
        raise ValueError("k exceeds n \u2014 probability is 1 by the Pigeonhole Principle.")
    prob = 1.0
    for i in range(k):
        prob *= (n - i) / n
    return 1.0 - prob


def _compute_power_set_size(d):
    n = int(d["n"])
    if n < 0:
        raise ValueError("n must be a non-negative integer.")
    return 2 ** n


def _compute_complete_graph_edges(d):
    n = int(d["n"])
    if n < 1:
        raise ValueError("n must be at least 1.")
    return n * (n - 1) // 2


# ── Catalog ────────────────────────────────────────────────────────────────────

MATHEMATICS_FORMULAS = {
    # Number Theory
    "gcd": {
        "title": "Greatest Common Divisor",
        "latex": r"\gcd(a,\,b)",
        "fields": [
            {"name": "a", "label": "Integer a", "type": "integer"},
            {"name": "b", "label": "Integer b", "type": "integer"},
        ],
        "compute": _compute_gcd,
        "substitute": lambda d: f"gcd({int(d['a'])}, {int(d['b'])})",
        "answer_label": "gcd(a, b)",
        "format_answer": str,
    },
    "lcm": {
        "title": "Least Common Multiple",
        "latex": r"\operatorname{lcm}(a,b) = \frac{|a \cdot b|}{\gcd(a,b)}",
        "fields": [
            {"name": "a", "label": "Integer a", "type": "integer", "min": 1},
            {"name": "b", "label": "Integer b", "type": "integer", "min": 1},
        ],
        "compute": _compute_lcm,
        "substitute": lambda d: f"lcm({int(d['a'])}, {int(d['b'])}) = {int(d['a'])} \u00d7 {int(d['b'])} / gcd({int(d['a'])}, {int(d['b'])})",
        "answer_label": "lcm(a, b)",
        "format_answer": str,
    },
    "euler-totient": {
        "title": "Euler's Totient \u03c6(n)",
        "latex": r"\phi(n) = n \prod_{p \mid n}\!\left(1 - \tfrac{1}{p}\right)",
        "fields": [
            {"name": "n", "label": "Positive integer n", "type": "integer", "min": 1},
        ],
        "compute": _compute_euler_totient,
        "substitute": lambda d: f"\u03c6({int(d['n'])})",
        "answer_label": "\u03c6(n)",
        "format_answer": str,
    },
    "divisor-count": {
        "title": "Number of Divisors \u03c4(n)",
        "latex": r"\tau(n) = \sum_{d \mid n} 1",
        "fields": [
            {"name": "n", "label": "Positive integer n", "type": "integer", "min": 1},
        ],
        "compute": _compute_divisor_count,
        "substitute": lambda d: f"\u03c4({int(d['n'])}) \u2014 count all divisors of {int(d['n'])}",
        "answer_label": "\u03c4(n)",
        "format_answer": str,
    },
    "sum-of-divisors": {
        "title": "Sum of Divisors \u03c3(n)",
        "latex": r"\sigma(n) = \sum_{d \mid n} d",
        "fields": [
            {"name": "n", "label": "Positive integer n", "type": "integer", "min": 1},
        ],
        "compute": _compute_sum_of_divisors,
        "substitute": lambda d: f"\u03c3({int(d['n'])}) \u2014 sum all divisors of {int(d['n'])}",
        "answer_label": "\u03c3(n)",
        "format_answer": str,
    },
    "modular-exp": {
        "title": "Modular Exponentiation",
        "latex": r"a^b \bmod m",
        "fields": [
            {"name": "a", "label": "Base a", "type": "integer"},
            {"name": "b", "label": "Exponent b (\u2265 0)", "type": "integer", "min": 0},
            {"name": "m", "label": "Modulus m (> 1)", "type": "integer", "min": 2},
        ],
        "compute": _compute_modular_exp,
        "substitute": lambda d: f"{int(d['a'])}^{int(d['b'])} mod {int(d['m'])}",
        "answer_label": "a\u1d47 mod m",
        "format_answer": str,
    },
    "modular-inverse": {
        "title": "Modular Multiplicative Inverse",
        "latex": r"a^{-1} \bmod m \;\text{s.t.}\; a\cdot x \equiv 1\pmod{m}",
        "fields": [
            {"name": "a", "label": "Integer a", "type": "integer"},
            {"name": "m", "label": "Modulus m (> 1)", "type": "integer", "min": 2},
        ],
        "compute": _compute_modular_inverse,
        "substitute": lambda d: f"{int(d['a'])}\u207b\u00b9 mod {int(d['m'])}",
        "answer_label": "a\u207b\u00b9 mod m",
        "format_answer": str,
    },
    # Combinatorics
    "permutations": {
        "title": "Permutations P(n, r)",
        "latex": r"P(n,r) = \frac{n!}{(n-r)!}",
        "fields": [
            {"name": "n", "label": "Total items n", "type": "integer", "min": 0},
            {"name": "r", "label": "Items chosen r", "type": "integer", "min": 0},
        ],
        "compute": _compute_permutations,
        "substitute": lambda d: f"P({int(d['n'])}, {int(d['r'])}) = {int(d['n'])}! / ({int(d['n'])} - {int(d['r'])})!",
        "answer_label": "P(n, r)",
        "format_answer": str,
    },
    "combinations": {
        "title": "Combinations C(n, r)",
        "latex": r"\binom{n}{r} = \frac{n!}{r!\,(n-r)!}",
        "fields": [
            {"name": "n", "label": "Total items n", "type": "integer", "min": 0},
            {"name": "r", "label": "Items chosen r", "type": "integer", "min": 0},
        ],
        "compute": _compute_combinations,
        "substitute": lambda d: f"C({int(d['n'])}, {int(d['r'])}) = {int(d['n'])}! / ({int(d['r'])}! \u00d7 ({int(d['n'])} - {int(d['r'])})!)",
        "answer_label": "C(n, r)",
        "format_answer": str,
    },
    "derangements": {
        "title": "Derangements D(n)",
        "latex": r"D_n = n!\sum_{k=0}^{n}\frac{(-1)^k}{k!}",
        "fields": [
            {"name": "n", "label": "Number of items n", "type": "integer", "min": 0},
        ],
        "compute": _compute_derangements,
        "substitute": lambda d: f"D({int(d['n'])}) = {int(d['n'])}! \u00d7 \u03a3(-1)^k/k! for k=0..{int(d['n'])}",
        "answer_label": "D(n)",
        "format_answer": str,
    },
    "catalan-number": {
        "title": "Catalan Number C\u2099",
        "latex": r"C_n = \frac{1}{n+1}\binom{2n}{n}",
        "fields": [
            {"name": "n", "label": "Index n", "type": "integer", "min": 0},
        ],
        "compute": _compute_catalan,
        "substitute": lambda d: f"C({int(d['n'])}) = \u0043(2\u00d7{int(d['n'])}, {int(d['n'])}) / ({int(d['n'])}+1)",
        "answer_label": "C\u2099",
        "format_answer": str,
    },
    "fibonacci": {
        "title": "Fibonacci Number F(n)",
        "latex": r"F_n = F_{n-1} + F_{n-2},\quad F_0=0,\;F_1=1",
        "fields": [
            {"name": "n", "label": "Index n", "type": "integer", "min": 0},
        ],
        "compute": _compute_fibonacci,
        "substitute": lambda d: f"F({int(d['n'])})",
        "answer_label": "F(n)",
        "format_answer": str,
    },
    "stars-and-bars": {
        "title": "Stars and Bars",
        "latex": r"\binom{n+k-1}{k}",
        "fields": [
            {"name": "n", "label": "Distinct bins n", "type": "integer", "min": 1},
            {"name": "k", "label": "Identical items k", "type": "integer", "min": 0},
        ],
        "compute": _compute_stars_and_bars,
        "substitute": lambda d: f"C({int(d['n'])}+{int(d['k'])}-1, {int(d['k'])}) = C({int(d['n'])+int(d['k'])-1}, {int(d['k'])})",
        "answer_label": "Ways",
        "format_answer": str,
    },
    # Probability
    "classical-prob": {
        "title": "Classical Probability",
        "latex": r"P(A) = \frac{\text{favorable}}{\text{total}}",
        "fields": [
            {"name": "favorable", "label": "Favorable outcomes", "type": "integer", "min": 0},
            {"name": "total", "label": "Total outcomes", "type": "integer", "min": 1},
        ],
        "compute": _compute_classical_prob,
        "substitute": lambda d: f"P = {int(d['favorable'])} / {int(d['total'])}",
        "answer_label": "P(A)",
        "format_answer": _fmt,
    },
    "complement-prob": {
        "title": "Complementary Probability",
        "latex": r"P(A') = 1 - P(A)",
        "fields": [
            {"name": "prob_a", "label": "P(A)", "min": 0, "max": 1},
        ],
        "compute": _compute_complement_prob,
        "substitute": lambda d: f"P(A') = 1 - {_fmt(d['prob_a'])}",
        "answer_label": "P(A')",
        "format_answer": _fmt,
    },
    "bayes-theorem": {
        "title": "Bayes' Theorem",
        "latex": r"P(A|B) = \frac{P(B|A)\,P(A)}{P(B)}",
        "fields": [
            {"name": "p_b_given_a", "label": "P(B|A)", "min": 0, "max": 1},
            {"name": "p_a", "label": "P(A)", "min": 0, "max": 1},
            {"name": "p_b", "label": "P(B)", "min": 0, "max": 1},
        ],
        "compute": _compute_bayes,
        "substitute": lambda d: f"P(A|B) = {_fmt(d['p_b_given_a'])} \u00d7 {_fmt(d['p_a'])} / {_fmt(d['p_b'])}",
        "answer_label": "P(A|B)",
        "format_answer": _fmt,
    },
    "binomial-pmf": {
        "title": "Binomial Distribution PMF",
        "latex": r"P(X=k) = \binom{n}{k}p^k(1-p)^{n-k}",
        "fields": [
            {"name": "n", "label": "Trials n", "type": "integer", "min": 1},
            {"name": "k", "label": "Successes k", "type": "integer", "min": 0},
            {"name": "p", "label": "Success probability p", "min": 0, "max": 1},
        ],
        "compute": _compute_binomial_pmf,
        "substitute": lambda d: f"P(X={int(d['k'])}) = C({int(d['n'])},{int(d['k'])}) \u00d7 {_fmt(d['p'])}^{int(d['k'])} \u00d7 (1-{_fmt(d['p'])})^{int(d['n'])-int(d['k'])}",
        "answer_label": "P(X = k)",
        "format_answer": _fmt,
    },
    "poisson-pmf": {
        "title": "Poisson Distribution PMF",
        "latex": r"P(X=k) = \frac{e^{-\lambda}\lambda^k}{k!}",
        "fields": [
            {"name": "lam", "label": "Rate \u03bb", "min": 0},
            {"name": "k", "label": "Occurrences k", "type": "integer", "min": 0},
        ],
        "compute": _compute_poisson_pmf,
        "substitute": lambda d: f"P(X={int(d['k'])}) = e^(-{_fmt(d['lam'])}) \u00d7 {_fmt(d['lam'])}^{int(d['k'])} / {int(d['k'])}!",
        "answer_label": "P(X = k)",
        "format_answer": _fmt,
    },
    "geometric-pmf": {
        "title": "Geometric Distribution PMF",
        "latex": r"P(X=k) = (1-p)^{k-1}p",
        "fields": [
            {"name": "p", "label": "Success probability p", "min": 0, "max": 1},
            {"name": "k", "label": "Trial of first success k", "type": "integer", "min": 1},
        ],
        "compute": _compute_geometric_pmf,
        "substitute": lambda d: f"P(X={int(d['k'])}) = (1-{_fmt(d['p'])})^{int(d['k'])-1} \u00d7 {_fmt(d['p'])}",
        "answer_label": "P(X = k)",
        "format_answer": _fmt,
    },
    # Series & Summations
    "arithmetic-series": {
        "title": "Arithmetic Series Sum",
        "latex": r"S_n = \frac{n}{2}\bigl(2a + (n-1)d\bigr)",
        "fields": [
            {"name": "a", "label": "First term a"},
            {"name": "diff", "label": "Common difference d"},
            {"name": "n", "label": "Number of terms n", "type": "integer", "min": 1},
        ],
        "compute": _compute_arithmetic_series,
        "substitute": lambda d: f"S_{int(d['n'])} = {int(d['n'])}/2 \u00d7 (2\u00d7{_fmt(d['a'])} + ({int(d['n'])}-1)\u00d7{_fmt(d['diff'])})",
        "answer_label": "S\u2099",
        "format_answer": _fmt,
    },
    "geometric-series-finite": {
        "title": "Finite Geometric Series Sum",
        "latex": r"S_n = \frac{a(1-r^n)}{1-r},\quad r \neq 1",
        "fields": [
            {"name": "a", "label": "First term a"},
            {"name": "r", "label": "Common ratio r"},
            {"name": "n", "label": "Number of terms n", "type": "integer", "min": 1},
        ],
        "compute": _compute_geometric_series_finite,
        "substitute": lambda d: f"S_{int(d['n'])} = {_fmt(d['a'])} \u00d7 (1 - {_fmt(d['r'])}^{int(d['n'])}) / (1 - {_fmt(d['r'])})",
        "answer_label": "S\u2099",
        "format_answer": _fmt,
    },
    "geometric-series-infinite": {
        "title": "Infinite Geometric Series Sum",
        "latex": r"S = \frac{a}{1-r},\quad |r| < 1",
        "fields": [
            {"name": "a", "label": "First term a"},
            {"name": "r", "label": "Common ratio r (|r| < 1)"},
        ],
        "compute": _compute_geometric_series_infinite,
        "substitute": lambda d: f"S = {_fmt(d['a'])} / (1 - {_fmt(d['r'])})",
        "answer_label": "S",
        "format_answer": _fmt,
    },
    "power-sum": {
        "title": "Sum of First n Integers",
        "latex": r"\sum_{k=1}^{n} k = \frac{n(n+1)}{2}",
        "fields": [
            {"name": "n", "label": "Upper limit n", "type": "integer", "min": 1},
        ],
        "compute": _compute_power_sum,
        "substitute": lambda d: f"S = {int(d['n'])} \u00d7 ({int(d['n'])}+1) / 2",
        "answer_label": "\u03a3k",
        "format_answer": str,
    },
    "sum-of-squares": {
        "title": "Sum of First n Squares",
        "latex": r"\sum_{k=1}^{n} k^2 = \frac{n(n+1)(2n+1)}{6}",
        "fields": [
            {"name": "n", "label": "Upper limit n", "type": "integer", "min": 1},
        ],
        "compute": _compute_sum_of_squares,
        "substitute": lambda d: f"S = {int(d['n'])} \u00d7 ({int(d['n'])}+1) \u00d7 (2\u00d7{int(d['n'])}+1) / 6",
        "answer_label": "\u03a3k\u00b2",
        "format_answer": str,
    },
    "sum-of-cubes": {
        "title": "Sum of First n Cubes",
        "latex": r"\sum_{k=1}^{n} k^3 = \left(\frac{n(n+1)}{2}\right)^2",
        "fields": [
            {"name": "n", "label": "Upper limit n", "type": "integer", "min": 1},
        ],
        "compute": _compute_sum_of_cubes,
        "substitute": lambda d: f"S = ({int(d['n'])} \u00d7 ({int(d['n'])}+1) / 2)\u00b2",
        "answer_label": "\u03a3k\u00b3",
        "format_answer": str,
    },
    # Discrete Mathematics
    "pigeonhole": {
        "title": "Pigeonhole Minimum",
        "latex": r"\text{min items} = n(m-1)+1",
        "fields": [
            {"name": "n", "label": "Number of holes n", "type": "integer", "min": 1},
            {"name": "m", "label": "Guarantee m per hole", "type": "integer", "min": 2},
        ],
        "compute": _compute_pigeonhole,
        "substitute": lambda d: f"{int(d['n'])} \u00d7 ({int(d['m'])}-1) + 1",
        "answer_label": "Minimum pigeons needed",
        "format_answer": str,
    },
    "inclusion-exclusion": {
        "title": "Inclusion-Exclusion (2 Sets)",
        "latex": r"|A \cup B| = |A| + |B| - |A \cap B|",
        "fields": [
            {"name": "a_size", "label": "|A|", "type": "integer", "min": 0},
            {"name": "b_size", "label": "|B|", "type": "integer", "min": 0},
            {"name": "intersection", "label": "|A \u2229 B|", "type": "integer", "min": 0},
        ],
        "compute": _compute_inclusion_exclusion,
        "substitute": lambda d: f"|A \u222a B| = {int(d['a_size'])} + {int(d['b_size'])} - {int(d['intersection'])}",
        "answer_label": "|A \u222a B|",
        "format_answer": str,
    },
    "stirling-approx": {
        "title": "Stirling's Approximation",
        "latex": r"n! \approx \sqrt{2\pi n}\left(\frac{n}{e}\right)^n",
        "fields": [
            {"name": "n", "label": "n", "type": "integer", "min": 1},
        ],
        "compute": _compute_stirling_approx,
        "substitute": lambda d: f"\u221a(2\u03c0\u00d7{int(d['n'])}) \u00d7 ({int(d['n'])}/e)^{int(d['n'])}",
        "answer_label": "n! \u2248",
        "format_answer": _fmt,
    },
    "birthday-prob": {
        "title": "Birthday Problem",
        "latex": r"P(\text{match}) = 1 - \frac{n!}{n^k(n-k)!}",
        "fields": [
            {"name": "n", "label": "Days in year n (e.g. 365)", "type": "integer", "min": 1},
            {"name": "k", "label": "Number of people k", "type": "integer", "min": 1},
        ],
        "compute": _compute_birthday_prob,
        "substitute": lambda d: f"P = 1 - ({int(d['n'])} \u00d7 {int(d['n'])-1} \u00d7 \u2026 \u00d7 ({int(d['n'])}-{int(d['k'])}+1)) / {int(d['n'])}^{int(d['k'])}",
        "answer_label": "P(shared birthday)",
        "format_answer": _fmt,
    },
    "power-set-size": {
        "title": "Power Set Size",
        "latex": r"|\mathcal{P}(S)| = 2^n",
        "fields": [
            {"name": "n", "label": "Set size n", "type": "integer", "min": 0},
        ],
        "compute": _compute_power_set_size,
        "substitute": lambda d: f"|P(S)| = 2^{int(d['n'])}",
        "answer_label": "|P(S)|",
        "format_answer": str,
    },
    "complete-graph-edges": {
        "title": "Complete Graph K(n) Edges",
        "latex": r"|E(K_n)| = \frac{n(n-1)}{2}",
        "fields": [
            {"name": "n", "label": "Vertices n", "type": "integer", "min": 1},
        ],
        "compute": _compute_complete_graph_edges,
        "substitute": lambda d: f"|E(K_{int(d['n'])})| = {int(d['n'])} \u00d7 ({int(d['n'])}-1) / 2",
        "answer_label": "Edges",
        "format_answer": str,
    },
}

MATHEMATICS_FORMULA_GROUPS = [
    {
        "title": "Number Theory",
        "slugs": ["gcd", "lcm", "euler-totient", "divisor-count", "sum-of-divisors", "modular-exp", "modular-inverse"],
    },
    {
        "title": "Combinatorics",
        "slugs": ["permutations", "combinations", "derangements", "catalan-number", "fibonacci", "stars-and-bars"],
    },
    {
        "title": "Probability",
        "slugs": ["classical-prob", "complement-prob", "bayes-theorem", "binomial-pmf", "poisson-pmf", "geometric-pmf"],
    },
    {
        "title": "Series & Summations",
        "slugs": ["arithmetic-series", "geometric-series-finite", "geometric-series-infinite", "power-sum", "sum-of-squares", "sum-of-cubes"],
    },
    {
        "title": "Discrete Mathematics",
        "slugs": ["pigeonhole", "inclusion-exclusion", "stirling-approx", "birthday-prob", "power-set-size", "complete-graph-edges"],
    },
]

MATHEMATICS_FORMULA_DESCRIPTIONS = {
    "gcd": "Compute the greatest common divisor of two integers.",
    "lcm": "Compute the least common multiple of two positive integers.",
    "euler-totient": "Count integers from 1 to n that are coprime with n.",
    "divisor-count": "Count the number of positive divisors of n.",
    "sum-of-divisors": "Compute the sum of all positive divisors of n.",
    "modular-exp": "Compute a\u1d47 mod m efficiently using fast exponentiation.",
    "modular-inverse": "Find x such that a\u00b7x \u2261 1 (mod m), if it exists.",
    "permutations": "Ordered arrangements: number of ways to pick r items from n.",
    "combinations": "Unordered selections: number of ways to choose r items from n.",
    "derangements": "Permutations of n elements with no element in its original position.",
    "catalan-number": "Count binary trees, valid bracket sequences, and triangulations.",
    "fibonacci": "The nth term in the Fibonacci sequence 0, 1, 1, 2, 3, 5, 8, \u2026",
    "stars-and-bars": "Ways to distribute k identical items into n distinct bins.",
    "classical-prob": "Probability as the ratio of favorable to total equally-likely outcomes.",
    "complement-prob": "Probability of the complement event P(A').",
    "bayes-theorem": "Update a prior probability with evidence using Bayes' rule.",
    "binomial-pmf": "Probability of exactly k successes in n independent Bernoulli trials.",
    "poisson-pmf": "Probability of k events in a Poisson process with rate \u03bb.",
    "geometric-pmf": "Probability that the first success occurs on trial k.",
    "arithmetic-series": "Sum of n terms of an arithmetic progression.",
    "geometric-series-finite": "Sum of n terms of a geometric progression.",
    "geometric-series-infinite": "Sum of a convergent infinite geometric series.",
    "power-sum": "Closed form for 1 + 2 + 3 + \u2026 + n.",
    "sum-of-squares": "Closed form for 1\u00b2 + 2\u00b2 + 3\u00b2 + \u2026 + n\u00b2.",
    "sum-of-cubes": "Closed form for 1\u00b3 + 2\u00b3 + 3\u00b3 + \u2026 + n\u00b3.",
    "pigeonhole": "Minimum items to guarantee m items in one hole among n holes.",
    "inclusion-exclusion": "Size of the union of two sets using the inclusion-exclusion principle.",
    "stirling-approx": "Approximate n! using Stirling's formula.",
    "birthday-prob": "Probability of a shared birthday among k people in an n-day year.",
    "power-set-size": "Number of subsets of an n-element set.",
    "complete-graph-edges": "Number of edges in the complete graph K\u2099 on n vertices.",
}
