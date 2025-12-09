from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
import re

def validar_rut(rut):
    """
    Valida formato y dígito verificador del RUT chileno.
    Acepta formatos: 12.345.678-9, 12345678-9, 123456789
    """
    rut_limpio = rut.replace(".", "").replace("-", "").upper()
    
    if not re.match(r"^\d{7,8}[0-9K]$", rut_limpio):
        raise ValidationError("El formato del RUT no es válido.")

    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]

    # Algoritmo Módulo 11
    suma = 0
    multiplo = 2
    
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
            
    resultado = 11 - (suma % 11)
    
    if resultado == 11:
        dv_calculado = '0'
    elif resultado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(resultado)

    if dv_calculado != dv_ingresado:
        raise ValidationError("El RUT no es válido (Dígito verificador incorrecto).")

class User(AbstractUser):
    ROLES = (
        ('super_admin', 'Super Admin (TemucoSoft)'),
        ('admin_cliente', 'Admin Cliente'),
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
        ('cliente_final', 'Cliente Final'),
    )
    
    # Se agrega el validador aquí
    rut = models.CharField(
        max_length=12, 
        blank=True, 
        null=True, 
        validators=[validar_rut],
        help_text="Formato: 12.345.678-9 o 12345678-9"
    )
    role = models.CharField(max_length=20, choices=ROLES, default='cliente_final')
    company = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
    

class Subscription(models.Model):
    PLANS = (
        ('basic', 'Básico'),
        ('standard', 'Estándar'),
        ('premium', 'Premium'),
    )
    company = models.CharField(max_length=100, help_text="Nombre de la empresa suscrita", default="Sin empresa")
    plan_name = models.CharField(max_length=20, choices=PLANS)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Subscriptions"
    
    def __str__(self):
        return f"{self.company} - Plan {self.get_plan_name_display()} ({self.start_date} a {self.end_date})"

    def clean(self):
        # [cite_start]Validación: end_date > start_date [cite: 196]
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("La fecha de término debe ser posterior a la fecha de inicio.")

class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    # Se asume que una sucursal pertenece a una empresa/cliente (Tenant)
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, validators=[validar_rut])
    contact = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    # Validación: precio >= 0 (guardado en centavos, ej: 1000 = $1000)
    price = models.IntegerField(validators=[MinValueValidator(0)], help_text="Precio en pesos chilenos")
    cost = models.IntegerField(validators=[MinValueValidator(0)], help_text="Costo en pesos chilenos")
    category = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.sku} - {self.name}"

class Inventory(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # [cite_start]Validación: stock >= 0 [cite: 202]
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reorder_point = models.IntegerField(default=10, help_text="Nivel mínimo para alerta de reposición")

    class Meta:
        unique_together = ('branch', 'product') # Evita duplicados del mismo producto en la misma sucursal

    def __str__(self):
        return f"{self.product.name} en {self.branch.name}: {self.stock}"

# --- Modelos Transaccionales (Ventas y E-commerce) ---

class Sale(models.Model):
    """Modelo para ventas presenciales (POS)"""
    PAYMENT_METHODS = (
        ('cash', 'Efectivo'),
        ('debit', 'Débito'),
        ('credit', 'Crédito'),
        ('transfer', 'Transferencia'),
    )
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT, help_text="Vendedor que realiza la venta")
    total = models.IntegerField(default=0, help_text="Total en pesos chilenos")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validación: created_at no puede estar en el futuro
        if self.created_at and self.created_at > timezone.now():
            raise ValidationError("La fecha de creación no puede estar en el futuro.")

    def __str__(self):
        return f"Venta #{self.id} - {self.branch.name}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.IntegerField(help_text="Precio unitario al momento de la venta (en pesos)")
    
    def save(self, *args, **kwargs):
        # Guarda el precio histórico si no viene definido
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)

class Order(models.Model):
    """Modelo para pedidos web (E-commerce)"""
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    )
    
    # Datos del cliente final (puede ser usuario registrado o anónimo)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.IntegerField(default=0, help_text="Total en pesos chilenos")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.IntegerField(help_text="Precio unitario en pesos")

class Purchase(models.Model):
    """Modelo para compras a proveedores"""
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, help_text="Sucursal que recibe la compra")
    date = models.DateField()
    total = models.IntegerField(default=0, help_text="Total en pesos chilenos")
    notes = models.TextField(blank=True, help_text="Notas adicionales sobre la compra")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validación: Purchase.date no puede ser mayor a hoy
        if self.date and self.date > timezone.now().date():
            raise ValidationError("La fecha de compra no puede ser mayor a hoy.")

    def __str__(self):
        return f"Compra #{self.id} - {self.supplier.name} ({self.date})"

class PurchaseItem(models.Model):
    """Items de la compra a proveedor"""
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    cost = models.IntegerField(help_text="Costo unitario al momento de la compra (en pesos)")

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

class CartItem(models.Model):
    """Items del carrito de compra (persistente en BD)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x{self.quantity}"