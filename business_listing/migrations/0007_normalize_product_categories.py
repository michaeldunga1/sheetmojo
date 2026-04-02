from django.db import migrations


def normalize_category(value):
    return " ".join((value or "").split()).title()


def normalize_product_categories(apps, schema_editor):
    Product = apps.get_model('business_listing', 'Product')
    for product in Product.objects.all().only('id', 'product_category'):
        normalized_category = normalize_category(product.product_category)
        if product.product_category != normalized_category:
            Product.objects.filter(pk=product.pk).update(product_category=normalized_category)


class Migration(migrations.Migration):

    dependencies = [
        ('business_listing', '0006_product'),
    ]

    operations = [
        migrations.RunPython(normalize_product_categories, migrations.RunPython.noop),
    ]