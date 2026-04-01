from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import BusinessDetails

def businesses_by_category(request, category):
    query = request.GET.get('q', '').strip()
    all_choices = dict(BusinessDetails.CATEGORY_CHOICES)
    businesses = BusinessDetails.objects.filter(category=category)
    if query:
        businesses = businesses.filter(
            Q(business_name__icontains=query)
            | Q(city__icontains=query)
            | Q(country__icontains=query)
            | Q(postal_code__icontains=query)
            | Q(short_description__icontains=query)
            | Q(long_description__icontains=query)
        )
    paginator = Paginator(businesses, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    category_label = all_choices.get(category, category)
    context = {
        'businesses': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'category': category,
        'category_label': category_label,
        'page_title': f"{category_label} Businesses",
        'q': query,
    }
    return render(request, 'business_listing/businesses_by_category.html', context)
