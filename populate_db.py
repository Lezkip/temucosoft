import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, Branch, Supplier, Product, Inventory, Sale, SaleItem, Subscription, Purchase, PurchaseItem
from django.utils import timezone
from datetime import timedelta

# Limpiar datos existentes (excepto admin) - en el orden correcto para evitar errores de foreign key
print("Limpiando datos existentes...")
SaleItem.objects.all().delete()
Sale.objects.all().delete()
PurchaseItem.objects.all().delete()
Purchase.objects.all().delete()
Inventory.objects.all().delete()
Product.objects.all().delete()
Supplier.objects.all().delete()
Branch.objects.all().delete()
Subscription.objects.all().delete()
User.objects.exclude(username='admin').delete()

# Crear suscripciones
print("\nCreando suscripciones...")
subs = [
    Subscription.objects.create(
        company='temucosoft',
        plan_name='premium',
        start_date=timezone.now().date() - timedelta(days=30),
        end_date=timezone.now().date() + timedelta(days=335),
        active=True
    ),
    Subscription.objects.create(
        company='farmacias_cruz_verde',
        plan_name='standard',
        start_date=timezone.now().date() - timedelta(days=60),
        end_date=timezone.now().date() + timedelta(days=305),
        active=True
    ),
    Subscription.objects.create(
        company='supermercado_lider',
        plan_name='premium',
        start_date=timezone.now().date() - timedelta(days=90),
        end_date=timezone.now().date() + timedelta(days=275),
        active=True
    ),
    Subscription.objects.create(
        company='libreria_nacional',
        plan_name='basic',
        start_date=timezone.now().date() - timedelta(days=15),
        end_date=timezone.now().date() + timedelta(days=350),
        active=True
    ),
]
print(f"✓ {len(subs)} suscripciones creadas")

# Crear usuarios
print("\nCreando usuarios...")
usuarios = []

# TemucoSoft - Proveedor del software SaaS (super_admin gestiona toda la plataforma)
usuarios.extend([
    User.objects.create_user(username='soporte_tsoft', password='1234', email='soporte@temucosoft.cl', 
                            company='temucosoft', role='super_admin', first_name='Carlos', last_name='Rodríguez',
                            is_staff=True, is_superuser=True),
])

# Farmacias Cruz Verde - Cliente/Tenant de TemucoSoft
usuarios.extend([
    User.objects.create_user(username='admin_cliente', password='1234', email='admin@cruzverde.cl',
                            company='farmacias_cruz_verde', role='admin_cliente', first_name='Roberto', last_name='Pérez',
                            is_staff=True),
    User.objects.create_user(username='gerente_farmacia', password='1234', email='gerente@cruzverde.cl',
                            company='farmacias_cruz_verde', role='gerente', first_name='Ana', last_name='Martínez'),
    User.objects.create_user(username='vendedor_farmacia1', password='1234', email='vendedor1@cruzverde.cl',
                            company='farmacias_cruz_verde', role='vendedor', first_name='Luis', last_name='Torres'),
    User.objects.create_user(username='vendedor_farmacia2', password='1234', email='vendedor2@cruzverde.cl',
                            company='farmacias_cruz_verde', role='vendedor', first_name='Carmen', last_name='Silva'),
    User.objects.create_user(username='cliente_farmacia', password='1234', email='cliente@cruzverde.cl',
                            company='farmacias_cruz_verde', role='cliente_final', first_name='Pedro', last_name='Jiménez'),
])

