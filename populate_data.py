from core.models import User, Branch, Supplier, Product, Inventory, Sale, SaleItem, Subscription, Purchase, PurchaseItem
from django.utils import timezone
from datetime import timedelta

# Limpiar datos existentes (excepto admin)
print("Limpiando datos existentes...")
User.objects.exclude(username='admin').delete()
Branch.objects.all().delete()
Supplier.objects.all().delete()
Product.objects.all().delete()
Inventory.objects.all().delete()
Sale.objects.all().delete()
SaleItem.objects.all().delete()
Subscription.objects.all().delete()
Purchase.objects.all().delete()
PurchaseItem.objects.all().delete()

# Crear suscripciones para las empresas
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

# Crear usuarios para diferentes empresas
print("\nCreando usuarios...")
usuarios = []

# TemucoSoft - ya existe admin, agregar más usuarios
usuarios.extend([
    User.objects.create_user(username='gerente_tsoft', password='1234', email='gerente@temucosoft.cl', 
                            company='temucosoft', role='gerente', first_name='Carlos', last_name='Rodríguez'),
    User.objects.create_user(username='vendedor_tsoft', password='1234', email='vendedor@temucosoft.cl',
                            company='temucosoft', role='vendedor', first_name='María', last_name='González'),
])

# Farmacias Cruz Verde
usuarios.extend([
    User.objects.create_user(username='admin_farmacia', password='1234', email='admin@cruzverde.cl',
                            company='farmacias_cruz_verde', role='admin_cliente', first_name='Roberto', last_name='Pérez',
                            is_staff=True),
    User.objects.create_user(username='gerente_farmacia', password='1234', email='gerente@cruzverde.cl',
                            company='farmacias_cruz_verde', role='gerente', first_name='Ana', last_name='Martínez'),
    User.objects.create_user(username='vendedor_farmacia1', password='1234', email='vendedor1@cruzverde.cl',
                            company='farmacias_cruz_verde', role='vendedor', first_name='Luis', last_name='Torres'),
    User.objects.create_user(username='vendedor_farmacia2', password='1234', email='vendedor2@cruzverde.cl',
                            company='farmacias_cruz_verde', role='vendedor', first_name='Carmen', last_name='Silva'),
])

# Supermercado Líder
usuarios.extend([
    User.objects.create_user(username='admin_lider', password='1234', email='admin@lider.cl',
                            company='supermercado_lider', role='admin_cliente', first_name='Jorge', last_name='Vargas',
                            is_staff=True),
    User.objects.create_user(username='gerente_lider', password='1234', email='gerente@lider.cl',
                            company='supermercado_lider', role='gerente', first_name='Patricia', last_name='Morales'),
    User.objects.create_user(username='vendedor_lider1', password='1234', email='vendedor1@lider.cl',
                            company='supermercado_lider', role='vendedor', first_name='Diego', last_name='Ramírez'),
    User.objects.create_user(username='vendedor_lider2', password='1234', email='vendedor2@lider.cl',
                            company='supermercado_lider', role='vendedor', first_name='Sofía', last_name='Contreras'),
])

# Librería Nacional
usuarios.extend([
    User.objects.create_user(username='admin_libreria', password='1234', email='admin@libreria.cl',
                            company='libreria_nacional', role='admin_cliente', first_name='Fernando', last_name='Castro',
                            is_staff=True),
    User.objects.create_user(username='vendedor_libreria', password='1234', email='vendedor@libreria.cl',
                            company='libreria_nacional', role='vendedor', first_name='Isabel', last_name='Muñoz'),
])

print(f"✓ {len(usuarios)} usuarios creados")

# Crear sucursales
print("\nCreando sucursales...")
sucursales = [
    # TemucoSoft
    Branch.objects.create(name='TemucoSoft Central', address='Av. Alemania 0281, Temuco', phone='+56452211234'),
    Branch.objects.create(name='TemucoSoft Santiago', address='Av. Providencia 1208, Santiago', phone='+56223344556'),
    
    # Farmacias Cruz Verde
    Branch.objects.create(name='Farmacia Cruz Verde Centro', address='Bulnes 667, Temuco', phone='+56452233445'),
    Branch.objects.create(name='Farmacia Cruz Verde Mall', address='Av. Alemania 945, Temuco', phone='+56452266778'),
    Branch.objects.create(name='Farmacia Cruz Verde Maipu', address='5 de Abril 1348, Maipu', phone='+56227788990'),
    
    # Supermercado Líder
    Branch.objects.create(name='Líder Express Centro', address='Manuel Rodríguez 1050, Temuco', phone='+56452299001'),
    Branch.objects.create(name='Líder Express Norte', address='Av. Caupolicán 0140, Temuco', phone='+56452299002'),
    Branch.objects.create(name='Líder Santiago Centro', address='San Diego 850, Santiago', phone='+56223311223'),
    
    # Librería Nacional
    Branch.objects.create(name='Librería Nacional Centro', address='Prat 565, Temuco', phone='+56452255667'),
]
print(f"✓ {len(sucursales)} sucursales creadas")

