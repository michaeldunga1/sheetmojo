from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..forms import ProductForm
from ..models import BusinessDetails, Product


def _product_owner_guard(request, business):
    if request.user != business.created_by:
        messages.error(request, 'You do not have permission to manage products for this business.')
        return redirect(reverse('business_details', kwargs={'slug': business.slug}))
    return None


@login_required
def add_product(request, slug):
    business = get_object_or_404(BusinessDetails, slug=slug)
    forbidden_response = _product_owner_guard(request, business)
    if forbidden_response:
        return forbidden_response

    if business.products.count() >= Product.MAX_PRODUCTS_PER_BUSINESS:
        messages.error(
            request,
            f'This business already has the maximum of {Product.MAX_PRODUCTS_PER_BUSINESS} products.',
        )
        return redirect(reverse('business_details', kwargs={'slug': business.slug}))

    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        try:
            product = form.save(commit=False)
            product.business = business
            product.save()
        except ValidationError as exc:
            form.add_error(None, ' '.join(exc.messages))
        except Exception:
            form.add_error(None, 'We could not save this product right now. Please try again.')
        else:
            messages.success(request, 'Product added successfully.')
            return redirect(reverse('business_details', kwargs={'slug': business.slug}))

    return render(request, 'business_listing/product_form.html', {
        'form': form,
        'business': business,
        'edit_mode': False,
    })