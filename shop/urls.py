from django.urls import path
from . import views

app_name = "shop"
urlpatterns = [
    path("", views.product_list, name="product_list"), path("sebət/", views.cart_detail, name="cart_detail"),
    path("sebət/əlavə-et/<int:product_id>/", views.cart_add, name="cart_add"),
    path("sebət/yenilə/<int:product_id>/", views.cart_update, name="cart_update"),
    path("sifariş/", views.checkout, name="checkout"), path("əlaqə/", views.contact, name="contact"),
]
