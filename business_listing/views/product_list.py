from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from decimal import Decimal, InvalidOperation

from ..models import Product


def product_list(request):
    query = request.GET.get('q', '').strip()
    filter_category = Product.normalize_category(request.GET.get('filter_category', '').strip())
    filter_currency = request.GET.get('filter_currency', '').strip().upper()
    min_price_raw = request.GET.get('min_price', '').strip()
    max_price_raw = request.GET.get('max_price', '').strip()
    filter_error = ''
    products = Product.objects.select_related('business').all()

    if filter_category:
        products = products.filter(product_category=filter_category)

    valid_currencies = set(Product.Currency.values)
    if filter_currency in valid_currencies:
        products = products.filter(currency=filter_currency)
    else:
        filter_currency = ''

    min_price = None
    if min_price_raw:
        try:
            min_price = Decimal(min_price_raw)
            if min_price < 0:
                filter_error = 'Minimum price cannot be negative.'
                min_price_raw = ''
                min_price = None
        except InvalidOperation:
            filter_error = 'Minimum price must be a valid number.'
            min_price_raw = ''

    max_price = None
    if max_price_raw:
        try:
            max_price = Decimal(max_price_raw)
            if max_price < 0:
                filter_error = 'Maximum price cannot be negative.'
                max_price_raw = ''
                max_price = None
        except InvalidOperation:
            filter_error = 'Maximum price must be a valid number.'
            max_price_raw = ''

    if min_price is not None and max_price is not None and min_price > max_price:
        filter_error = 'Minimum price cannot be greater than maximum price.'
        min_price_raw = ''
        max_price_raw = ''
        min_price = None
        max_price = None

    if min_price is not None:
        products = products.filter(price__gte=min_price)

    if max_price is not None:
        products = products.filter(price__lte=max_price)

    if query:
        products = products.filter(
            Q(product_name__icontains=query)
            | Q(product_category__icontains=query)
            | Q(product_description__icontains=query)
            | Q(currency__icontains=query)
            | Q(terms_of_sale__icontains=query)
            | Q(business__business_name__icontains=query)
            | Q(business__category__icontains=query)
            | Q(business__city__icontains=query)
            | Q(business__country__icontains=query)
        )

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    available_categories = Product.objects.order_by('product_category').values_list('product_category', flat=True).distinct()
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': 'All Products',
        'q': query,
        'available_categories': available_categories,
        'currency_choices': Product.Currency.choices,
        'filter_category': filter_category,
        'filter_currency': filter_currency,
        'min_price': min_price_raw,
        'max_price': max_price_raw,
        'filter_error': filter_error,
        'search_placeholder': 'Search by product name, business, category, city, country, currency, or description',
        'search_help_text': 'Tip: product search matches both product details and the linked business listing information.',
    }
    return render(request, 'business_listing/product_list.html', context)