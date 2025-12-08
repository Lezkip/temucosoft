from rest_framework import serializers
from .models import User, Product, Branch, Supplier, Inventory, Sale, SaleItem, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rut', 'role', 'company', 'is_active']
        read_only_fields = ['role', 'company'] # Por seguridad, solo admin debería cambiar esto

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'branch', 'branch_name', 'product', 'product_name', 'stock', 'reorder_point']

# --- Serializadores para Ventas (Anidados) ---

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['product', 'product_name', 'quantity', 'price']
        read_only_fields = ['price'] # El precio se toma del producto al guardar

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True) # Permite enviar una lista de items en la misma venta

    class Meta:
        model = Sale
        fields = ['id', 'branch', 'user', 'total', 'payment_method', 'created_at', 'items']
        read_only_fields = ['total', 'user', 'created_at'] # El total se calcula solo

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # Asigna el usuario actual automáticamente
        validated_data['user'] = self.context['request'].user
        
        sale = Sale.objects.create(**validated_data)
        
        total_venta = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price # Precio actual del producto
            
            SaleItem.objects.create(sale=sale, price=price, **item_data)
            
            # Descontar stock
            inventory = Inventory.objects.get(branch=sale.branch, product=product)
            inventory.stock -= quantity
            inventory.save()
            
            total_venta += price * quantity
            
        sale.total = total_venta
        sale.save()
        return sale
    

# --- Serializadores para Pedidos (E-commerce) ---

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'quantity', 'price']
        read_only_fields = ['price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'customer_name', 'customer_email', 'status', 'total', 'created_at', 'items']
        read_only_fields = ['total', 'created_at', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Si el usuario está autenticado, lo asignamos. Si no, queda null (compra anónima)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
            
        order = Order.objects.create(**validated_data)
        
        total_order = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price # Precio actual
            
            OrderItem.objects.create(order=order, price=price, **item_data)
            
            # Nota: En e-commerce el stock suele descontarse al confirmar pago o envío,
            # pero para este ejercicio lo descontaremos al crear el pedido:
            inventory = Inventory.objects.filter(product=product).first()
            if inventory:
                inventory.stock -= quantity
                inventory.save()
            
            total_order += price * quantity
            
        order.total = total_order
        order.save()
        return order