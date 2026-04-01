from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django_countries import countries as country_info
from ..models import BusinessDetails

def businesses_by_postal_code(request, country_code, postal_code):
    query = request.GET.get('q', '').strip()
    country_name = country_info.name(country_code) or country_code
    businesses = BusinessDetails.objects.filter(country=country_code, postal_code=postal_code)
    if query:
        businesses = businesses.filter(
            Q(business_name__icontains=query)
            | Q(category__icontains=query)
            | Q(city__icontains=query)
            | Q(short_description__icontains=query)
            | Q(long_description__icontains=query)
        )
    paginator = Paginator(businesses, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'businesses': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': f"Businesses in {postal_code}, {country_name}",
        'country_code': country_code,
        'country_name': country_name,
        'postal_code': postal_code,
        'q': query,
    }
    return render(request, 'business_listing/businesses_by_city.html', context)
