from django.urls import path
from . import views

app_name = "shop"
urlpatterns = [
    path("", views.product_list, name="product_list"), path("sebet/", views.cart_detail, name="cart_detail"),
    path("sebet/elave-et/<int:product_id>/", views.cart_add, name="cart_add"),
    path("sebet/yenile/<int:product_id>/", views.cart_update, name="cart_update"),
    path("sifaris/", views.checkout, name="checkout"), path("elaqe/", views.contact, name="contact"),
]
