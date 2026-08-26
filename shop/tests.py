from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import reverse

from .models import Product, StoreProfile


class StorefrontTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="magaza1", password="guclu-sifre")
        self.product = Product.objects.create(
            name="Yağ filtri", part_number="OF-123", category="Filtrlər",
            price=Decimal("19.90"), quantity=10, is_available=True,
        )

    def test_home_page_is_azerbaijani_and_lists_products(self):
        response = self.client.get(reverse("shop:product_list"))
        self.assertContains(response, "Kasva Motors")
        self.assertContains(response, "Yağ filtri")
        self.assertContains(response, "Səbətə əlavə et")
        self.assertContains(response, "Miqdar")
        self.assertContains(response, "Orta")
        self.assertContains(response, "shop/images/kasva-motors-logo.png")
        self.assertContains(response, "product-search-data")
        self.assertContains(response, "shop/search.js")

    def test_product_image_button_only_appears_when_an_image_exists(self):
        response = self.client.get(reverse("shop:product_list"))
        self.assertNotContains(response, "data-product-image")
        self.product.image_url = "https://example.com/product.jpg"
        self.product.save()
        response = self.client.get(reverse("shop:product_list"))
        self.assertContains(response, "data-product-image")

    def test_groups_are_not_registered_in_the_admin(self):
        self.assertNotIn(Group, admin.site._registry)

    def test_store_address_is_saved_with_the_user_profile(self):
        profile = StoreProfile.objects.create(user=self.user, phone_number="+994 55 000 00 00", address="Bakı şəhəri, Nərimanov rayonu")
        self.assertEqual(profile.user.store_profile.address, "Bakı şəhəri, Nərimanov rayonu")
        self.assertEqual(profile.user.store_profile.phone_number, "+994 55 000 00 00")

    def test_product_admin_shows_total_inventory_value(self):
        self.product.quantity = 3
        self.product.save()
        admin_user = get_user_model().objects.create_superuser(username="admin", password="admin-password")
        self.client.force_login(admin_user)
        response = self.client.get("/admin/shop/product/")
        self.assertContains(response, "Ümumi inventar dəyəri")
        self.assertContains(response, "59,70 AZN")

    def test_order_admin_detail_shows_ordered_products(self):
        self.client.force_login(self.user)
        self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.client.post(reverse("shop:cart_detail"), {"delivery_method": "pickup"})
        order = self.product.orderitem_set.get().order
        admin_user = get_user_model().objects.create_superuser(username="admin", password="admin-password")
        self.client.force_login(admin_user)
        response = self.client.get(f"/admin/shop/order/{order.id}/change/")
        self.assertContains(response, "Sifariş edilən məhsullar")
        self.assertContains(response, "Yağ filtri")
        self.assertContains(response, "× 1")

    def test_cart_can_add_product(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.assertRedirects(response, reverse("shop:cart_detail"))
        self.assertContains(self.client.get(reverse("shop:cart_detail")), "Yağ filtri")

    def test_basket_quantity_is_limited_to_inventory(self):
        self.client.force_login(self.user)
        self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        response = self.client.post(reverse("shop:cart_update", args=[self.product.id]), {"quantity": 99}, follow=True)
        self.assertContains(response, "maksimum mövcud miqdara çatmısınız")
        self.assertEqual(self.client.session["cart"][str(self.product.id)], 10)

    def test_basket_confirmation_creates_order_and_clears_cart(self):
        self.client.force_login(self.user)
        self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        response = self.client.post(reverse("shop:cart_detail"), {"delivery_method": "pickup"}, follow=True)
        self.assertContains(response, "Sifarişiniz qəbul edildi")
        self.assertEqual(self.product.orderitem_set.count(), 1)
        self.assertNotIn("cart", self.client.session)
        order = self.product.orderitem_set.get().order
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.delivery_method, "pickup")
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 9)

    def test_login_is_required_to_add_to_cart(self):
        response = self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.assertRedirects(response, f"{reverse('shop:login')}?next={reverse('shop:cart_add', args=[self.product.id])}")

    def test_malformed_basket_session_does_not_cause_a_server_error(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["cart"] = {"invalid": "wrong", str(self.product.id): "2"}
        session.save()
        response = self.client.get(reverse("shop:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Yağ filtri")
        session["cart"] = "invalid"
        session.save()
        response = self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.assertEqual(response.status_code, 302)

    def test_profile_shows_users_order_history(self):
        self.client.force_login(self.user)
        self.client.post(reverse("shop:cart_add", args=[self.product.id]))
        self.client.post(reverse("shop:cart_detail"), {"delivery_method": "free_delivery"})
        response = self.client.get(reverse("shop:profile"))
        self.assertContains(response, "Sifariş tarixçəsi")
        self.assertContains(response, "Pulsuz 1-2 günə çatdırılma")

    def test_contact_page_shows_phone(self):
        response = self.client.get(reverse("shop:contact"))
        self.assertEqual(reverse("shop:contact"), "/elaqe/")
        self.assertContains(response, "+994 55 205 48 48")
        self.assertContains(response, "+994 99 205 48 48")
        self.assertContains(response, "40.3904259")
