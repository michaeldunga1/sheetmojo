from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import BusinessDetails

def listed_businesses(request):
    query = request.GET.get('q', '').strip()
    businesses = BusinessDetails.objects.all()
    if query:
        businesses = businesses.filter(
            Q(business_name__icontains=query)
            | Q(category__icontains=query)
            | Q(city__icontains=query)
            | Q(country__icontains=query)
            | Q(postal_code__icontains=query)
            | Q(short_description__icontains=query)
            | Q(long_description__icontains=query)
        )
    paginator = Paginator(businesses, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'businesses': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': 'Listed Businesses',
        'q': query,
    }
    return render(request, 'business_listing/listed_businesses.html', context)
