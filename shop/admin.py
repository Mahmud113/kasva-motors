from django.contrib import admin
from .models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "part_number", "category", "compatibility", "price", "is_available", "created_at")
    list_filter = ("category", "compatibility", "is_available")
    search_fields = ("name", "part_number")
    list_editable = ("price", "is_available")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price_at_purchase")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "phone_number", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("first_name", "last_name", "phone_number")
    list_editable = ("status",)
    readonly_fields = ("total_price", "created_at")
    inlines = (OrderItemInline,)
    def customer(self, obj): return f"{obj.first_name} {obj.last_name}"
    customer.short_description = "Müştəri"
