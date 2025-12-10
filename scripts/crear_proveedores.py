import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Supplier, Product

# Crear proveedores
proveedores = [
    {
        'name': 'Distribuidora Tecnológica S.A.',
        'rut': '76.123.456-7',
        'contact': 'Juan Pérez - contacto@distecno.cl - +56912345678'
    },
    {
        'name': 'Importadora Eléctrica Ltda.',
        'rut': '77.234.567-8',
        'contact': 'María González - ventas@impelec.cl - +56987654321'
    },
    {
        'name': 'Alimentos del Sur SpA',
        'rut': '78.345.678-9',
        'contact': 'Carlos Ramírez - info@alimentossur.cl - +56923456789'
    },
    {
        'name': 'FarmaSalud Distribuidora',
        'rut': '79.456.789-0',
        'contact': 'Ana Martínez - contacto@farmasalud.cl - +56934567890'
    },
    {
        'name': 'Ferretería Industrial Chile',
        'rut': '76.567.890-1',
        'contact': 'Roberto Silva - ventas@ferreind.cl - +56945678901'
    },
    {
        'name': 'Higiene y Limpieza Total',
        'rut': '77.678.901-2',
        'contact': 'Patricia López - info@higienetotal.cl - +56956789012'
    }
]

print("Creando proveedores...")
created_suppliers = []
for prov in proveedores:
    supplier, created = Supplier.objects.get_or_create(
        name=prov['name'],
        defaults=prov
    )
    created_suppliers.append(supplier)
    status = "✓ Creado" if created else "✓ Ya existe"
    print(f"{status}: {supplier.name}")

# Asignar proveedores a productos por categoría
print("\nAsignando proveedores a productos...")
categorias_proveedores = {
    # Hardware/Tecnología
    'Computadores': created_suppliers[0],
    'Accesorios': created_suppliers[0],
    'Periféricos': created_suppliers[0],
    'Monitores': created_suppliers[0],
    # Eléctricos
    'Iluminación': created_suppliers[1],
    'Cables': created_suppliers[1],
    'Protección': created_suppliers[1],
    # Alimentos
    'Granos': created_suppliers[2],
    'Aceites': created_suppliers[2],
    'Endulzantes': created_suppliers[2],
    'Harinas': created_suppliers[2],
    'Salsas': created_suppliers[2],
    # Farmacia
    'Analgésicos': created_suppliers[3],
    'Antiinflamatorios': created_suppliers[3],
    'Desinfectantes': created_suppliers[3],
    'Equipos': created_suppliers[3],
    # Ferretería
    'Herramientas Eléctricas': created_suppliers[4],
    'Herramientas Manuales': created_suppliers[4],
    'Medición': created_suppliers[4],
    # Higiene
    'Cuidado Personal': created_suppliers[5],
    'Higiene': created_suppliers[5],
    'Limpieza': created_suppliers[5]
}

products = Product.objects.all()
updated = 0

for product in products:
    if product.category in categorias_proveedores:
        product.supplier = categorias_proveedores[product.category]
        product.save()
        print(f"✓ {product.name} → {product.supplier.name}")
        updated += 1

print(f"\n{'='*50}")
print(f"Resumen:")
print(f"Proveedores en sistema: {len(created_suppliers)}")
print(f"Productos actualizados: {updated}")
print(f"{'='*50}")
