from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django_countries import countries as country_info
from django.contrib.auth import get_user_model

def users_by_city_name(request, country_code, city):
    query = request.GET.get('q', '').strip()
    country_name = country_info.name(country_code) or country_code
    User = get_user_model()
    users = User.objects.filter(profile__country=country_code, profile__city=city)
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(profile__postal_code__icontains=query)
            | Q(profile__about_me__icontains=query)
        )
    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'users': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': f"Users in {city}, {country_name}",
        'country_code': country_code,
        'country_name': country_name,
        'city': city,
        'q': query,
    }
    return render(request, 'business_listing/users_by_city.html', context)
