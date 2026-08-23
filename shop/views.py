from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm
from .models import Order, OrderItem, Product


def product_list(request):
    products = Product.objects.all()
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    brand = request.GET.get("brand", "")
    sort = request.GET.get("sort", "new")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(part_number__icontains=query))
    if category: products = products.filter(category=category)
    if brand: products = products.filter(compatibility__icontains=brand)
    orderings = {"price_asc": "price", "price_desc": "-price", "new": "-created_at"}
    products = products.order_by(orderings.get(sort, "-created_at"))
    return render(request, "shop/product_list.html", {
        "products": products, "categories": Product.objects.values_list("category", flat=True).distinct(),
        "brands": Product.objects.exclude(compatibility="").values_list("compatibility", flat=True).distinct(),
    })


def cart_items(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(id__in=cart, is_available=True)
    items, total = [], Decimal("0")
    for product in products:
        quantity = int(cart[str(product.id)])
        subtotal = product.price * quantity
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    return items, total


def cart_add(request, product_id):
    if request.method != "POST": return redirect("shop:product_list")
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    cart = request.session.get("cart", {})
    key = str(product.id)
    cart[key] = min(int(cart.get(key, 0)) + 1, 99)
    request.session["cart"] = cart
    messages.success(request, f"{product.name} səbətə əlavə edildi.")
    return redirect(request.POST.get("next") or "shop:cart_detail")


def cart_update(request, product_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        key = str(product_id)
        quantity = int(request.POST.get("quantity", 0))
        if quantity > 0: cart[key] = min(quantity, 99)
        else: cart.pop(key, None)
        request.session["cart"] = cart
    return redirect("shop:cart_detail")


def cart_detail(request):
    items, total = cart_items(request)
    return render(request, "shop/cart.html", {"items": items, "total": total})


def checkout(request):
    items, total = cart_items(request)
    if not items:
        messages.error(request, "Səbətiniz boşdur.")
        return redirect("shop:product_list")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = form.save(commit=False)
            order.total_price = total
            order.save()
            OrderItem.objects.bulk_create([OrderItem(order=order, product=i["product"], quantity=i["quantity"], price_at_purchase=i["product"].price) for i in items])
        request.session.pop("cart", None)
        messages.success(request, "Sifarişiniz qəbul edildi. Tezliklə sizinlə əlaqə saxlayacağıq.")
        return redirect("shop:product_list")
    return render(request, "shop/checkout.html", {"items": items, "total": total, "form": form})


def contact(request):
    return render(request, "shop/contact.html")
