from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Product


class StorefrontTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="magaza1", password="guclu-sifre")
        self.product = Product.objects.create(
            name="Yağ filtri", part_number="OF-123", category="Filtrlər",
            price=Decimal("19.90"), is_available=True,
        )

    def test_home_page_is_azerbaijani_and_lists_products(self):
        response = self.client.get(reverse("shop:product_list"))
        self.assertContains(response, "Kasva Motors")
        self.assertContains(response, "Yağ filtri")
        self.assertContains(response, "Səbətə əlavə et")
        self.assertContains(response, "shop/images/kasva-motors-logo.png")

    def test_cart_can_add_product(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.assertRedirects(response, reverse("shop:cart_detail"))
        self.assertContains(self.client.get(reverse("shop:cart_detail")), "Yağ filtri")

    def test_checkout_creates_order_and_clears_cart(self):
        self.client.force_login(self.user)
        self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        response = self.client.post(reverse("shop:checkout"), {
            "phone_number": "050 205 48 48", "delivery_method": "pickup",
        }, follow=True)
        self.assertContains(response, "Sifarişiniz qəbul edildi")
        self.assertEqual(self.product.orderitem_set.count(), 1)
        self.assertNotIn("cart", self.client.session)
        order = self.product.orderitem_set.get().order
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.delivery_method, "pickup")

    def test_login_is_required_to_add_to_cart(self):
        response = self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.assertRedirects(response, f"{reverse('shop:login')}?next={reverse('shop:cart_add', args=[self.product.id])}")

    def test_profile_shows_users_order_history(self):
        self.client.force_login(self.user)
        self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.client.post(reverse("shop:checkout"), {"phone_number": "050 205 48 48", "delivery_method": "free_delivery"})
        response = self.client.get(reverse("shop:profile"))
        self.assertContains(response, "Sifariş tarixçəsi")
        self.assertContains(response, "Pulsuz 1-2 günə çatdırılma")

    def test_contact_page_shows_phone(self):
        response = self.client.get(reverse("shop:contact"))
        self.assertEqual(reverse("shop:contact"), "/elaqe/")
        self.assertContains(response, "050 205 48 48")
        self.assertContains(response, "099 205 48 48")
        self.assertContains(response, "40.3904259")
