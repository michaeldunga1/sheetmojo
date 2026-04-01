from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django_countries import countries as country_info
from ..models import UserProfile

def users_by_postal_code(request, country_code, postal_code):
    query = request.GET.get('q', '').strip()
    country_name = country_info.name(country_code) or country_code
    users = UserProfile.objects.filter(country=country_code, postal_code=postal_code)
    if query:
        users = users.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(city__icontains=query)
            | Q(about_me__icontains=query)
        )
    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'users': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'country_code': country_code,
        'country_name': country_name,
        'postal_code': postal_code,
        'q': query,
    }
    return render(request, 'business_listing/users_by_postal_code.html', context)
