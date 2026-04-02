try:
    import pycountry
except Exception:  # pragma: no cover
    pycountry = None


FALLBACK_CURRENCY_CHOICES = (
    ("USD", "US Dollar (USD)"),
    ("EUR", "Euro (EUR)"),
    ("GBP", "British Pound (GBP)"),
    ("KES", "Kenyan Shilling (KES)"),
    ("UGX", "Ugandan Shilling (UGX)"),
    ("TZS", "Tanzanian Shilling (TZS)"),
    ("NGN", "Nigerian Naira (NGN)"),
    ("ZAR", "South African Rand (ZAR)"),
)


def get_currency_choices():
    if pycountry is None:
        return FALLBACK_CURRENCY_CHOICES

    choices_by_code = {}
    for currency in pycountry.currencies:
        code = getattr(currency, "alpha_3", None)
        name = getattr(currency, "name", None)
        if not code or not name:
            continue
        choices_by_code[code] = f"{name} ({code})"

    if not choices_by_code:
        return FALLBACK_CURRENCY_CHOICES

    return tuple((code, choices_by_code[code]) for code in sorted(choices_by_code.keys()))


CURRENCY_CHOICES = get_currency_choices()
CURRENCY_CODES = tuple(code for code, _ in CURRENCY_CHOICES)