# Supermercado Líder - Cliente/Tenant de TemucoSoft
usuarios.extend([
    User.objects.create_user(username='admin_cliente2', password='1234', email='admin@lider.cl',
                            company='supermercado_lider', role='admin_cliente', first_name='Jorge', last_name='Vargas',
                            is_staff=True),
    User.objects.create_user(username='gerente_lider', password='1234', email='gerente@lider.cl',
                            company='supermercado_lider', role='gerente', first_name='Patricia', last_name='Morales'),
    User.objects.create_user(username='vendedor_lider1', password='1234', email='vendedor1@lider.cl',
                            company='supermercado_lider', role='vendedor', first_name='Diego', last_name='Ramírez'),
    User.objects.create_user(username='vendedor_lider2', password='1234', email='vendedor2@lider.cl',
                            company='supermercado_lider', role='vendedor', first_name='Sofía', last_name='Contreras'),
    User.objects.create_user(username='cliente_lider', password='1234', email='cliente@lider.cl',
                            company='supermercado_lider', role='cliente_final', first_name='Laura', last_name='Herrera'),
])

# Librería Nacional - Cliente/Tenant de TemucoSoft
usuarios.extend([
    User.objects.create_user(username='admin_cliente3', password='1234', email='admin@libreria.cl',
                            company='libreria_nacional', role='admin_cliente', first_name='Fernando', last_name='Castro',
                            is_staff=True),
    User.objects.create_user(username='vendedor_libreria', password='1234', email='vendedor@libreria.cl',
                            company='libreria_nacional', role='vendedor', first_name='Isabel', last_name='Muñoz'),
    User.objects.create_user(username='cliente_libreria', password='1234', email='cliente@libreria.cl',
                            company='libreria_nacional', role='cliente_final', first_name='Andrés', last_name='Rojas'),
])

print(f"✓ {len(usuarios)} usuarios creados")

# Crear sucursales de los clientes/tenants (no de TemucoSoft)
print("\nCreando sucursales de los clientes...")
sucursales = [
    # Farmacias Cruz Verde (Cliente/Tenant)
    Branch.objects.create(name='Farmacia Cruz Verde Centro', address='Bulnes 667, Temuco', phone='+56452233445', company='farmacias_cruz_verde'),
    Branch.objects.create(name='Farmacia Cruz Verde Mall', address='Av. Alemania 945, Temuco', phone='+56452266778', company='farmacias_cruz_verde'),
    Branch.objects.create(name='Farmacia Cruz Verde Maipu', address='5 de Abril 1348, Maipu', phone='+56227788990', company='farmacias_cruz_verde'),
    
    # Supermercado Líder (Cliente/Tenant)
    Branch.objects.create(name='Líder Express Centro', address='Manuel Rodríguez 1050, Temuco', phone='+56452299001', company='supermercado_lider'),
    Branch.objects.create(name='Líder Express Norte', address='Av. Caupolicán 0140, Temuco', phone='+56452299002', company='supermercado_lider'),
    Branch.objects.create(name='Líder Santiago Centro', address='San Diego 850, Santiago', phone='+56223311223', company='supermercado_lider'),
    
    # Librería Nacional (Cliente/Tenant)
    Branch.objects.create(name='Librería Nacional Centro', address='Prat 565, Temuco', phone='+56452255667', company='libreria_nacional'),
]
print(f"✓ {len(sucursales)} sucursales creadas")

# Crear proveedores
print("\nCreando proveedores...")
proveedores = [
    Supplier.objects.create(name='Laboratorios Chile S.A.', rut='76123456-7', contact='Dr. Juan Pérez'),
    Supplier.objects.create(name='Distribuidora Médica del Sur', rut='77234567-8', contact='María López'),
    Supplier.objects.create(name='Distribuidora de Alimentos CCU', rut='78345678-9', contact='Pedro Sánchez'),
    Supplier.objects.create(name='Nestlé Chile', rut='79456789-0', contact='Carolina Vega'),
    Supplier.objects.create(name='Carozzi S.A.', rut='80567890-1', contact='Andrés Moreno'),
    Supplier.objects.create(name='Editorial Planeta Chile', rut='81678901-2', contact='Valeria Torres'),
    Supplier.objects.create(name='Distribuidora de Papelería Rhein', rut='82789012-3', contact='Gustavo Muñoz'),
    Supplier.objects.create(name='Importadora Tech Solutions', rut='83890123-4', contact='Roberto Díaz'),
]
print(f"✓ {len(proveedores)} proveedores creados")

