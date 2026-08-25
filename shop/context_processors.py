from .models import Product


def cart_count(request):
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        return {"cart_count": 0}
    count = 0
    for quantity in cart.values():
        try:
            count += max(int(quantity), 0)
        except (TypeError, ValueError):
            continue
    return {"cart_count": count}


def search_products(request):
    """Product data for the home-page search suggestions only."""
    if request.resolver_match and request.resolver_match.view_name == "shop:product_list":
        return {"search_products": list(Product.objects.values("id", "name", "part_number", "is_available"))}
    return {"search_products": []}
