import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from shop.models import Order, Product


REQUIRED_COLUMNS = ("mehsul", "mehsul kodu", "brend", "brend kodu", "qiymet", "stock")


class Command(BaseCommand):
    help = "Replace confirmed test catalog data with products from a CSV export."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=Path)

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        if not csv_path.is_file():
            raise CommandError(f"CSV file not found: {csv_path}")

        with csv_path.open(encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames != list(REQUIRED_COLUMNS):
                raise CommandError(f"Expected columns: {', '.join(REQUIRED_COLUMNS)}")
            rows = list(reader)

        products = []
        for line_number, row in enumerate(rows, start=2):
            values = {column: row[column].strip() for column in REQUIRED_COLUMNS}
            if not all(values.values()):
                raise CommandError(f"Line {line_number} has an empty required value.")
            try:
                price = Decimal(values["qiymet"])
                quantity = int(values["stock"])
            except (InvalidOperation, ValueError) as error:
                raise CommandError(f"Line {line_number} has an invalid price or stock value.") from error
            if price < 0 or quantity < 0:
                raise CommandError(f"Line {line_number} has a negative price or stock value.")
            products.append(Product(
                product_name=values["mehsul"],
                product_code=values["mehsul kodu"],
                brand_name=values["brend"],
                brand_code=values["brend kodu"],
                price=price,
                quantity=quantity,
                stock_level=Product.StockLevel.HIGH,
                is_available=quantity > 0,
            ))

        with transaction.atomic():
            old_products = Product.objects.all()
            old_product_ids = list(old_products.values_list("id", flat=True))
            test_orders = Order.objects.filter(orderitem__product_id__in=old_product_ids).distinct()
            if test_orders.exclude(orderitem__product_id__in=old_product_ids).exists():
                raise CommandError("A test order also contains a non-test product; no data was changed.")
            order_count = test_orders.count()
            test_orders.delete()
            deleted_product_count, _ = old_products.delete()
            Product.objects.bulk_create(products)

        self.stdout.write(self.style.SUCCESS(
            f"Deleted {deleted_product_count} test products and {order_count} test orders; imported {len(products)} products."
        ))