# Crear productos
print("\nCreando productos...")
productos = []

# Productos de farmacia
productos.extend([
    Product.objects.create(name='Paracetamol 500mg', description='Analgésico y antipirético', price=2500, cost=1500, category='medicamentos', sku='MED-001', supplier=proveedores[0]),
    Product.objects.create(name='Ibuprofeno 400mg', description='Antiinflamatorio no esteroideo', price=3200, cost=1800, category='medicamentos', sku='MED-002', supplier=proveedores[0]),
    Product.objects.create(name='Amoxicilina 500mg', description='Antibiótico de amplio espectro', price=8500, cost=5000, category='medicamentos', sku='MED-003', supplier=proveedores[1]),
    Product.objects.create(name='Loratadina 10mg', description='Antihistamínico para alergias', price=4500, cost=2500, category='medicamentos', sku='MED-004', supplier=proveedores[0]),
    Product.objects.create(name='Omeprazol 20mg', description='Inhibidor de bomba de protones', price=6800, cost=4000, category='medicamentos', sku='MED-005', supplier=proveedores[1]),
    Product.objects.create(name='Vitamina C 1000mg', description='Suplemento vitamínico', price=5500, cost=3000, category='suplementos', sku='SUP-001', supplier=proveedores[0]),
    Product.objects.create(name='Termómetro Digital', description='Termómetro digital de precisión', price=8900, cost=5500, category='equipamiento', sku='EQP-001', supplier=proveedores[1]),
    Product.objects.create(name='Alcohol Gel 500ml', description='Desinfectante de manos', price=3500, cost=2000, category='higiene', sku='HIG-001', supplier=proveedores[1]),
])

# Productos de supermercado
productos.extend([
    Product.objects.create(name='Leche Entera 1L', description='Leche entera pasteurizada', price=890, cost=600, category='lacteos', sku='LAC-001', supplier=proveedores[3]),
    Product.objects.create(name='Pan Hallulla (6 unidades)', description='Pan fresco del día', price=1200, cost=700, category='panaderia', sku='PAN-001', supplier=proveedores[4]),
    Product.objects.create(name='Arroz Grado 1 (1kg)', description='Arroz de primera calidad', price=1450, cost=900, category='abarrotes', sku='ABA-001', supplier=proveedores[4]),
    Product.objects.create(name='Aceite Vegetal 900ml', description='Aceite vegetal refinado', price=2300, cost=1500, category='abarrotes', sku='ABA-002', supplier=proveedores[2]),
    Product.objects.create(name='Coca Cola 1.5L', description='Bebida gaseosa', price=1650, cost=1000, category='bebidas', sku='BEB-001', supplier=proveedores[2]),
    Product.objects.create(name='Yogurt Natural 125g', description='Yogurt natural sin azúcar', price=450, cost=300, category='lacteos', sku='LAC-002', supplier=proveedores[3]),
    Product.objects.create(name='Manzanas Royal (1kg)', description='Manzanas frescas', price=1890, cost=1200, category='frutas', sku='FRU-001', supplier=proveedores[2]),
    Product.objects.create(name='Tomates (1kg)', description='Tomates frescos', price=1450, cost=900, category='verduras', sku='VER-001', supplier=proveedores[2]),
    Product.objects.create(name='Fideos Espagueti 400g', description='Pasta italiana', price=890, cost=500, category='abarrotes', sku='ABA-003', supplier=proveedores[4]),
    Product.objects.create(name='Detergente en Polvo 1kg', description='Detergente para ropa', price=3200, cost=2000, category='limpieza', sku='LIM-001', supplier=proveedores[2]),
])