# Crear proveedores
print("\nCreando proveedores...")
proveedores = [
    # Proveedores de farmacia
    Supplier.objects.create(name='Laboratorios Chile S.A.', rut='76123456-7', contact='Dr. Juan Pérez'),
    Supplier.objects.create(name='Distribuidora Médica del Sur', rut='77234567-8', contact='María López'),
    
    # Proveedores de alimentos
    Supplier.objects.create(name='Distribuidora de Alimentos CCU', rut='78345678-9', contact='Pedro Sánchez'),
    Supplier.objects.create(name='Nestlé Chile', rut='79456789-0', contact='Carolina Vega'),
    Supplier.objects.create(name='Carozzi S.A.', rut='80567890-1', contact='Andrés Moreno'),
    
    # Proveedores de librería
    Supplier.objects.create(name='Editorial Planeta Chile', rut='81678901-2', contact='Valeria Torres'),
    Supplier.objects.create(name='Distribuidora de Papelería Rhein', rut='82789012-3', contact='Gustavo Muñoz'),
    
    # Proveedores generales
    Supplier.objects.create(name='Importadora Tech Solutions', rut='83890123-4', contact='Roberto Díaz'),
]
print(f"✓ {len(proveedores)} proveedores creados")

# Crear productos por categoría
print("\nCreando productos...")
productos = []

# Productos de farmacia (Farmacias Cruz Verde)
productos.extend([
    Product.objects.create(name='Paracetamol 500mg', description='Analgésico y antipirético', price=Decimal('2500.00'), stock=500, category='medicamentos', sku='MED-001', supplier=proveedores[0]),
    Product.objects.create(name='Ibuprofeno 400mg', description='Antiinflamatorio no esteroideo', price=Decimal('3200.00'), stock=350, category='medicamentos', sku='MED-002', supplier=proveedores[0]),
    Product.objects.create(name='Amoxicilina 500mg', description='Antibiótico de amplio espectro', price=Decimal('8500.00'), stock=200, category='medicamentos', sku='MED-003', supplier=proveedores[1]),
    Product.objects.create(name='Loratadina 10mg', description='Antihistamínico para alergias', price=Decimal('4500.00'), stock=300, category='medicamentos', sku='MED-004', supplier=proveedores[0]),
    Product.objects.create(name='Omeprazol 20mg', description='Inhibidor de bomba de protones', price=Decimal('6800.00'), stock=250, category='medicamentos', sku='MED-005', supplier=proveedores[1]),
    Product.objects.create(name='Vitamina C 1000mg', description='Suplemento vitamínico', price=Decimal('5500.00'), stock=400, category='suplementos', sku='SUP-001', supplier=proveedores[0]),
    Product.objects.create(name='Termómetro Digital', description='Termómetro digital de precisión', price=Decimal('8900.00'), stock=80, category='equipamiento', sku='EQP-001', supplier=proveedores[1]),
    Product.objects.create(name='Alcohol Gel 500ml', description='Desinfectante de manos', price=Decimal('3500.00'), stock=600, category='higiene', sku='HIG-001', supplier=proveedores[1]),
])

