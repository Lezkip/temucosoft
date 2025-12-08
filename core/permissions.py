from rest_framework import permissions

class IsAdminCliente(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'admin_cliente']

class IsGerente(permissions.BasePermission):
    def has_permission(self, request, view):
        # Gerente o superior
        return request.user.is_authenticated and request.user.role in ['super_admin', 'admin_cliente', 'gerente']

class IsVendedor(permissions.BasePermission):
    def has_permission(self, request, view):
        # Vendedor o superior
        return request.user.is_authenticated and request.user.role in ['super_admin', 'admin_cliente', 'gerente', 'vendedor']