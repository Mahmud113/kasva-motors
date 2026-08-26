from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
    if not isinstance(cart, dict):
        request.session.pop("cart", None)
        return [], Decimal("0")
    product_ids = []
    quantities = {}
    for product_id, quantity in cart.items():
        try:
            product_id, quantity = int(product_id), int(quantity)
        except (TypeError, ValueError):
            continue
        if product_id > 0 and quantity > 0:
            product_ids.append(product_id)
            quantities[product_id] = min(quantity, 99)
    products = Product.objects.filter(id__in=product_ids, is_available=True, quantity__gt=0)
    items, total = [], Decimal("0")
    for product in products:
        quantity = min(quantities[product.id], product.quantity)
        subtotal = product.price * quantity
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    return items, total


@login_required
def cart_add(request, product_id):
    if request.method != "POST": return redirect("shop:product_list")
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    key = str(product.id)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    try:
        current_quantity = int(cart.get(key, 0))
    except (TypeError, ValueError):
        current_quantity = 0
    available_to_add = product.quantity - current_quantity
    if available_to_add <= 0:
        messages.error(request, f"{product.name} məhsulundan səbətdə əlavə edilə biləcək miqdar qalmayıb.")
        return redirect(request.POST.get("next") or "shop:cart_detail")
    requested_quantity = max(quantity, 1)
    if requested_quantity > available_to_add:
        messages.warning(request, f"{product.name} üçün maksimum mövcud miqdara çatmısınız.")
    cart[key] = current_quantity + min(requested_quantity, available_to_add, 99)
    request.session["cart"] = cart
    messages.success(request, f"{product.name} səbətə əlavə edildi.")
    return redirect(request.POST.get("next") or "shop:cart_detail")


@login_required
def cart_update(request, product_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        if not isinstance(cart, dict):
            cart = {}
        key = str(product_id)
        if request.POST.get("remove"):
            quantity = 0
        else:
            try:
                quantity = int(request.POST.get("quantity", 0))
            except (TypeError, ValueError):
                quantity = 0
        product = Product.objects.filter(pk=product_id, is_available=True).first()
        if quantity > 0 and product and product.quantity > 0:
            if quantity > product.quantity:
                messages.warning(request, f"{product.name} üçün maksimum mövcud miqdara çatmısınız.")
            cart[key] = min(quantity, product.quantity, 99)
        else:
            cart.pop(key, None)
        request.session["cart"] = cart
    return redirect("shop:cart_detail")


@login_required
def cart_detail(request):
    items, total = cart_items(request)
    if not items:
        if request.method == "POST":
            messages.error(request, "Səbətiniz boşdur.")
            return redirect("shop:product_list")
        return render(request, "shop/cart.html", {"items": items, "total": total})
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            locked_products = {
                product.id: product
                for product in Product.objects.select_for_update().filter(id__in=[item["product"].id for item in items])
            }
            for item in items:
                product = locked_products.get(item["product"].id)
                if not product or not product.is_available or product.quantity < item["quantity"]:
                    messages.error(request, f"{item['product'].name} üçün kifayət qədər stok yoxdur. Səbətinizi yeniləyin.")
                    return redirect("shop:cart_detail")
            order = form.save(commit=False)
            order.customer = request.user
            order.total_price = total
            order.save()
            OrderItem.objects.bulk_create([OrderItem(order=order, product=locked_products[i["product"].id], quantity=i["quantity"], price_at_purchase=i["product"].price) for i in items])
            for item in items:
                product = locked_products[item["product"].id]
                product.quantity -= item["quantity"]
                product.is_available = product.quantity > 0
                product.save(update_fields=("quantity", "is_available"))
        request.session.pop("cart", None)
        messages.success(request, "Sifarişiniz qəbul edildi. Tezliklə sizinlə əlaqə saxlayacağıq.")
        return redirect("shop:product_list")
    return render(request, "shop/cart.html", {"items": items, "total": total, "form": form})


@login_required
def profile(request):
    orders = request.user.orders.prefetch_related("orderitem_set__product")
    purchases = orders.filter(status=Order.Status.COMPLETED, payment_status=Order.PaymentStatus.PAID)
    return render(request, "shop/profile.html", {"orders": orders, "purchases": purchases})


def contact(request):
    return render(request, "shop/contact.html")
