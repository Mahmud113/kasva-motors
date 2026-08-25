from django.core.validators import MinValueValidator
from django.conf import settings
from django.db import models


class Product(models.Model):
    name = models.CharField("Ad", max_length=180)
    part_number = models.CharField("Hissə nömrəsi", max_length=80, unique=True)
    category = models.CharField("Kateqoriya", max_length=100)
    compatibility = models.CharField("Avtomobil markası", max_length=120, blank=True)
    price = models.DecimalField("Qiymət", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image_url = models.URLField("Şəkil ünvanı", blank=True)
    is_available = models.BooleanField("Mövcuddur", default=True)
    created_at = models.DateTimeField("Yaradılma tarixi", auto_now_add=True)

    class Meta:
        verbose_name = "Məhsul"
        verbose_name_plural = "Məhsullar"
        ordering = ["-created_at"]

    def __str__(self): return f"{self.name} ({self.part_number})"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Gözləmədə"
        READY = "ready", "Təhvil almağa hazırdır"
        COMPLETED = "completed", "Tamamlandı"
        CANCELLED = "cancelled", "Ləğv edildi"
    class DeliveryMethod(models.TextChoices):
        PICKUP = "pickup", "Özüm götürəcəyəm"
        PAID_TAXI = "paid_taxi", "Ödənişli taksi ilə göndərilsin"
        FREE_DELIVERY = "free_delivery", "Pulsuz 1-2 günə çatdırılma"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Ödənilməyib"
        PAID = "paid", "Ödənilib"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Mağaza istifadəçisi", related_name="orders", null=True, blank=True)
    # Köhnə sifariş qeydlərini qorumaq üçün saxlanılır; yeni sifarişlər istifadəçi hesabına bağlanır.
    first_name = models.CharField("Ad", max_length=80, blank=True)
    last_name = models.CharField("Soyad", max_length=80, blank=True)
    phone_number = models.CharField("Telefon nömrəsi", max_length=30)
    delivery_method = models.CharField("Çatdırılma üsulu", max_length=20, choices=DeliveryMethod.choices, default=DeliveryMethod.PICKUP)
    payment_status = models.CharField("Ödəniş statusu", max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    total_price = models.DecimalField("Ümumi məbləğ", max_digits=10, decimal_places=2)
    status = models.CharField("Status", max_length=15, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField("Sifariş tarixi", auto_now_add=True)

    class Meta:
        verbose_name = "Sifariş"
        verbose_name_plural = "Sifarişlər"
        ordering = ["-created_at"]

    def __str__(self): return f"#{self.pk} — {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Sifariş")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Məhsul")
    quantity = models.PositiveIntegerField("Miqdar", validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField("Alış qiyməti", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Sifariş məhsulu"
        verbose_name_plural = "Sifariş məhsulları"

    def __str__(self): return f"{self.product} × {self.quantity}"
