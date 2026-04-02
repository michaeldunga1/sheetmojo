from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..forms import ProductForm
from ..models import Product
from .add_product import _product_owner_guard


@login_required
def edit_product(request, slug, product_slug):
    product = get_object_or_404(Product.objects.select_related('business'), slug=product_slug, business__slug=slug)
    forbidden_response = _product_owner_guard(request, product.business)
    if forbidden_response:
        return forbidden_response

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
        except Exception:
            form.add_error(None, 'We could not update this product right now. Please try again.')
        else:
            messages.success(request, 'Product updated successfully.')
            return redirect(reverse('business_details', kwargs={'slug': product.business.slug}))

    return render(request, 'business_listing/product_form.html', {
        'form': form,
        'business': product.business,
        'product': product,
        'edit_mode': True,
    })