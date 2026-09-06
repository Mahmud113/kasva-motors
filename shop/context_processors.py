from .models import Product


def cart_count(request):
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        return {"cart_count": 0}
    requested_quantities = {}
    for product_id, quantity in cart.items():
        try:
            product_id, quantity = int(product_id), int(quantity)
        except (TypeError, ValueError):
            continue
        if product_id > 0 and quantity > 0:
            requested_quantities[product_id] = min(quantity, 99)
    products = Product.objects.filter(
        id__in=requested_quantities,
        is_available=True,
        quantity__gt=0,
    ).values("id", "quantity")
    count = sum(min(requested_quantities[product["id"]], product["quantity"]) for product in products)
    return {"cart_count": count}


def search_products(request):
    """Product data for the home-page search suggestions only."""
    if request.resolver_match and request.resolver_match.view_name == "shop:product_list":
        return {"search_products": list(Product.objects.values("id", "product_name", "product_code", "brand_name", "brand_code", "is_available"))}
    return {"search_products": []}
