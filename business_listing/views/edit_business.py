from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import BusinessDetails
from .add_business import _business_form_context

@login_required
def edit_business(request, slug):
    business = get_object_or_404(BusinessDetails, slug=slug)

    # Only the original creator may modify this listing.
    if request.user != business.created_by:
        messages.error(request, 'You do not have permission to edit this business.')
        return redirect(reverse('business_details', kwargs={'slug': slug}))

    if request.method == 'POST':
        business_name = request.POST.get('business_name', '').strip()
        category = request.POST.get('category', '').strip()
        country = request.POST.get('country', '').strip().upper()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        post_office_box = request.POST.get('post_office_box', '').strip() or None
        short_description = request.POST.get('short_description', '').strip()
        long_description = request.POST.get('long_description', '').strip()

        if not business_name or not category or not country or not city:
            messages.error(request, 'Business name, category, country, and city are required.')
            return render(request, 'business_listing/business_form.html', _business_form_context(
                error='Business name, category, country, and city are required.',
                business=business,
                data=request.POST,
                edit_mode=True,
            ))

        if len(category) > 100:
            messages.error(request, 'Category must be 100 characters or fewer.')
            return render(request, 'business_listing/business_form.html', _business_form_context(
                error='Category must be 100 characters or fewer.',
                business=business,
                data=request.POST,
                edit_mode=True,
            ))

        if post_office_box:
            try:
                post_office_box = int(post_office_box)
            except (TypeError, ValueError):
                messages.error(request, 'Post office box must be a whole number.')
                return render(request, 'business_listing/business_form.html', _business_form_context(
                    error='Post office box must be a whole number.',
                    business=business,
                    data=request.POST,
                    edit_mode=True,
                ))

        business.business_name = business_name
        business.category = category
        business.country = country
        business.city = city
        business.postal_code = postal_code
        business.post_office_box = post_office_box
        business.short_description = short_description
        business.long_description = long_description
        business.save()
        messages.success(request, 'Business details updated successfully.')
        return redirect(reverse('business_details', kwargs={'slug': business.slug}))

    return render(request, 'business_listing/business_form.html', _business_form_context(
        business=business,
        edit_mode=True,
    ))
