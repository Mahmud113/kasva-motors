from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0008_update_product_catalog_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="product_code",
            field=models.CharField(max_length=80, verbose_name="Məhsul kodu"),
        ),
    ]
