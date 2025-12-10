"""
Script para migrar de SQLite a PostgreSQL
Pasos:
1. Instalar PostgreSQL
2. Crear base de datos y usuario en PostgreSQL
3. Actualizar settings.py con la configuración de PostgreSQL
4. Ejecutar este script
"""

import os
import sys
import django
from django.core.management import call_command

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("=" * 70)
print("MIGRACIÓN DE SQLite A PostgreSQL")
print("=" * 70)

print("\n1. Exportando datos de SQLite...")
try:
    # Exportar todos los datos a un archivo JSON
    call_command('dumpdata', 'core', 'auth', 'contenttypes', 'sessions', 
                 output='sqlite_backup.json', indent=2)
    print("   ✓ Datos exportados a sqlite_backup.json")
except Exception as e:
    print(f"   ✗ Error al exportar: {e}")
    sys.exit(1)

print("\n2. Para completar la migración:")
print("   a) Instala PostgreSQL si no lo tienes:")
print("      - Windows: Descarga desde https://www.postgresql.org/download/windows/")
print("      - Linux: sudo apt-get install postgresql postgresql-contrib")
print("")
print("   b) Crea la base de datos y usuario en PostgreSQL:")
print("      ```sql")
print("      CREATE USER temucosoft_user WITH PASSWORD 'tu_contraseña_segura';")
print("      CREATE DATABASE temucosoft_db OWNER temucosoft_user;")
print("      GRANT ALL PRIVILEGES ON DATABASE temucosoft_db TO temucosoft_user;")
print("      ```")
print("")
print("   c) Instala el driver de PostgreSQL:")
print("      pip install psycopg2-binary")
print("")
print("   d) Actualiza tu config/settings.py:")
print("      ```python")
print("      DATABASES = {")
print("          'default': {")
print("              'ENGINE': 'django.db.backends.postgresql',")
print("              'NAME': 'temucosoft_db',")
print("              'USER': 'temucosoft_user',")
print("              'PASSWORD': 'tu_contraseña_segura',")
print("              'HOST': 'localhost',")
print("              'PORT': '5432',")
print("          }")
print("      }")
print("      ```")
print("")
print("   e) Ejecuta las migraciones en PostgreSQL:")
print("      python manage.py migrate")
print("")
print("   f) Importa los datos:")
print("      python manage.py loaddata sqlite_backup.json")
print("")
print("   g) Verifica que todo esté correcto:")
print("      python manage.py createsuperuser (si es necesario)")
print("      python manage.py runserver")
print("")
print("=" * 70)
print("✓ Respaldo completado: sqlite_backup.json")
print("=" * 70)
