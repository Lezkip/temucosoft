import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User

print("\n" + "="*90)
print("LISTADO COMPLETO DE USUARIOS POR EMPRESA")
print("="*90)

companies = {}
for user in User.objects.all().order_by('company', 'role'):
    if user.company not in companies:
        companies[user.company] = []
    companies[user.company].append({
        'username': user.username,
        'role': user.role,
        'name': f"{user.first_name} {user.last_name}",
        'email': user.email
    })

for company in sorted(companies.keys()):
    print(f"\n🏢 {company.upper()}")
    print("-"*90)
    for user in companies[company]:
        print(f"  👤 {user['role']:20} | username: {user['username']:25} | pw: 1234")
        print(f"     Nombre: {user['name']:30} | Email: {user['email']}")
        print()

print("="*90)
print("\nRECUERDA: Todas las contraseñas son: 1234")
print("="*90)
