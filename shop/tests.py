from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Product


class StorefrontTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Yağ filtri", part_number="OF-123", category="Filtrlər",
            price=Decimal("19.90"), is_available=True,
        )

    def test_home_page_is_azerbaijani_and_lists_products(self):
        response = self.client.get(reverse("shop:product_list"))
        self.assertContains(response, "Kasva Motors")
        self.assertContains(response, "Yağ filtri")
        self.assertContains(response, "Səbətə əlavə et")

    def test_cart_can_add_product(self):
        response = self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.assertRedirects(response, reverse("shop:cart_detail"))
        self.assertContains(self.client.get(reverse("shop:cart_detail")), "Yağ filtri")

    def test_checkout_creates_order_and_clears_cart(self):
        self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        response = self.client.post(reverse("shop:checkout"), {
            "first_name": "Aysel", "last_name": "Məmmədova", "phone_number": "050 205 48 48",
        }, follow=True)
        self.assertContains(response, "Sifarişiniz qəbul edildi")
        self.assertEqual(self.product.orderitem_set.count(), 1)
        self.assertNotIn("cart", self.client.session)

    def test_contact_page_shows_phone(self):
        response = self.client.get(reverse("shop:contact"))
        self.assertContains(response, "050 205 48 48")
