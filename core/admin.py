from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription, Branch, Supplier, Product, Inventory, Sale, SaleItem, Order, OrderItem, Purchase, PurchaseItem, CartItem

# --- Usuario ---
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rut', 'role', 'company')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('rut', 'role', 'company')}),
    )

# --- Producto (NUEVO: Esto soluciona el error) ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'price', 'category')
    search_fields = ['name', 'sku'] # Obligatorio para que funcione el autocomplete en Ventas

# --- Ventas (POS) ---
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    autocomplete_fields = ['product'] # Requiere que ProductAdmin tenga search_fields

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'user', 'total', 'created_at')
    list_filter = ('branch', 'created_at')
    inlines = [SaleItemInline]
    readonly_fields = ('created_at',)

# --- Pedidos (E-commerce) ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)

# --- Compras a Proveedores ---
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    autocomplete_fields = ['product']

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'branch', 'date', 'total', 'created_at')
    list_filter = ('branch', 'date', 'supplier')
    inlines = [PurchaseItemInline]
    readonly_fields = ('created_at',)

# --- Carrito de Compra ---
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ['user__username', 'product__name']

# --- Registros Simples (Ya no incluye Product porque se registró arriba) ---
admin.site.register(Subscription)
admin.site.register(Branch)
admin.site.register(Supplier)
admin.site.register(Inventory)