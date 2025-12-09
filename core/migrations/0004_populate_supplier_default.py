from django.db import migrations


def set_default_supplier(apps, schema_editor):
    Supplier = apps.get_model('core', 'Supplier')
    Product = apps.get_model('core', 'Product')

    supplier, _ = Supplier.objects.get_or_create(
        name='Proveedor Genérico',
        defaults={
            'rut': '12.345.678-5',  # RUT válido según módulo 11
            'contact': 'contacto@proveedor.com',
        }
    )
    Product.objects.filter(supplier__isnull=True).update(supplier=supplier)


def unset_default_supplier(apps, schema_editor):
    Supplier = apps.get_model('core', 'Supplier')
    Product = apps.get_model('core', 'Product')

    try:
        supplier = Supplier.objects.get(name='Proveedor Genérico')
    except Supplier.DoesNotExist:
        return

    Product.objects.filter(supplier=supplier).update(supplier=None)


def preserve_supplier(apps, schema_editor):
    """No-op placeholder to avoid reverse data loss for supplier changes."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_supplier_to_product'),
    ]

    operations = [
        migrations.RunPython(set_default_supplier, unset_default_supplier),
    ]
