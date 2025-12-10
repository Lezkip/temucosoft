from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, BranchViewSet, SupplierViewSet, 
    InventoryViewSet, SaleViewSet, OrderViewSet, ReportViewSet,
    SubscriptionViewSet, CartViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]

