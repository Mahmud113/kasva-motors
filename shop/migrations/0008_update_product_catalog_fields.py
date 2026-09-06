# Generated manually to preserve existing product names and product codes.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0007_product_stock_level"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="name",
            new_name="product_name",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="part_number",
            new_name="product_code",
        ),
        migrations.AlterField(
            model_name="product",
            name="product_name",
            field=models.CharField(max_length=180, verbose_name="Məhsul"),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_code",
            field=models.CharField(max_length=80, unique=True, verbose_name="Məhsul kodu"),
        ),
        migrations.AddField(
            model_name="product",
            name="brand_name",
            field=models.CharField(default="", max_length=120, verbose_name="Brend"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="brand_code",
            field=models.CharField(default="", max_length=80, verbose_name="Brend kodu"),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name="product",
            name="category",
        ),
        migrations.RemoveField(
            model_name="product",
            name="compatibility",
        ),
        migrations.RemoveField(
            model_name="product",
            name="image_url",
        ),
        migrations.AlterField(
            model_name="product",
            name="stock_level",
            field=models.CharField(
                choices=[("high", "Çox"), ("medium", "Orta"), ("low", "Az")],
                default="high",
                max_length=6,
                verbose_name="Stok səviyyəsi",
            ),
        ),
    ]
