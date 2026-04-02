from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, render

from ..models import Product


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('business', 'business__created_by'), slug=slug)

    related_products = (
        Product.objects.select_related('business')
        .exclude(pk=product.pk)
        .annotate(
            related_score=(
                Case(
                    When(product_category=product.product_category, then=Value(2)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(business=product.business, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
        )
        .filter(related_score__gt=0)
        .order_by('-related_score', '-posted_on')[:6]
    )

    return render(request, 'business_listing/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })