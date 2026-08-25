from .models import Product


def cart_count(request):
    return {"cart_count": sum(request.session.get("cart", {}).values())}


def search_products(request):
    """Product data used by the search suggestions on every storefront page."""
    return {"search_products": list(Product.objects.values("id", "name", "part_number", "is_available"))}
