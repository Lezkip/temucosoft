from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils.dateparse import parse_date
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
import json

# Imports para Vistas Web (HTML)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Product, Branch, Supplier, Inventory, Sale, Order, User, OrderItem, SaleItem, Subscription, Purchase, PurchaseItem, CartItem
from .serializers import (
    ProductSerializer, BranchSerializer, SupplierSerializer,
    InventorySerializer, SaleSerializer, OrderSerializer, CartItemSerializer
)
from .permissions import IsAdminCliente, IsGerente, IsVendedor, HasAPIAccess

# ==========================================
# LÍMITES POR PLAN DE SUSCRIPCIÓN
# ==========================================
PLAN_FEATURES = {
    'basico': {
        'max_branches': 1,
        'max_users': 5,
        'reports': False,
        'api_access': False,
        'inventory_tracking': True,
        'pos_system': False,
    },
    'estandar': {
        'max_branches': 3,
        'max_users': 20,
        'reports': True,
        'api_access': False,
        'inventory_tracking': True,
        'pos_system': True,
    },
    'premium': {
        'max_branches': 999,
        'max_users': 999,
        'reports': True,
        'api_access': True,
        'inventory_tracking': True,
        'pos_system': True,
    }
}

def get_user_plan(user):
    """Obtiene el plan activo de la empresa del usuario"""
    if not user.is_authenticated or not user.company:
        return None
    subscription = Subscription.objects.filter(company=user.company, active=True).first()
    if subscription:
        return subscription.plan_name.lower()
    return None

def check_plan_feature(user, feature):
    """Verifica si el usuario tiene acceso a una característica según su plan"""
    plan = get_user_plan(user)
    if not plan or plan not in PLAN_FEATURES:
        return False
    return PLAN_FEATURES[plan].get(feature, False)

def get_plan_limit(user, limit_name):
    """Obtiene el límite de un plan para un usuario"""
    plan = get_user_plan(user)
    if not plan or plan not in PLAN_FEATURES:
        return 0
    return PLAN_FEATURES[plan].get(limit_name, 0)

