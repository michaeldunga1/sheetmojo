from types import SimpleNamespace

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django_countries import countries
from ..models import BusinessDetails

MAX_BUSINESSES_PER_USER = 3
EMPTY_BUSINESS = SimpleNamespace(
    business_name='',
    category='',
    country='',
    city='',
    postal_code='',
    post_office_box='',
    tags='',
    short_description='',
    long_description='',
)


def _business_form_context(**extra):
    """Keep shared form metadata in one place for add/edit screens."""
    context = {
        'business': EMPTY_BUSINESS,
        'data': {},
        'country_choices': list(countries),
    }
    context.update(extra)
    return context

@login_required
def add_business(request):
    # Enforce the per-user business cap before touching user input.
    current_count = BusinessDetails.objects.filter(created_by=request.user).count()
    limit_reached = current_count >= MAX_BUSINESSES_PER_USER

    if request.method == 'POST':
        if limit_reached:
            messages.error(request, f'You can list up to {MAX_BUSINESSES_PER_USER} businesses only.')
            return render(request, 'business_listing/business_form.html', _business_form_context(
                error=f'You can list up to {MAX_BUSINESSES_PER_USER} businesses only.',
                edit_mode=False,
                business_limit_reached=True,
                current_business_count=current_count,
                max_businesses_per_user=MAX_BUSINESSES_PER_USER,
            ))

        business_name = request.POST.get('business_name', '').strip()
        category = request.POST.get('category', '').strip()
        country = request.POST.get('country', '').strip().upper()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        post_office_box = request.POST.get('post_office_box', '').strip()
        tags = request.POST.get('tags', '').strip()
        short_description = request.POST.get('short_description', '').strip()
        long_description = request.POST.get('long_description', '').strip()

        if not all([business_name, category, country, city, postal_code, post_office_box, tags, short_description, long_description]):
            messages.error(request, 'All fields are required.')
            return render(request, 'business_listing/business_form.html', _business_form_context(
                error='All fields are required.',
                data=request.POST,
                edit_mode=False,
                business_limit_reached=limit_reached,
                current_business_count=current_count,
                max_businesses_per_user=MAX_BUSINESSES_PER_USER,
            ))

        if len(category) > 100:
            messages.error(request, 'Category must be 100 characters or fewer.')
            return render(request, 'business_listing/business_form.html', _business_form_context(
                error='Category must be 100 characters or fewer.',
                data=request.POST,
                edit_mode=False,
                business_limit_reached=limit_reached,
                current_business_count=current_count,
                max_businesses_per_user=MAX_BUSINESSES_PER_USER,
            ))

        try:
            post_office_box = int(post_office_box)
            if post_office_box < 1:
                raise ValueError()
        except (TypeError, ValueError):
            messages.error(request, 'Post office box must be a positive whole number.')
            return render(request, 'business_listing/business_form.html', _business_form_context(
                error='Post office box must be a positive whole number.',
                data=request.POST,
                edit_mode=False,
                business_limit_reached=limit_reached,
                current_business_count=current_count,
                max_businesses_per_user=MAX_BUSINESSES_PER_USER,
            ))

        BusinessDetails.objects.create(
            business_name=business_name,
            category=category,
            country=country,
            city=city,
            postal_code=postal_code,
            post_office_box=post_office_box,
            tags=tags,
            short_description=short_description,
            long_description=long_description,
            created_by=request.user,
        )
        messages.success(request, 'Your business has been listed successfully.')
        return redirect(reverse('listed_businesses'))

    return render(request, 'business_listing/business_form.html', _business_form_context(
        edit_mode=False,
        business_limit_reached=limit_reached,
        current_business_count=current_count,
        max_businesses_per_user=MAX_BUSINESSES_PER_USER,
    ))
