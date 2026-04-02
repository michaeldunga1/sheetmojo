from .product_list import product_list

def home(request):
    # Root URL now shows the product listing experience.
    return product_list(request)