# ==========================================
#              LÓGICA API (REST)
# ==========================================

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        # super_admin puede hacer todo
        if self.request.user.role == 'super_admin':
            return [permissions.IsAuthenticated()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsGerente()]
        return [permissions.IsAuthenticated()]

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    
    def get_permissions(self):
        # super_admin tiene acceso total
        if self.request.user and self.request.user.role == 'super_admin':
            return [permissions.IsAuthenticated()]
        return [IsAdminCliente, HasAPIAccess]
    
    def create(self, request, *args, **kwargs):
        """Validar límite de sucursales según plan antes de crear"""
        # super_admin no tiene límite
        if request.user.role != 'super_admin':
            max_branches = get_plan_limit(request.user, 'max_branches')
            current_branches = Branch.objects.count()
            
            if current_branches >= max_branches:
                return Response(
                    {'error': f'Tu plan permite máximo {max_branches} sucursales. Ya tienes {current_branches}.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().create(request, *args, **kwargs)

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    
    def get_permissions(self):
        # super_admin tiene acceso total
        if self.request.user and self.request.user.role == 'super_admin':
            return [permissions.IsAuthenticated()]
        return [IsGerente]

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['branch']

    def get_permissions(self):
        # super_admin tiene acceso total
        if self.request.user and self.request.user.role == 'super_admin':
            return [permissions.IsAuthenticated()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsGerente()]
        return [IsVendedor()]

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    http_method_names = ['get', 'post', 'head']

    def get_permissions(self):
        # super_admin tiene acceso total
        if self.request.user and self.request.user.role == 'super_admin':
            return [permissions.IsAuthenticated()]
        return [IsVendedor()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

class SubscriptionViewSet(viewsets.ModelViewSet):
    """API para gestionar suscripciones (solo super_admin puede crear)"""
    queryset = Subscription.objects.all()
    serializer_class = None  # Se define en serializers.py
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo super_admin puede crear/editar/eliminar suscripciones
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        # Evitar importar aquí, se importa en serializers
        from .serializers import SubscriptionSerializer
        return SubscriptionSerializer

class ReportViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        # super_admin tiene acceso total
        if hasattr(self, 'request') and self.request.user and self.request.user.role == 'super_admin':
            return [permissions.IsAuthenticated()]
        return [IsGerente()]
    
    permission_classes = [IsGerente]

    @action(detail=False, methods=['get'])
    def stock(self, request):
        branch_id = request.query_params.get('branch')
        branches = Branch.objects.all()
        if branch_id:
            branches = branches.filter(id=branch_id)

        data = []
        for branch in branches:
            inventory = Inventory.objects.filter(branch=branch).select_related('product')
            items = []
            total_units = 0
            total_value = 0
            for inv in inventory:
                value = inv.stock * inv.product.price
                total_units += inv.stock
                total_value += value
                items.append({
                    "product": inv.product.name,
                    "sku": inv.product.sku,
                    "stock": inv.stock,
                    "value": value
                })
            data.append({
                "branch_id": branch.id,
                "branch": branch.name,
                "total_items": len(items),
                "total_units": total_units,
                "total_value": total_value,
                "inventory": items
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def sales(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        branch_id = request.query_params.get('branch')
        granularity = request.query_params.get('granularity', 'day')  # day | month
        
        today = timezone.now().date()
        
        # Validar que las fechas no sean futuras
        if date_from:
            date_from_parsed = parse_date(date_from)
            if date_from_parsed and date_from_parsed > today:
                return Response(
                    {"error": "La fecha 'desde' no puede ser mayor a hoy."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if date_to:
            date_to_parsed = parse_date(date_to)
            if date_to_parsed and date_to_parsed > today:
                return Response(
                    {"error": "La fecha 'hasta' no puede ser mayor a hoy."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        sales_qs = Sale.objects.all()

        if branch_id:
            sales_qs = sales_qs.filter(branch_id=branch_id)
        if date_from:
            sales_qs = sales_qs.filter(created_at__date__gte=parse_date(date_from))
        if date_to:
            sales_qs = sales_qs.filter(created_at__date__lte=parse_date(date_to))
        # Agrupación por día o mes
        if granularity == 'month':
            date_trunc = TruncMonth('created_at')
            date_format = 'Y-m'
        else:
            date_trunc = TruncDate('created_at')
            date_format = 'Y-m-d'

        grouped = (
            sales_qs
            .annotate(period=date_trunc)
            .values('branch_id', 'branch__name', 'period')
            .annotate(total_amount=Sum('total'), total_transactions=Count('id'))
            .order_by('branch_id', 'period')
        )

        # Estructura por sucursal
        result = {}
        for row in grouped:
            bid = row['branch_id']
            if bid not in result:
                result[bid] = {
                    "branch_id": bid,
                    "branch": row['branch__name'],
                    "periods": [],
                    "total_amount": 0,
                    "total_transactions": 0,
                }
            period_str = row['period'].strftime(date_format)
            result[bid]["periods"].append({
                "period": period_str,
                "total_amount": row['total_amount'] or 0,
                "total_transactions": row['total_transactions'],
            })
            result[bid]["total_amount"] += row['total_amount'] or 0
            result[bid]["total_transactions"] += row['total_transactions']

        return Response({
            "filters": {
                "date_from": date_from,
                "date_to": date_to,
                "branch": branch_id,
                "granularity": granularity,
            },
            "branches": list(result.values()),
        })

    @action(detail=False, methods=['get'])
    def suppliers(self, request):
        """Reporte simple de proveedores (sin pedidos asociados en el modelo actual)."""
        suppliers = Supplier.objects.all()
        data = []
        for supplier in suppliers:
            data.append({
                "id": supplier.id,
                "name": supplier.name,
                "rut": supplier.rut,
                "contact": supplier.contact,
                # No hay relación producto-proveedor ni pedidos en el modelo actual
                "products": [],
                "last_orders": [],
            })
        return Response(data)


# ==========================================
#           CARRITO (API)
# ==========================================

class CartViewSet(viewsets.ViewSet):
    """API para gestionar carrito de compras"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """POST /api/cart/add/ — Agregar producto al carrito (requiere JWT)"""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {"error": "product_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response(
                    {"error": "quantity debe ser >= 1"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "quantity debe ser un número entero"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener o crear CartItem para este usuario
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Si ya existe, aumentar quantity
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response({
            "message": "Producto agregado al carrito",
            "cart_item": serializer.data,
            "created": created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """POST /api/cart/checkout/ — Convertir carrito en Order y vaciar carrito (requiere JWT)"""
        
        # Obtener items del carrito
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return Response(
                {"error": "El carrito está vacío"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            total = 0
            order_items_data = []
            
            # Procesar cada item del carrito
            for cart_item in cart_items:
                product = cart_item.product
                quantity = cart_item.quantity
                price = product.price
                subtotal = price * quantity
                
                order_items_data.append({
                    "product_id": product.id,
                    "quantity": quantity,
                    "price": price,
                    "subtotal": subtotal
                })
                
                total += subtotal
            
            # Crear Order
            order = Order.objects.create(
                user=request.user,
                customer_name=request.user.get_full_name() or request.user.username,
                customer_email=request.user.email,
                status='pending',
                total=total
            )
            
            # Crear OrderItems
            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
            
            # Vaciar carrito del usuario
            cart_items.delete()
            
            order_serializer = OrderSerializer(order)
            return Response({
                "message": "Orden creada exitosamente",
                "order": order_serializer.data,
                "total": total
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Error al procesar la orden: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ==========================================
#           VISTAS WEB (TEMPLATES)
# ==========================================

def home_view(request):
    return render(request, 'core/index.html')

def company_login_view(request):
    """Paso 1: seleccionar la empresa antes del login de usuario."""
    if request.method == 'POST':
        company = request.POST.get('company', '').strip()

        if not company:
            messages.error(request, "Ingresa el nombre de la empresa para continuar.")
            return redirect('company_login')

        # Validamos que exista al menos un usuario asociado a la empresa
        if not User.objects.filter(company__iexact=company).exists():
            messages.error(request, "No existe ninguna cuenta asociada a esa empresa.")
            return redirect('company_login')

        # Guardamos la empresa seleccionada en sesión para usarla en el login de usuario
        request.session['selected_company'] = company
        messages.success(request, f"Empresa '{company}' seleccionada. Ahora inicia sesión con tu usuario.")
        return redirect('login')

    return render(request, 'core/company_login.html')


def login_view(request):
    """Paso 2: login de usuario validando que pertenezca a la empresa elegida."""
    selected_company = request.session.get('selected_company')
    if not selected_company:
        return redirect('company_login')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Validar que el usuario pertenezca a la empresa elegida
            if not user.company or user.company.lower() != selected_company.lower():
                messages.error(request, "El usuario no pertenece a la empresa seleccionada.")
                return redirect('login')

            # Restringir super_admin solo a la empresa temucosoft
            if user.role == 'super_admin' and selected_company.lower() != 'temucosoft':
                messages.error(request, "El rol super_admin solo puede usarse con la empresa 'temucosoft'.")
                return redirect('login')

            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Usuario o contraseña inválidos")
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {
        'form': form,
        'selected_company': selected_company,
    })

def logout_view(request):
    if request.user.is_authenticated:
        # Mensaje antes de cerrar la sesión
        messages.success(request, "Sesión cerrada correctamente.")
        logout(request)

    # Limpiar la empresa seleccionada
    if 'selected_company' in request.session:
        del request.session['selected_company']
    
    # Redirige a la página de login (la cual es un template limpio)
    return redirect('company_login')


@login_required
def product_list_view(request):
    # Permitido para todos los usuarios (interno o e-commerce)
    # super_admin ve todos; otros ven solo productos de su empresa
    if request.user.role == 'super_admin':
        products = Product.objects.select_related('supplier').annotate(total_stock=Sum('inventory__stock'))
    else:
        # Filtrar productos que estén en sucursales de su empresa
        products = Product.objects.filter(
            inventory__branch__name__contains=request.user.company
        ).distinct().select_related('supplier').annotate(total_stock=Sum('inventory__stock'))
    
    return render(request, 'core/product_list.html', {'products': products})


@login_required
def pos_view(request):
    # Restricción de rol
    if request.user.role not in ['vendedor', 'gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "Acceso denegado al POS.")
        return redirect('home')

    # super_admin ve todos; otros ven solo productos de su empresa
    if request.user.role == 'super_admin':
        products_data = Product.objects.all()
    else:
        products_data = Product.objects.filter(
            inventory__branch__name__contains=request.user.company
        ).distinct()
    
    products_list = []
    for p in products_data:
        products_list.append({
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'price': int(p.price),
        })

    # super_admin ve todas las sucursales; otros ven solo su empresa
    if request.user.role == 'super_admin':
        branches = Branch.objects.all()
    else:
        branches = Branch.objects.filter(name__contains=request.user.company)
    
    context = {
        'products_json': json.dumps(products_list, default=str),
        'branches': branches
    }
    return render(request, 'core/pos.html', context)

@login_required
def user_list_view(request):
    """Muestra la lista de usuarios. Restringido a Admin Cliente."""
    # Restricción de rol
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "Acceso denegado. Se requiere rol de Administrador de Cliente.")
        return redirect('home')

    # super_admin ve todos; admin_cliente solo ve su empresa
    if request.user.role == 'super_admin':
        users = User.objects.all().order_by('username')
    else:
        users = User.objects.filter(company=request.user.company).order_by('username')
    
    return render(request, 'core/user_list.html', {'users': users})


# ==========================================
#       VISTAS CRUD - PRODUCTOS
# ==========================================

@login_required
def product_create_view(request):
    """Crear nuevo producto"""
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para crear productos.")
        return redirect('home')
    
    if request.method == 'POST':
        sku = request.POST.get('sku')
        name = request.POST.get('name')
        category = request.POST.get('category', '')
        price = request.POST.get('price')
        cost = request.POST.get('cost', 0)
        description = request.POST.get('description', '')
        supplier_id = request.POST.get('supplier')
        
        if not sku or not name or not price:
            messages.error(request, "SKU, Nombre y Precio son requeridos.")
            return redirect('product_create')
        
        try:
            supplier = None
            if supplier_id:
                supplier = Supplier.objects.get(id=supplier_id)
            
            product = Product.objects.create(
                sku=sku,
                name=name,
                category=category,
                price=float(price),
                cost=float(cost),
                description=description,
                supplier=supplier
            )
            
            # Crear registros de inventario para todas las sucursales con stock 0
            branches = Branch.objects.all()
            for branch in branches:
                Inventory.objects.create(
                    product=product,
                    branch=branch,
                    stock=0
                )
            
            messages.success(request, f"Producto '{name}' creado exitosamente.")
            return redirect('product_list')
        except Exception as e:
            messages.error(request, f"Error al crear producto: {str(e)}")
    
    suppliers = Supplier.objects.all()
    return render(request, 'core/product_form.html', {'mode': 'create', 'suppliers': suppliers})


@login_required
def product_edit_view(request, product_id):
    """Editar producto existente"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para editar productos.")
        return redirect('home')
    
    if request.method == 'POST':
        product.sku = request.POST.get('sku', product.sku)
        product.name = request.POST.get('name', product.name)
        product.category = request.POST.get('category', product.category)
        product.price = float(request.POST.get('price', product.price))
        product.cost = float(request.POST.get('cost', product.cost))
        product.description = request.POST.get('description', product.description)
        
        supplier_id = request.POST.get('supplier')
        if supplier_id:
            product.supplier = Supplier.objects.get(id=supplier_id)
        else:
            product.supplier = None
        
        try:
            product.save()
            messages.success(request, f"Producto '{product.name}' actualizado exitosamente.")
            return redirect('product_list')
        except Exception as e:
            messages.error(request, f"Error al actualizar producto: {str(e)}")
    
    suppliers = Supplier.objects.all()
    return render(request, 'core/product_form.html', {'product': product, 'mode': 'edit', 'suppliers': suppliers})


@login_required
def product_delete_view(request, product_id):
    """Eliminar producto"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para eliminar productos.")
        return redirect('home')
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Producto '{name}' eliminado exitosamente.")
        return redirect('product_list')
    
    return render(request, 'core/product_confirm_delete.html', {'product': product})


# ==========================================
#       VISTAS CRUD - USUARIOS
# ==========================================

@login_required
def user_create_view(request):
    """Crear nuevo usuario"""
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para crear usuarios.")
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        rut = request.POST.get('rut', '')
        role = request.POST.get('role', 'vendedor')
        
        if not username or not password:
            messages.error(request, "Usuario y contraseña son requeridos.")
            return redirect('user_create')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe.")
            return redirect('user_create')
        
        try:
            # admin_cliente solo puede crear usuarios para su empresa
            # super_admin puede especificar la empresa
            if request.user.role == 'super_admin':
                company = request.POST.get('company', '')
            else:
                company = request.user.company
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                rut=rut if rut else None,
                role=role,
                company=company,
                is_active=True
            )
            messages.success(request, f"Usuario '{username}' creado exitosamente.")
            return redirect('user_list')
        except Exception as e:
            messages.error(request, f"Error al crear usuario: {str(e)}")
    
    # Obtener lista de empresas únicas para super_admin
    companies = []
    if request.user.role == 'super_admin':
        companies = User.objects.exclude(company__isnull=True).exclude(company='').values_list('company', flat=True).distinct().order_by('company')
    
    return render(request, 'core/user_form.html', {'mode': 'create', 'companies': companies})


@login_required
def user_edit_view(request, user_id):
    """Editar usuario existente"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para editar usuarios.")
        return redirect('home')
    
    # admin_cliente solo puede editar usuarios de su empresa
    if request.user.role == 'admin_cliente' and user_obj.company != request.user.company:
        messages.error(request, "No puede editar usuarios de otra empresa.")
        return redirect('user_list')
    
    if request.method == 'POST':
        user_obj.email = request.POST.get('email', user_obj.email)
        user_obj.first_name = request.POST.get('first_name', user_obj.first_name)
        user_obj.last_name = request.POST.get('last_name', user_obj.last_name)
        role = request.POST.get('role', user_obj.role)
        
        user_obj.role = role
        rut = request.POST.get('rut', '')
        user_obj.rut = rut if rut else None
        is_active = request.POST.get('is_active') == 'on'
        user_obj.is_active = is_active
        
        password = request.POST.get('password')
        if password:
            user_obj.set_password(password)
        
        try:
            user_obj.save()
            messages.success(request, f"Usuario '{user_obj.username}' actualizado exitosamente.")
            return redirect('user_list')
        except Exception as e:
            messages.error(request, f"Error al actualizar usuario: {str(e)}")
    
    return render(request, 'core/user_form.html', {'user': user_obj, 'mode': 'edit'})


@login_required
def user_delete_view(request, user_id):
    """Eliminar usuario"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para eliminar usuarios.")
        return redirect('home')
    
    if request.user.id == user_obj.id:
        messages.error(request, "No puede eliminarse a sí mismo.")
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f"Usuario '{username}' eliminado exitosamente.")
        return redirect('user_list')
    
    return render(request, 'core/user_confirm_delete.html', {'user': user_obj})


# ==========================================
#       VISTAS CRUD - INVENTARIO
# ==========================================

@login_required
def inventory_view(request):
    """Gestionar inventario por sucursal"""
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin', 'vendedor']:
        messages.error(request, "No tiene permisos para ver inventario.")
        return redirect('home')
    
    branch_id = request.GET.get('branch')
    inventory = Inventory.objects.select_related('product', 'branch').all()
    branches = Branch.objects.all()
    
    # Filtrar por empresa si no es super_admin
    if request.user.role != 'super_admin' and request.user.company:
        branches = branches.filter(name__contains=request.user.company)
        inventory = inventory.filter(branch__in=branches)
    
    if branch_id:
        inventory = inventory.filter(branch_id=branch_id)
    
    return render(request, 'core/inventory_list.html', {
        'inventory': inventory,
        'branches': branches,
        'selected_branch': branch_id
    })


@login_required
def inventory_edit_view(request, inventory_id):
    """Ajustar stock de inventario"""
    inv = get_object_or_404(Inventory, id=inventory_id)
    
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para ajustar inventario.")
        return redirect('home')
    
    if request.method == 'POST':
        new_stock = request.POST.get('stock')
        if new_stock is not None:
            try:
                inv.stock = int(new_stock)
                inv.save()
                messages.success(request, f"Stock actualizado para {inv.product.name}.")
                return redirect('inventory')
            except Exception as e:
                messages.error(request, f"Error al actualizar stock: {str(e)}")
    
    return render(request, 'core/inventory_edit.html', {'inventory': inv})


# ==========================================
#       VISTAS CRUD - SUCURSALES
# ==========================================

@login_required
def branch_list_view(request):
    """Listar sucursales"""
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para ver sucursales.")
        return redirect('home')
    
    # super_admin ve todas; admin_cliente solo su empresa
    if request.user.role == 'super_admin':
        branches = Branch.objects.all()
    else:
        branches = Branch.objects.filter(name__contains=request.user.company)
    
    return render(request, 'core/branch_list.html', {'branches': branches})


@login_required
def branch_create_view(request):
    """Crear nueva sucursal"""
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para crear sucursales.")
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        
        if not name:
            messages.error(request, "El nombre de la sucursal es requerido.")
            return redirect('branch_create')
        
        try:
            Branch.objects.create(
                name=name,
                address=address,
                phone=phone
            )
            messages.success(request, f"Sucursal '{name}' creada exitosamente.")
            return redirect('branch_list')
        except Exception as e:
            messages.error(request, f"Error al crear sucursal: {str(e)}")
    
    return render(request, 'core/branch_form.html', {'mode': 'create'})


@login_required
def branch_edit_view(request, branch_id):
    """Editar sucursal"""
    branch = get_object_or_404(Branch, id=branch_id)
    
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para editar sucursales.")
        return redirect('home')
    
    if request.method == 'POST':
        branch.name = request.POST.get('name', branch.name)
        branch.address = request.POST.get('address', branch.address)
        branch.phone = request.POST.get('phone', branch.phone)
        
        try:
            branch.save()
            messages.success(request, f"Sucursal '{branch.name}' actualizada exitosamente.")
            return redirect('branch_list')
        except Exception as e:
            messages.error(request, f"Error al actualizar sucursal: {str(e)}")
    
    return render(request, 'core/branch_form.html', {'branch': branch, 'mode': 'edit'})


@login_required
def branch_delete_view(request, branch_id):
    """Eliminar sucursal"""
    branch = get_object_or_404(Branch, id=branch_id)
    
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para eliminar sucursales.")
        return redirect('home')
    
    if request.method == 'POST':
        name = branch.name
        branch.delete()
        messages.success(request, f"Sucursal '{name}' eliminada exitosamente.")
        return redirect('branch_list')
    
    return render(request, 'core/branch_confirm_delete.html', {'branch': branch})


# ==========================================
#       VISTAS CRUD - PROVEEDORES
# ==========================================

@login_required
def supplier_list_view(request):
    """Listar proveedores"""
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para ver proveedores.")
        return redirect('home')
    
    suppliers = Supplier.objects.all().prefetch_related('products')
    return render(request, 'core/supplier_list.html', {'suppliers': suppliers})


@login_required
def supplier_create_view(request):
    """Crear nuevo proveedor"""
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para crear proveedores.")
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        rut = request.POST.get('rut')
        contact = request.POST.get('contact', '')
        
        if not name or not rut:
            messages.error(request, "Nombre y RUT son requeridos.")
            return redirect('supplier_create')
        
        try:
            Supplier.objects.create(name=name, rut=rut, contact=contact)
            messages.success(request, f"Proveedor '{name}' creado exitosamente.")
            return redirect('supplier_list')
        except Exception as e:
            messages.error(request, f"Error al crear proveedor: {str(e)}")
    
    return render(request, 'core/supplier_form.html', {'mode': 'create'})


@login_required
def supplier_edit_view(request, supplier_id):
    """Editar proveedor"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para editar proveedores.")
        return redirect('home')
    
    if request.method == 'POST':
        supplier.name = request.POST.get('name', supplier.name)
        supplier.rut = request.POST.get('rut', supplier.rut)
        supplier.contact = request.POST.get('contact', supplier.contact)
        
        try:
            supplier.save()
            messages.success(request, f"Proveedor '{supplier.name}' actualizado exitosamente.")
            return redirect('supplier_list')
        except Exception as e:
            messages.error(request, f"Error al actualizar proveedor: {str(e)}")
    
    return render(request, 'core/supplier_form.html', {'supplier': supplier, 'mode': 'edit'})


@login_required
def supplier_delete_view(request, supplier_id):
    """Eliminar proveedor"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para eliminar proveedores.")
        return redirect('home')
    
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        messages.success(request, f"Proveedor '{name}' eliminado exitosamente.")
        return redirect('supplier_list')
    
    return render(request, 'core/supplier_confirm_delete.html', {'supplier': supplier})


# ==========================================
#       VISTAS - DETALLES Y REPORTES HTML
# ==========================================

@login_required
def product_detail_view(request, product_id):
    """Detalle de producto (redirecciona según rol)"""
    product = get_object_or_404(Product, id=product_id)
    
    # cliente_final ve una vista simplificada (solo para agregar al carrito)
    if request.user.role == 'cliente_final':
        return render(request, 'core/product_detail_cliente.html', {
            'product': product
        })
    
    # Otros roles ven detalles completos (inventario por sucursal, costo, etc.)
    inventory = Inventory.objects.filter(product=product).select_related('branch')
    
    return render(request, 'core/product_detail.html', {
        'product': product,
        'inventory': inventory
    })


@login_required
def sales_list_view(request):
    """Lista de ventas (POS) y compras (e-commerce) con filtros"""
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para ver ventas.")
        return redirect('home')
    
    # Obtener ventas POS
    sales = Sale.objects.select_related('branch', 'user').prefetch_related('items__product').order_by('-created_at')
    
    # Obtener compras e-commerce
    orders = Order.objects.prefetch_related('items__product').order_by('-created_at')
    
    # Filtros opcionales
    branch_id = request.GET.get('branch')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    today = timezone.now().date()
    
    # Validar que las fechas no sean futuras
    if date_from:
        try:
            from datetime import datetime
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            if date_from_parsed > today:
                messages.warning(request, "La fecha 'desde' no puede ser mayor a hoy.")
                date_from = None
            else:
                sales = sales.filter(created_at__date__gte=date_from)
                orders = orders.filter(created_at__date__gte=date_from)
        except ValueError:
            messages.warning(request, "Formato de fecha 'desde' inválido.")
            date_from = None
    
    if date_to:
        try:
            from datetime import datetime
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            if date_to_parsed > today:
                messages.warning(request, "La fecha 'hasta' no puede ser mayor a hoy.")
                date_to = None
            else:
                sales = sales.filter(created_at__date__lte=date_to)
                orders = orders.filter(created_at__date__lte=date_to)
        except ValueError:
            messages.warning(request, "Formato de fecha 'hasta' inválido.")
            date_to = None
    
    if branch_id:
        sales = sales.filter(branch_id=branch_id)
    
    branches = Branch.objects.all()
    
    return render(request, 'core/sales_list.html', {
        'sales': sales,
        'orders': orders,
        'branches': branches,
        'filters': {
            'branch': branch_id,
            'date_from': date_from,
            'date_to': date_to,
        }
    })


@login_required
def reports_view(request):
    """Dashboard de reportes HTML"""
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para ver reportes.")
        return redirect('home')
    
    return render(request, 'core/reports.html')


@login_required
def stock_report_view(request):
    """Reporte de stock visual en HTML"""
    if request.user.role not in ['gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para ver reportes.")
        return redirect('home')
    
    branch_id = request.GET.get('branch')
    branches = Branch.objects.all()
    
    # Filtrar por empresa si no es super_admin
    if request.user.role != 'super_admin' and request.user.company:
        branches = branches.filter(name__contains=request.user.company)
    
    if branch_id:
        selected_branches = branches.filter(id=branch_id)
    else:
        selected_branches = branches
    
    report_data = []
    for branch in selected_branches:
        inventory = Inventory.objects.filter(branch=branch).select_related('product')
        total_units = sum(inv.stock for inv in inventory)
        total_value = sum(inv.stock * inv.product.price for inv in inventory)
        
        report_data.append({
            'branch': branch,
            'inventory': inventory,
            'total_units': total_units,
            'total_value': total_value,
        })
    
    return render(request, 'core/stock_report.html', {
        'report_data': report_data,
        'branches': branches,
        'selected_branch': branch_id,
    })


@login_required
@login_required
def subscription_view(request):
    """Vista de suscripción de la empresa"""
    if request.user.role not in ['admin_cliente', 'super_admin']:
        messages.error(request, "No tiene permisos para ver suscripciones.")
        return redirect('home')
    
    # Obtener suscripción activa de la empresa del usuario
    if not request.user.company:
        messages.error(request, "No tienes una empresa asignada.")
        return redirect('home')
    
    subscription = Subscription.objects.filter(company=request.user.company, active=True).first()
    
    # admin_cliente ve su suscripción pero no puede gestionarla
    # super_admin puede gestionar todas
    can_manage = request.user.role == 'super_admin'
    
    return render(request, 'core/subscription.html', {
        'subscription': subscription,
        'can_manage': can_manage
    })


@login_required
def subscription_create_view(request):
    """Crear nueva suscripción (solo super_admin para empresas)"""
    if request.user.role != 'super_admin':
        messages.error(request, "Solo super_admin puede crear suscripciones.")
        return redirect('home')
    
    if request.method == 'POST':
        company = request.POST.get('company')
        plan_name = request.POST.get('plan_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if not company or not plan_name or not start_date or not end_date:
            messages.error(request, "Todos los campos son requeridos.")
            return redirect('subscription_create')
        
        try:
            # Desactivar suscripción anterior de la empresa si existe
            Subscription.objects.filter(company=company).update(active=False)
            
            # Crear nueva suscripción
            subscription = Subscription.objects.create(
                company=company,
                plan_name=plan_name,
                start_date=start_date,
                end_date=end_date,
                active=True
            )
            subscription.full_clean()  # Validar
            subscription.save()
            
            messages.success(request, f"Suscripción {plan_name} activada para {company}.")
            return redirect('subscription_list')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    # GET: mostrar formulario
    companies = User.objects.filter(company__isnull=False).values_list('company', flat=True).distinct().order_by('company')
    plans = Subscription.PLANS
    
    return render(request, 'core/subscription_form.html', {
        'companies': companies,
        'plans': plans,
        'mode': 'create'
    })


@login_required
def subscription_list_view(request):
    """Listar suscripciones (solo super_admin)"""
    if request.user.role != 'super_admin':
        messages.error(request, "Solo super_admin puede ver el listado de suscripciones.")
        return redirect('home')
    
    subscriptions = Subscription.objects.all().order_by('-end_date')
    
    return render(request, 'core/subscription_list.html', {'subscriptions': subscriptions})


@login_required
def subscription_edit_view(request, subscription_id):
    """Editar suscripción (solo super_admin)"""
    if request.user.role != 'super_admin':
        messages.error(request, "Solo super_admin puede editar suscripciones.")
        return redirect('home')
    
    subscription = get_object_or_404(Subscription, id=subscription_id)
    
    if request.method == 'POST':
        plan_name = request.POST.get('plan_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        active = request.POST.get('active') == 'on'
        
        try:
            subscription.plan_name = plan_name
            subscription.start_date = start_date
            subscription.end_date = end_date
            subscription.active = active
            subscription.full_clean()
            subscription.save()
            
            messages.success(request, "Suscripción actualizada exitosamente.")
            return redirect('subscription_list')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    companies = User.objects.filter(company__isnull=False).values_list('company', flat=True).distinct().order_by('company')
    plans = Subscription.PLANS
    
    return render(request, 'core/subscription_form.html', {
        'subscription': subscription,
        'companies': companies,
        'plans': plans,
        'mode': 'edit'
    })


# ==========================================
#       VISTAS - CARRITO Y CHECKOUT
# ==========================================

def cart_view(request):
    """Vista del carrito de compras (no requiere autenticación)"""
    # El carrito se maneja en sesión o localStorage en frontend
    return render(request, 'core/cart.html')


def checkout_view(request):
    """Vista de checkout para procesar pedido (con o sin autenticación)"""
    if request.method == 'POST':
        # Procesar pedido desde el carrito
        cart_data = json.loads(request.POST.get('cart_data', '[]'))
        
        if not cart_data:
            messages.error(request, "El carrito está vacío.")
            return redirect('cart')
        
        # Obtener datos del formulario
        customer_name = request.POST.get('customer_name', '')
        customer_email = request.POST.get('customer_email', '')
        
        # Si no hay datos en el formulario, usar datos del usuario autenticado
        if request.user.is_authenticated:
            if not customer_name:
                customer_name = request.user.get_full_name() or request.user.username
            if not customer_email:
                customer_email = request.user.email
        
        try:
            # Crear pedido (user puede ser None para anónimos)
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=customer_name,
                customer_email=customer_email,
                status='paid',  # Se marca como pagada al completar checkout
            )
            
            total = 0
            for item in cart_data:
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])
                price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                
                # Descontar stock de todas las sucursales (para compras online)
                # Se descuenta proporcionalmente o de la primera disponible
                inventories = Inventory.objects.filter(product=product).order_by('branch')
                remaining_quantity = quantity
                
                for inventory in inventories:
                    if remaining_quantity <= 0:
                        break
                    
                    if inventory.stock >= remaining_quantity:
                        inventory.stock -= remaining_quantity
                        inventory.save()
                        remaining_quantity = 0
                    else:
                        remaining_quantity -= inventory.stock
                        inventory.stock = 0
                        inventory.save()
                
                if remaining_quantity > 0:
                    order.delete()
                    messages.error(request, f"Stock insuficiente de {product.name}")
                    return redirect('cart')
                
                total += price * quantity
            
            order.total = total
            order.save()
            
            messages.success(request, "Compra realizada correctamente.")
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Error al procesar pedido: {str(e)}")
            return redirect('cart')
    
    return render(request, 'core/checkout.html')


@login_required
def plan_status_view(request):
    """Vista para mostrar el estado del plan de la empresa"""
    if not request.user.company:
        messages.error(request, "No tienes una empresa asignada.")
        return redirect('home')
    
    subscription = Subscription.objects.filter(company=request.user.company, active=True).first()
    
    plan_features = {}
    if subscription:
        plan_key = subscription.plan_name.lower()
        if plan_key in PLAN_FEATURES:
            plan_features = PLAN_FEATURES[plan_key]
    
    return render(request, 'core/plan_status.html', {
        'subscription': subscription,
        'plan_features': plan_features
    })


@login_required
def plan_status_view(request):
    """Ver estado del plan de suscripción"""
    if not request.user.company:
        messages.error(request, "No tienes una empresa asignada.")
        return redirect('home')
    
    subscription = Subscription.objects.filter(company=request.user.company, active=True).first()
    
    # Obtener características del plan
    plan_features = {}
    if subscription:
        plan = subscription.plan_name.lower()
        if plan in PLAN_FEATURES:
            plan_features = PLAN_FEATURES[plan]
    
    return render(request, 'core/plan_status.html', {
        'subscription': subscription,
        'plan_features': plan_features
    })




