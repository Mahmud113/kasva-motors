from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Kasva Motors İdarəetmə Paneli"
admin.site.site_title = "Kasva Motors Admin"
admin.site.index_title = "Mağaza idarəetməsi"

urlpatterns = [path("admin/", admin.site.urls), path("", include("shop.urls"))]
