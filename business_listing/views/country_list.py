from django.shortcuts import render
from django.core.paginator import Paginator
from django_countries import countries as django_countries


ALL_COUNTRIES = [
    {'code': str(code), 'name': str(name)}
    for code, name in django_countries
]
ALL_COUNTRIES.sort(key=lambda item: item['name'].lower())

def country_list(request):
    query = request.GET.get('q', '').strip().lower()
    countries = ALL_COUNTRIES
    if query:
        countries = [
            item for item in countries
            if query in str(item['code']).lower() or query in str(item['name']).lower()
        ]
    paginator = Paginator(countries, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'countries': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'q': request.GET.get('q', '').strip(),
    }
    return render(request, 'business_listing/country_list.html', context)
