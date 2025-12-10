import os
import sys
from pathlib import Path
import django
import re

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Branch, Product, Inventory

companies_catalog = {
    'Comercial Andes SA': [
        {'name': 'Notebook HP 15.6" Intel Core i5', 'description': 'Laptop ideal para trabajo y estudio, 8GB RAM, 256GB SSD', 'price': 549990, 'cost': 380000, 'category': 'Computadores', 'stock': 12, 'reorder': 3},
        {'name': 'Mouse Inalámbrico Logitech M185', 'description': 'Mouse ergonómico con conexión USB, batería de larga duración', 'price': 8990, 'cost': 5000, 'category': 'Accesorios', 'stock': 45, 'reorder': 10},
        {'name': 'Teclado Mecánico RGB Gamer', 'description': 'Teclado retroiluminado con switches mecánicos, ideal para gaming', 'price': 45990, 'cost': 28000, 'category': 'Periféricos', 'stock': 18, 'reorder': 5},
        {'name': 'Monitor LED 24" Full HD', 'description': 'Pantalla 1920x1080, 75Hz, HDMI, ideal para oficina', 'price': 129990, 'cost': 85000, 'category': 'Monitores', 'stock': 8, 'reorder': 2},
        {'name': 'Webcam Logitech C920 Full HD', 'description': 'Cámara web 1080p con micrófono estéreo', 'price': 69990, 'cost': 45000, 'category': 'Accesorios', 'stock': 20, 'reorder': 5},
    ],
    'TecnoSoft SPA': [
        {'name': 'Ampolleta LED 9W Luz Blanca', 'description': 'Bajo consumo, equivalente a 60W tradicional', 'price': 2990, 'cost': 1500, 'category': 'Iluminación', 'stock': 150, 'reorder': 30},
        {'name': 'Cable Eléctrico 2x14 AWG (rollo 100m)', 'description': 'Cable certificado para instalaciones domiciliarias', 'price': 45990, 'cost': 28000, 'category': 'Cables', 'stock': 25, 'reorder': 5},
        {'name': 'Enchufe Doble con Tierra 10A', 'description': 'Enchufe empotrable blanco, certificado SEC', 'price': 3990, 'cost': 2000, 'category': 'Accesorios', 'stock': 80, 'reorder': 15},
        {'name': 'Interruptor Automático 2P 32A', 'description': 'Protección termomagnética para tablero eléctrico', 'price': 18990, 'cost': 12000, 'category': 'Protección', 'stock': 35, 'reorder': 8},
        {'name': 'Reflector LED 50W IP65', 'description': 'Luz exterior resistente al agua, 4000 lúmenes', 'price': 24990, 'cost': 15000, 'category': 'Iluminación', 'stock': 18, 'reorder': 4},
    ],
    'Express Commerce CO': [
        {'name': 'Arroz Grado 1 (saco 25kg)', 'description': 'Arroz blanco de alta calidad para restaurantes', 'price': 19990, 'cost': 12000, 'category': 'Granos', 'stock': 40, 'reorder': 10},
        {'name': 'Aceite Vegetal Girasol 5L', 'description': 'Aceite refinado ideal para cocina profesional', 'price': 12990, 'cost': 8000, 'category': 'Aceites', 'stock': 60, 'reorder': 15},
        {'name': 'Azúcar Granulada (saco 50kg)', 'description': 'Azúcar blanca refinada para uso comercial', 'price': 35990, 'cost': 22000, 'category': 'Endulzantes', 'stock': 30, 'reorder': 8},
        {'name': 'Harina 0000 (saco 25kg)', 'description': 'Harina de trigo refinada para panificación', 'price': 24990, 'cost': 16000, 'category': 'Harinas', 'stock': 35, 'reorder': 10},
        {'name': 'Salsa de Tomate Industrial 5kg', 'description': 'Salsa concentrada para cocina profesional', 'price': 8990, 'cost': 5500, 'category': 'Salsas', 'stock': 55, 'reorder': 12},
    ],
    'RetailChile Store': [
        {'name': 'Paracetamol 500mg (caja 100 tabletas)', 'description': 'Analgésico y antipirético de uso general', 'price': 4990, 'cost': 2500, 'category': 'Analgésicos', 'stock': 200, 'reorder': 40},
        {'name': 'Ibuprofeno 400mg (caja 50 cápsulas)', 'description': 'Antiinflamatorio no esteroideo', 'price': 6990, 'cost': 3500, 'category': 'Antiinflamatorios', 'stock': 150, 'reorder': 30},
        {'name': 'Alcohol Gel 70% (frasco 500ml)', 'description': 'Desinfectante de manos con glicerina', 'price': 3990, 'cost': 2000, 'category': 'Desinfectantes', 'stock': 120, 'reorder': 25},
        {'name': 'Termómetro Digital Infrarrojo', 'description': 'Medición sin contacto, pantalla LCD', 'price': 19990, 'cost': 12000, 'category': 'Equipos', 'stock': 45, 'reorder': 10},
        {'name': 'Mascarilla Quirúrgica (caja 50 unidades)', 'description': 'Mascarillas desechables de 3 capas', 'price': 8990, 'cost': 5000, 'category': 'Protección', 'stock': 80, 'reorder': 20},
    ],
    'TechMarket Ltda': [
        {'name': 'Taladro Percutor Bosch 650W', 'description': 'Taladro profesional con maletín y brocas', 'price': 89990, 'cost': 55000, 'category': 'Herramientas Eléctricas', 'stock': 15, 'reorder': 3},
        {'name': 'Destornillador Set 12 piezas', 'description': 'Juego de destornilladores planos y estrella', 'price': 12990, 'cost': 7000, 'category': 'Herramientas Manuales', 'stock': 50, 'reorder': 10},
        {'name': 'Sierra Circular 7" 1400W', 'description': 'Sierra eléctrica con guía láser y disco', 'price': 79990, 'cost': 48000, 'category': 'Herramientas Eléctricas', 'stock': 12, 'reorder': 3},
        {'name': 'Nivel Láser Autonivelante', 'description': 'Nivel láser de línea cruzada 15m alcance', 'price': 45990, 'cost': 28000, 'category': 'Medición', 'stock': 18, 'reorder': 4},
        {'name': 'Cinta Métrica 8m Stanley', 'description': 'Cinta métrica con freno automático', 'price': 8990, 'cost': 5000, 'category': 'Medición', 'stock': 60, 'reorder': 15},
    ],
    'Distribuidora Central SPA': [
        {'name': 'Shampoo Pantene 400ml', 'description': 'Shampoo reparación total para todo tipo de cabello', 'price': 4990, 'cost': 2800, 'category': 'Cuidado Personal', 'stock': 100, 'reorder': 20},
        {'name': 'Papel Higiénico Elite (pack 24 rollos)', 'description': 'Papel suave triple hoja', 'price': 12990, 'cost': 7500, 'category': 'Higiene', 'stock': 80, 'reorder': 15},
        {'name': 'Detergente Líquido 3L', 'description': 'Detergente concentrado aroma lavanda', 'price': 8990, 'cost': 5200, 'category': 'Limpieza', 'stock': 65, 'reorder': 12},
        {'name': 'Cloro 5L', 'description': 'Desinfectante multiuso sin aroma', 'price': 3990, 'cost': 2000, 'category': 'Limpieza', 'stock': 90, 'reorder': 18},
        {'name': 'Cepillo Dental (pack 3 unidades)', 'description': 'Cepillos con cerdas suaves', 'price': 2990, 'cost': 1500, 'category': 'Cuidado Personal', 'stock': 150, 'reorder': 30},
    ],
}

created = []
for company, products in companies_catalog.items():
    slug = re.sub(r'[^a-z0-9]+', '-', company.lower()).strip('-') or 'empresa'
    branch, _ = Branch.objects.get_or_create(
        name=f'Sucursal {company}',
        defaults={'address': f'Dirección {company}', 'phone': '999999999'}
    )

    for idx, tpl in enumerate(products, start=1):
        sku = f"{slug}-sku{idx}"
        prod_defaults = {
            'name': tpl['name'],
            'description': tpl['description'],
            'price': tpl['price'],
            'cost': tpl['cost'],
            'category': tpl['category'],
        }
        product, _ = Product.objects.get_or_create(sku=sku, defaults=prod_defaults)
        inventory, inv_created = Inventory.objects.get_or_create(
            branch=branch,
            product=product,
            defaults={'stock': tpl['stock'], 'reorder_point': tpl['reorder']}
        )
        if not inv_created and inventory.stock == 0:
            inventory.stock = tpl['stock']
            inventory.reorder_point = tpl['reorder']
            inventory.save()
        created.append((company, branch.name, product.sku, inventory.stock))

print('Items cargados:', len(created))
print(created[:12])
