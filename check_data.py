import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Product, Inventory, Branch

print(f'\n📦 Total productos en BD: {Product.objects.count()}')
print(f'📊 Total inventarios: {Inventory.objects.count()}')
print(f'🏢 Total sucursales: {Branch.objects.count()}\n')

if Product.objects.count() == 0:
    print("⚠️  NO HAY PRODUCTOS EN LA BASE DE DATOS")
    print("Ejecuta: python populate_db.py")
else:
    print("✓ Hay productos en la base de datos")
    print("\nProductos por categoría:")
    from django.db.models import Count
    productos_por_categoria = Product.objects.values('category').annotate(total=Count('id')).order_by('category')
    for cat in productos_por_categoria:
        print(f"  • {cat['category']}: {cat['total']} productos")
    
    print("\nInventario por sucursal:")
    for branch in Branch.objects.all():
        total_items = Inventory.objects.filter(branch=branch).count()
        print(f"  • {branch.name}: {total_items} productos en stock")