# Productos de librería
productos.extend([
    Product.objects.create(name='Cuaderno Universitario 100 hojas', description='Cuaderno espiral tapa dura', price=2500, cost=1500, category='papeleria', sku='PAP-001', supplier=proveedores[6]),
    Product.objects.create(name='Lápiz Grafito HB (caja 12 unid.)', description='Lápices de escritura', price=3200, cost=1800, category='papeleria', sku='PAP-002', supplier=proveedores[6]),
    Product.objects.create(name='Libro "Cien Años de Soledad"', description='Novela de Gabriel García Márquez', price=12500, cost=8000, category='libros', sku='LIB-001', supplier=proveedores[5]),
    Product.objects.create(name='Libro "El Principito"', description='Clásico de Antoine de Saint-Exupéry', price=8900, cost=6000, category='libros', sku='LIB-002', supplier=proveedores[5]),
    Product.objects.create(name='Mochila Escolar', description='Mochila resistente con compartimentos', price=18500, cost=12000, category='accesorios', sku='ACC-001', supplier=proveedores[6]),
    Product.objects.create(name='Calculadora Científica', description='Calculadora para estudiantes', price=15800, cost=10000, category='tecnologia', sku='TEC-001', supplier=proveedores[7]),
    Product.objects.create(name='Resma de Papel A4 (500 hojas)', description='Papel bond blanco', price=4500, cost=3000, category='papeleria', sku='PAP-003', supplier=proveedores[6]),
    Product.objects.create(name='Set de Plumones 12 colores', description='Plumones de colores', price=5800, cost=3500, category='papeleria', sku='PAP-004', supplier=proveedores[6]),
])

# Productos varios para la librería
productos.extend([
    Product.objects.create(name='Tijeras Escolares', description='Tijeras punta roma', price=2800, cost=1800, category='papeleria', sku='PAP-005', supplier=proveedores[6]),
    Product.objects.create(name='Pegamento en Barra 40g', description='Pegamento no tóxico', price=1500, cost=900, category='papeleria', sku='PAP-006', supplier=proveedores[6]),
    Product.objects.create(name='Carpeta 3 Anillos', description='Carpeta tamaño oficio', price=3200, cost=2000, category='papeleria', sku='PAP-007', supplier=proveedores[6]),
    Product.objects.create(name='Regla 30cm', description='Regla plástica transparente', price=800, cost=500, category='papeleria', sku='PAP-008', supplier=proveedores[6]),
])

print(f"✓ {len(productos)} productos creados")

# Crear inventario
print("\nCreando registros de inventario...")
inventarios = []
for producto in productos:
    if producto.category in ['medicamentos', 'suplementos', 'equipamiento', 'higiene']:
        sucursales_asignadas = sucursales[0:3]  # Farmacias
        cantidad_base = 100
    elif producto.category in ['lacteos', 'panaderia', 'abarrotes', 'bebidas', 'frutas', 'verduras', 'limpieza']:
        sucursales_asignadas = sucursales[3:6]  # Supermercados
        cantidad_base = 150
    elif producto.category in ['papeleria', 'libros', 'accesorios']:
        sucursales_asignadas = [sucursales[6]]  # Librería
        cantidad_base = 50
    else:
        sucursales_asignadas = sucursales[0:3]  # Por defecto farmacias
        cantidad_base = 75
    
    for sucursal in sucursales_asignadas:
        inventarios.append(
            Inventory.objects.create(
                product=producto,
                branch=sucursal,
                stock=cantidad_base,
                reorder_point=cantidad_base // 4
            )
        )

print(f"✓ {len(inventarios)} registros de inventario creados")

# Crear ventas
print("\nCreando ventas...")
ventas = []
vendedores = User.objects.filter(role='vendedor')

if vendedores.exists():
    for i in range(50):
        dias_atras = i % 30
        fecha_venta = timezone.now() - timedelta(days=dias_atras)
        vendedor = vendedores[i % vendedores.count()]
        sucursal = sucursales[i % len(sucursales)]
        
        venta = Sale.objects.create(
            user=vendedor,
            branch=sucursal,
            total=0,
            payment_method='cash',
            created_at=fecha_venta
        )
        
        num_items = (i % 4) + 2
        total_venta = 0
        productos_venta = productos[i*2:(i*2)+num_items] if (i*2)+num_items <= len(productos) else productos[:num_items]
        
        for producto in productos_venta:
            cantidad = (i % 3) + 1
            subtotal = producto.price * cantidad
            total_venta += subtotal
            
            SaleItem.objects.create(
                sale=venta,
                product=producto,
                quantity=cantidad,
                price=producto.price
            )
        
        venta.total = total_venta
        venta.save()
        ventas.append(venta)

    print(f"✓ {len(ventas)} ventas creadas")
