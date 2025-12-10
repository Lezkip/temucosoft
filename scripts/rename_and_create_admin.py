import os
import sys
import django
from django.contrib.auth.hashers import make_password

# Ensure project root on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User

# Renombrar 'admin' a 'super_admin' si existe
try:
    u = User.objects.get(username='admin')
    u.username = 'super_admin'
    u.save()
    print("Renombrado 'admin' -> 'super_admin'")
except User.DoesNotExist:
    print("Usuario 'admin' no encontrado para renombrar")

# Crear admin superuser de pruebas
if User.objects.filter(username='admin').exists():
    print("Ya existe usuario 'admin', no se creó uno nuevo")
else:
    User.objects.create(
        username='admin',
        email='admin@temucosoft.local',
        password=make_password('1234'),
        first_name='Admin',
        last_name='Sistema',
        role='admin_cliente',
        company='temucosoft',
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    print("Creado usuario 'admin' (superuser) pass=1234")