# Productos de supermercado (Líder)
productos.extend([
    Product.objects.create(name='Leche Entera 1L', description='Leche entera pasteurizada', price=Decimal('890.00'), stock=1200, category='lacteos', sku='LAC-001', supplier=proveedores[3]),
    Product.objects.create(name='Pan Hallulla (6 unidades)', description='Pan fresco del día', price=Decimal('1200.00'), stock=800, category='panaderia', sku='PAN-001', supplier=proveedores[4]),
    Product.objects.create(name='Arroz Grado 1 (1kg)', description='Arroz de primera calidad', price=Decimal('1450.00'), stock=500, category='abarrotes', sku='ABA-001', supplier=proveedores[4]),
    Product.objects.create(name='Aceite Vegetal 900ml', description='Aceite vegetal refinado', price=Decimal('2300.00'), stock=350, category='abarrotes', sku='ABA-002', supplier=proveedores[2]),
    Product.objects.create(name='Coca Cola 1.5L', description='Bebida gaseosa', price=Decimal('1650.00'), stock=900, category='bebidas', sku='BEB-001', supplier=proveedores[2]),
    Product.objects.create(name='Yogurt Natural 125g', description='Yogurt natural sin azúcar', price=Decimal('450.00'), stock=700, category='lacteos', sku='LAC-002', supplier=proveedores[3]),
    Product.objects.create(name='Manzanas Royal (1kg)', description='Manzanas frescas', price=Decimal('1890.00'), stock=400, category='frutas', sku='FRU-001', supplier=proveedores[2]),
    Product.objects.create(name='Tomates (1kg)', description='Tomates frescos', price=Decimal('1450.00'), stock=350, category='verduras', sku='VER-001', supplier=proveedores[2]),
    Product.objects.create(name='Fideos Espagueti 400g', description='Pasta italiana', price=Decimal('890.00'), stock=600, category='abarrotes', sku='ABA-003', supplier=proveedores[4]),
    Product.objects.create(name='Detergente en Polvo 1kg', description='Detergente para ropa', price=Decimal('3200.00'), stock=250, category='limpieza', sku='LIM-001', supplier=proveedores[2]),
])

# Productos de librería
productos.extend([
    Product.objects.create(name='Cuaderno Universitario 100 hojas', description='Cuaderno espiral tapa dura', price=Decimal('2500.00'), stock=300, category='papeleria', sku='PAP-001', supplier=proveedores[6]),
    Product.objects.create(name='Lápiz Grafito HB (caja 12 unid.)', description='Lápices de escritura', price=Decimal('3200.00'), stock=200, category='papeleria', sku='PAP-002', supplier=proveedores[6]),
    Product.objects.create(name='Libro "Cien Años de Soledad"', description='Novela de Gabriel García Márquez', price=Decimal('12500.00'), stock=50, category='libros', sku='LIB-001', supplier=proveedores[5]),
    Product.objects.create(name='Libro "El Principito"', description='Clásico de Antoine de Saint-Exupéry', price=Decimal('8900.00'), stock=80, category='libros', sku='LIB-002', supplier=proveedores[5]),
    Product.objects.create(name='Mochila Escolar', description='Mochila resistente con compartimentos', price=Decimal('18500.00'), stock=45, category='accesorios', sku='ACC-001', supplier=proveedores[6]),
    Product.objects.create(name='Calculadora Científica', description='Calculadora para estudiantes', price=Decimal('15800.00'), stock=60, category='tecnologia', sku='TEC-001', supplier=proveedores[7]),
    Product.objects.create(name='Resma de Papel A4 (500 hojas)', description='Papel bond blanco', price=Decimal('4500.00'), stock=150, category='papeleria', sku='PAP-003', supplier=proveedores[6]),
    Product.objects.create(name='Set de Plumones 12 colores', description='Plumones de colores', price=Decimal('5800.00'), stock=120, category='papeleria', sku='PAP-004', supplier=proveedores[6]),
])

# Productos de tecnología (TemucoSoft)
productos.extend([
    Product.objects.create(name='Mouse Inalámbrico', description='Mouse óptico inalámbrico', price=Decimal('12500.00'), stock=100, category='tecnologia', sku='TEC-002', supplier=proveedores[7]),
    Product.objects.create(name='Teclado USB', description='Teclado estándar USB', price=Decimal('18900.00'), stock=75, category='tecnologia', sku='TEC-003', supplier=proveedores[7]),
    Product.objects.create(name='Webcam HD 1080p', description='Cámara web alta definición', price=Decimal('35000.00'), stock=40, category='tecnologia', sku='TEC-004', supplier=proveedores[7]),
    Product.objects.create(name='Cable HDMI 2m', description='Cable de video y audio', price=Decimal('8500.00'), stock=150, category='tecnologia', sku='TEC-005', supplier=proveedores[7]),
])

print(f"✓ {len(productos)} productos creados")

