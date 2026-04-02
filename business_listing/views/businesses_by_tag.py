from django.core.paginator import Paginator
from django.shortcuts import render

from ..models import BusinessDetails
from ..tag_utils import build_tag_filter, normalize_tag


def businesses_by_tag(request, tag):
    normalized_tag = normalize_tag(tag)
    businesses = BusinessDetails.objects.filter(build_tag_filter('tags', normalized_tag))

    paginator = Paginator(businesses, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'businesses': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': f'Businesses Tagged "{normalized_tag}"',
        'q': '',
    }
    return render(request, 'business_listing/listed_businesses.html', context)
