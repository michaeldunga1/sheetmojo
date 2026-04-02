from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from ..models import Product
from .add_product import _product_owner_guard


@login_required
def delete_product(request, slug, product_slug):
    product = get_object_or_404(Product.objects.select_related('business'), slug=product_slug, business__slug=slug)
    forbidden_response = _product_owner_guard(request, product.business)
    if forbidden_response:
        return forbidden_response

    if request.method == 'POST':
        try:
            product.delete()
        except Exception:
            messages.error(request, 'We could not delete this product right now. Please try again.')
        else:
            messages.success(request, 'Product deleted successfully.')

    return redirect(reverse('business_details', kwargs={'slug': slug}))