# Crear inventario para diferentes sucursales
print("\nCreando registros de inventario...")
inventarios = []
for i, producto in enumerate(productos):
    # Asignar productos a sucursales según la empresa
    if producto.category in ['medicamentos', 'suplementos', 'equipamiento', 'higiene']:
        # Productos de farmacia
        sucursales_asignadas = sucursales[2:5]  # Farmacias
    elif producto.category in ['lacteos', 'panaderia', 'abarrotes', 'bebidas', 'frutas', 'verduras', 'limpieza']:
        # Productos de supermercado
        sucursales_asignadas = sucursales[5:8]  # Supermercados
    elif producto.category in ['papeleria', 'libros', 'accesorios']:
        # Productos de librería
        sucursales_asignadas = [sucursales[8]]  # Librería
    else:
        # Productos de tecnología
        sucursales_asignadas = sucursales[0:2]  # TemucoSoft
    
    for sucursal in sucursales_asignadas:
        cantidad = producto.stock // len(sucursales_asignadas)
        inventarios.append(
            Inventory.objects.create(
                product=producto,
                branch=sucursal,
                quantity=cantidad,
                last_updated=timezone.now()
            )
        )

print(f"✓ {len(inventarios)} registros de inventario creados")

# Crear ventas
print("\nCreando ventas...")
ventas = []
admin = User.objects.get(username='admin')
vendedores = User.objects.filter(role='vendedor')

# Crear 50 ventas con diferentes fechas
for i in range(50):
    dias_atras = i % 30
    fecha_venta = timezone.now() - timedelta(days=dias_atras)
    
    # Seleccionar vendedor y sucursal
    vendedor = vendedores[i % vendedores.count()]
    sucursal = sucursales[i % len(sucursales)]
    
    # Crear venta
    venta = Sale.objects.create(
        user=vendedor,
        branch=sucursal,
        total=Decimal('0.00'),
        date=fecha_venta
    )
    
    # Agregar items a la venta (2-5 productos por venta)
    num_items = (i % 4) + 2
    total_venta = Decimal('0.00')
    
    productos_venta = productos[i*2:(i*2)+num_items] if (i*2)+num_items <= len(productos) else productos[:num_items]
    
    for producto in productos_venta:
        cantidad = (i % 3) + 1
        subtotal = producto.price * cantidad
        total_venta += subtotal
        
        SaleItem.objects.create(
            sale=venta,
            product=producto,
            quantity=cantidad,
            price=producto.price,
            subtotal=subtotal
        )
    
    # Actualizar total de la venta
    venta.total = total_venta
    venta.save()
    ventas.append(venta)

print(f"✓ {len(ventas)} ventas creadas")

# Crear compras
print("\nCreando compras...")
compras = []
for i in range(20):
    dias_atras = i % 25
    fecha_compra = timezone.now() - timedelta(days=dias_atras)
    
    proveedor = proveedores[i % len(proveedores)]
    sucursal = sucursales[i % len(sucursales)]
    
    compra = Purchase.objects.create(
        supplier=proveedor,
        branch=sucursal,
        total=Decimal('0.00'),
        date=fecha_compra,
        created_by=admin
    )
    
    # Agregar items a la compra
    num_items = (i % 3) + 2
    total_compra = Decimal('0.00')
    
    productos_compra = productos[i*3:(i*3)+num_items] if (i*3)+num_items <= len(productos) else productos[:num_items]
    
    for producto in productos_compra:
        cantidad = ((i % 5) + 1) * 10
        precio_compra = producto.price * Decimal('0.7')  # 70% del precio de venta
        subtotal = precio_compra * cantidad
        total_compra += subtotal
        
        PurchaseItem.objects.create(
            purchase=compra,
            product=producto,
            quantity=cantidad,
            price=precio_compra,
            subtotal=subtotal
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
print("\n🏢 EMPRESAS CON DATOS:")
print("  • temucosoft - Productos de tecnología")
print("  • farmacias_cruz_verde - Medicamentos y salud")
print("  • supermercado_lider - Alimentos y productos varios")
print("  • libreria_nacional - Libros y papelería")
print("\n🔑 CREDENCIALES (todos con password: 1234):")
print("  • admin / temucosoft")
print("  • admin_farmacia / farmacias_cruz_verde")
print("  • admin_lider / supermercado_lider")
print("  • admin_libreria / libreria_nacional")
print("="*60)
