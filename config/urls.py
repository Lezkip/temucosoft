from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# Importación obligatoria de las vistas web
from core.views import (
    home_view, company_login_view, login_view, logout_view, product_list_view, pos_view, user_list_view,
    product_create_view, product_edit_view, product_delete_view, product_detail_view,
    user_create_view, user_edit_view, user_delete_view,
    inventory_view, inventory_edit_view,
    branch_list_view, branch_create_view, branch_edit_view, branch_delete_view,
    supplier_list_view, supplier_create_view, supplier_edit_view, supplier_delete_view,
    sales_list_view, reports_view, stock_report_view, subscription_view,
    subscription_create_view, subscription_list_view, subscription_edit_view,
    cart_view, checkout_view, plan_status_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('core.urls')),
    
    # Rutas Web (Frontend - HTML)
    path('', home_view, name='home'),
    path('empresa/', company_login_view, name='company_login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Rutas de Productos
    path('products/', product_list_view, name='product_list'),
    path('products/create/', product_create_view, name='product_create'),
    path('products/<int:product_id>/', product_detail_view, name='product_detail'),
    path('products/<int:product_id>/edit/', product_edit_view, name='product_edit'),
    path('products/<int:product_id>/delete/', product_delete_view, name='product_delete'),
    
    # Rutas de Usuarios
    path('users/', user_list_view, name='user_list'),
    path('users/create/', user_create_view, name='user_create'),
    path('users/<int:user_id>/edit/', user_edit_view, name='user_edit'),
    path('users/<int:user_id>/delete/', user_delete_view, name='user_delete'),
    
    # Rutas de Inventario
    path('inventory/', inventory_view, name='inventory'),
    path('inventory/<int:inventory_id>/edit/', inventory_edit_view, name='inventory_edit'),
    
    # Rutas de Sucursales
    path('branches/', branch_list_view, name='branch_list'),
    path('branches/create/', branch_create_view, name='branch_create'),
    path('branches/<int:branch_id>/edit/', branch_edit_view, name='branch_edit'),
    path('branches/<int:branch_id>/delete/', branch_delete_view, name='branch_delete'),
    
    # Rutas de Proveedores
    path('suppliers/', supplier_list_view, name='supplier_list'),
    path('suppliers/create/', supplier_create_view, name='supplier_create'),
    path('suppliers/<int:supplier_id>/edit/', supplier_edit_view, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', supplier_delete_view, name='supplier_delete'),
    
    # Rutas de Ventas y Reportes
    path('sales/', sales_list_view, name='sales_list'),
    path('reports/', reports_view, name='reports'),
    path('reports/stock/', stock_report_view, name='stock_report'),
    
    # Suscripción
    path('subscription/', subscription_view, name='subscription'),
    path('subscription/status/', plan_status_view, name='plan_status'),
    path('subscriptions/', subscription_list_view, name='subscription_list'),
    path('subscriptions/create/', subscription_create_view, name='subscription_create'),
    path('subscriptions/<int:subscription_id>/edit/', subscription_edit_view, name='subscription_edit'),
    
    # Carrito y Checkout
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    
    # POS
    path('pos/', pos_view, name='pos'),
]
