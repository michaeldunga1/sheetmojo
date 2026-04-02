from django.db.models import Q


def normalize_tag(tag):
    return " ".join((tag or "").split())


def build_tag_filter(field_name, tag):
    normalized = normalize_tag(tag)
    if not normalized:
        return Q(pk__isnull=True)

    return (
        Q(**{f"{field_name}__iexact": normalized})
        | Q(**{f"{field_name}__istartswith": f"{normalized},"})
        | Q(**{f"{field_name}__iendswith": f",{normalized}"})
        | Q(**{f"{field_name}__iendswith": f", {normalized}"})
        | Q(**{f"{field_name}__icontains": f",{normalized},"})
        | Q(**{f"{field_name}__icontains": f", {normalized},"})
    )