else:
    print("⚠ No hay vendedores para crear ventas")

# Crear compras
print("\nCreando compras...")
compras = []
admin = User.objects.get(username='admin')

for i in range(20):
    dias_atras = i % 25
    fecha_compra = timezone.now() - timedelta(days=dias_atras)
    proveedor = proveedores[i % len(proveedores)]
    sucursal = sucursales[i % len(sucursales)]
    
    compra = Purchase.objects.create(
        supplier=proveedor,
        branch=sucursal,
        total=0,
        date=fecha_compra.date(),
        notes=f'Compra de reposición #{i+1}'
    )
    
    num_items = (i % 3) + 2
    total_compra = 0
    productos_compra = productos[i*3:(i*3)+num_items] if (i*3)+num_items <= len(productos) else productos[:num_items]
    
    for producto in productos_compra:
        cantidad = ((i % 5) + 1) * 10
        precio_compra = int(producto.price * 0.7)
        subtotal = precio_compra * cantidad
        total_compra += subtotal
        
        PurchaseItem.objects.create(
            purchase=compra,
            product=producto,
            quantity=cantidad,
            cost=precio_compra
        )
    
    compra.total = total_compra
    compra.save()
    compras.append(compra)

print(f"✓ {len(compras)} compras creadas")

print("\n" + "="*60)
print("¡DATOS FICTICIOS CREADOS EXITOSAMENTE!")
print("="*60)
print(f"\n📊 RESUMEN:")
print(f"  • {len(subs)} suscripciones")
print(f"  • {len(usuarios) + 1} usuarios (+ admin)")
print(f"  • {len(sucursales)} sucursales")
print(f"  • {len(proveedores)} proveedores")
print(f"  • {len(productos)} productos")
print(f"  • {len(inventarios)} registros de inventario")
print(f"  • {len(ventas)} ventas")
print(f"  • {len(compras)} compras")
print("\n🏢 MODELO DE NEGOCIO:")
print("  • TemucoSoft = Proveedor de software SaaS para gestión de inventario y ventas")
print("  • Clientes/Tenants = Empresas que arriendan el software (farmacias, supermercados, librerías)")
print("\n👥 ROLES DE USUARIO:")
print("  • super_admin = Administrador de TemucoSoft (gestiona toda la plataforma)")
print("  • admin_cliente = Dueño del negocio/tenant (control total de su empresa)")
print("  • gerente = Gestión de inventario, reportes, proveedores")
print("  • vendedor = Realiza ventas POS, gestiona caja (sin cambio de precios)")
print("  • cliente_final = Usuario público para e-commerce")
print("\n🏢 CLIENTES/TENANTS CON DATOS:")
print("  • farmacias_cruz_verde - Medicamentos y productos de salud (3 sucursales)")
print("  • supermercado_lider - Alimentos y productos de consumo (3 sucursales)")
print("  • libreria_nacional - Libros y papelería (1 sucursal)")
print("\n🔑 CREDENCIALES (todos con password: 1234):")
print("\n  TEMUCOSOFT (Proveedor del software):")
print("    • admin / temucosoft [super_admin - control total]")
print("    • soporte_tsoft / temucosoft [super_admin - soporte técnico]")
print("\n  CLIENTES/TENANTS:")
print("    • admin_cliente / farmacias_cruz_verde [admin_cliente - dueño]")
print("    • admin_cliente2 / supermercado_lider [admin_cliente - dueño]")
print("    • admin_cliente3 / libreria_nacional [admin_cliente - dueño]")
print("\n  Otros usuarios por empresa: gerente_*, vendedor_*, cliente_*")
print("="*60)
