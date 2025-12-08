from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# Importación obligatoria de las vistas web
from core.views import home_view, login_view, logout_view, product_list_view, pos_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('core.urls')),
    
    # Rutas Web (Frontend - HTML)
    path('', home_view, name='home'),      # Esta es la ruta raíz que faltaba
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('products/', product_list_view, name='product_list'),
    path('pos/', pos_view, name='pos'),
]