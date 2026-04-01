from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import BusinessDetails

@login_required
def delete_business(request, slug):
    business = get_object_or_404(BusinessDetails, slug=slug)

    # Ownership check
    if request.user != business.created_by:
        return redirect(reverse('business_details', kwargs={'slug': slug}))

    if request.method == 'POST':
        business.delete()
        return redirect(reverse('listed_businesses'))

    return render(request, 'business_listing/confirm_delete.html', {
        'business': business,
    })
