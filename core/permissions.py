from rest_framework import permissions
from .models import Subscription

class IsAdminCliente(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # super_admin tiene acceso a todo
        if request.user.role == 'super_admin':
            return True
        return request.user.role in ['admin_cliente']

class IsGerente(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # super_admin tiene acceso a todo
        if request.user.role == 'super_admin':
            return True
        # Gerente o superior (excepto super_admin que ya pasó)
        return request.user.role in ['admin_cliente', 'gerente']

class IsVendedor(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # super_admin tiene acceso a todo
        if request.user.role == 'super_admin':
            return True
        # Vendedor o superior (excepto super_admin que ya pasó)
        return request.user.role in ['admin_cliente', 'gerente', 'vendedor']

class HasAPIAccess(permissions.BasePermission):
    """Verifica que el usuario tenga acceso a API según su plan"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Super admin siempre tiene acceso total
        if request.user.role == 'super_admin':
            return True
        
        # Verificar suscripción activa con plan que incluya API
        if not request.user.company:
            return False
        
        subscription = Subscription.objects.filter(company=request.user.company, active=True).first()
        if not subscription:
            return False
        
        plan = subscription.plan_name.lower()
        # Solo 'premium' tiene acceso a API (excepto super_admin que ya pasó)
        return plan == 'premium'
