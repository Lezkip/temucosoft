from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
import json

# Imports para Vistas Web (HTML)
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .models import Product, Branch, Supplier, Inventory, Sale, Order
from .serializers import (
    ProductSerializer, BranchSerializer, SupplierSerializer,
    InventorySerializer, SaleSerializer, OrderSerializer
)
from .permissions import IsAdminCliente, IsGerente, IsVendedor

# ==========================================
#              LÓGICA API (REST)
# ==========================================

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsGerente()]
        return [permissions.IsAuthenticated()]

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminCliente]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsGerente]

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['branch']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsGerente()]
        return [IsVendedor()]

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsVendedor]
    http_method_names = ['get', 'post', 'head']

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

class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsGerente]

    @action(detail=False, methods=['get'])
    def stock(self, request):
        data = []
        branches = Branch.objects.all()
        for branch in branches:
            inventory = Inventory.objects.filter(branch=branch).select_related('product')
            items = []
            for inv in inventory:
                items.append({
                    "product": inv.product.name,
                    "sku": inv.product.sku,
                    "stock": inv.stock,
                    "value": inv.stock * inv.product.price
                })
            data.append({
                "branch": branch.name,
                "total_items": len(items),
                "inventory": items
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def sales(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        branch_id = request.query_params.get('branch')
        
        sales_qs = Sale.objects.all()

        if branch_id:
            sales_qs = sales_qs.filter(branch_id=branch_id)
        if date_from:
            sales_qs = sales_qs.filter(created_at__date__gte=parse_date(date_from))
        if date_to:
            sales_qs = sales_qs.filter(created_at__date__lte=parse_date(date_to))

        total_money = sales_qs.aggregate(Sum('total'))['total__sum'] or 0
        total_count = sales_qs.count()
        serializer = SaleSerializer(sales_qs, many=True)

        return Response({
            "period": f"{date_from} to {date_to}",
            "branch_filter": branch_id,
            "total_sales_amount": total_money,
            "total_transactions": total_count,
            "sales_detail": serializer.data
        })

# ==========================================
#           VISTAS WEB (TEMPLATES)
# ==========================================

def home_view(request):
    return render(request, 'core/index.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Usuario o contraseña inválidos")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def product_list_view(request):
    # Solo permitido para Gerentes, Admin Cliente o Vendedores
    if request.user.role not in ['gerente', 'admin_cliente', 'vendedor', 'super_admin']:
        messages.error(request, "No tiene permisos para ver el inventario.")
        return redirect('home')

    # Obtenemos productos y anotamos el stock total (suma de inventarios)
    products = Product.objects.annotate(total_stock=Sum('inventory__stock'))
    
    return render(request, 'core/product_list.html', {'products': products})



@login_required
def pos_view(request):
    # Restricción de rol
    if request.user.role not in ['vendedor', 'gerente', 'admin_cliente', 'super_admin']:
        messages.error(request, "Acceso denegado al POS.")
        return redirect('home')

    # Serializamos productos para usarlos en JS
    products = Product.objects.all().values('id', 'sku', 'name', 'price')
    branches = Branch.objects.all()
    
    context = {
        'products_json': json.dumps(list(products), default=str),
        'branches': branches
    }
    return render(request, 'core/pos.html', context)

