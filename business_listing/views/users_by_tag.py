from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render

from ..tag_utils import build_tag_filter, normalize_tag

User = get_user_model()


def users_by_tag(request, tag):
    normalized_tag = normalize_tag(tag)
    users = User.objects.select_related('profile').filter(
        build_tag_filter('profile__tags', normalized_tag)
    ).order_by('-date_joined')

    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'users': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_title': f'Users Tagged "{normalized_tag}"',
        'q': '',
    }
    return render(request, 'business_listing/all_users.html', context)
