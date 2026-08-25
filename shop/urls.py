from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "shop"
urlpatterns = [
    path("giris/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("cixis/", auth_views.LogoutView.as_view(), name="logout"),
    path("profilim/", views.profile, name="profile"),
    path("", views.product_list, name="product_list"), path("sebet/", views.cart_detail, name="cart_detail"),
    path("sebet/elave-et/<int:product_id>/", views.cart_add, name="cart_add"),
    path("sebet/yenile/<int:product_id>/", views.cart_update, name="cart_update"),
    path("elaqe/", views.contact, name="contact"),
]
