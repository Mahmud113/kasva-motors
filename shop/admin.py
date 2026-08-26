from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.db.models import F, Sum
from .models import Order, OrderItem, Product, StoreProfile

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
        ("Əlaqə məlumatları", {"fields": ("email",)}),
        ("Hesab statusu", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Vacib tarixlər", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "password1", "password2")}),
        ("Əlaqə məlumatları", {"fields": ("email",)}),
        ("Hesab statusu", {"fields": ("is_active", "is_staff")}),
    )

    list_display = ("username", "store_phone_number", "store_address", "email", "is_active", "is_staff")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("store_profile")

    @admin.display(description="Ünvan")
    def store_address(self, obj):
        return getattr(obj.store_profile, "address", "")

    @admin.display(description="Telefon nömrəsi")
    def store_phone_number(self, obj):
        return getattr(obj.store_profile, "phone_number", "")


class StoreProfileInline(admin.StackedInline):
    model = StoreProfile
    extra = 1
    max_num = 1
    can_delete = False
    fields = ("phone_number", "address")


StoreUserAdmin.inlines = (StoreProfileInline,)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "part_number", "category", "compatibility", "price", "quantity", "is_available", "created_at")
    list_filter = ("category", "compatibility", "is_available")
    search_fields = ("name", "part_number")
    list_editable = ("price", "quantity", "is_available")
    change_list_template = "admin/shop/product/change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["total_inventory"] = Product.objects.aggregate(
            total=Sum(F("price") * F("quantity"), default=0)
        )["total"]
        return super().changelist_view(request, extra_context=extra_context)


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
    exclude = ("first_name", "last_name")
    inlines = (OrderItemInline,)
    @admin.display(description="Mağaza istifadəçisi", ordering="customer__username")
    def customer(self, obj): return (obj.customer.get_full_name() or obj.customer.username) if obj.customer else "Təyin edilməyib"
