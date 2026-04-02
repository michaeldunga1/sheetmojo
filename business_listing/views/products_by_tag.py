from django.core.paginator import Paginator
from django.shortcuts import render

from ..models import Product
from ..tag_utils import build_tag_filter, normalize_tag


def products_by_tag(request, tag):
    normalized_tag = normalize_tag(tag)
    products = Product.objects.select_related('business').filter(
        build_tag_filter('tags', normalized_tag)
    )

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': f'Products Tagged "{normalized_tag}"',
        'selected_tag': normalized_tag,
        'available_categories': Product.objects.order_by('product_category').values_list('product_category', flat=True).distinct(),
        'currency_choices': Product.Currency.choices,
        'filter_category': '',
        'filter_currency': '',
        'min_price': '',
        'max_price': '',
        'filter_error': '',
        'q': '',
        'search_placeholder': f'Search products tagged {normalized_tag}',
        'search_help_text': f'Tag filter is active for {normalized_tag}.',
    }
    return render(request, 'business_listing/product_list.html', context)
