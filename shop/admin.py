from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from .models import Order, OrderItem, Product

# Django-nun hazır istifadəçi idarəetmə səhifəsini saxlayırıq, sadəcə admin
# menyusundakı ingiliscə başlıqları Azərbaycan dilində göstəririk.
User._meta.verbose_name = "İstifadəçi"
User._meta.verbose_name_plural = "İstifadəçilər"
Group._meta.verbose_name = "Qrup"
Group._meta.verbose_name_plural = "Qruplar"

# The supplier has no need for user-managed groups or per-user permissions.
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(User)
class StoreUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Şəxsi məlumatlar", {"fields": ("first_name", "last_name", "email")}),
        ("Hesab statusu", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Vacib tarixlər", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "password1", "password2")}),
        ("Şəxsi məlumatlar", {"fields": ("first_name", "last_name", "email")}),
        ("Hesab statusu", {"fields": ("is_active", "is_staff")}),
    )


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
    list_display = ("id", "customer", "phone_number", "delivery_method", "total_price", "payment_status", "status", "created_at")
    list_filter = ("delivery_method", "payment_status", "status", "created_at")
    search_fields = ("customer__username", "customer__first_name", "customer__last_name", "phone_number")
    list_editable = ("payment_status", "status")
    readonly_fields = ("customer", "phone_number", "delivery_method", "total_price", "created_at")
    inlines = (OrderItemInline,)
    @admin.display(description="Mağaza istifadəçisi", ordering="customer__username")
    def customer(self, obj): return (obj.customer.get_full_name() or obj.customer.username) if obj.customer else "Təyin edilməyib"
