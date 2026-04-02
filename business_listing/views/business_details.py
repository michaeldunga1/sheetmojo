from django.shortcuts import render, get_object_or_404
from ..models import BusinessDetails

def business_details(request, slug):
    business = get_object_or_404(BusinessDetails.objects.prefetch_related('products'), slug=slug)
    context = {'business': business}
    return render(request, 'business_listing/business_details.html', context)
