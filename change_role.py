#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User

# Cambiar el rol de admin a super_admin
user = User.objects.get(username='admin')
print(f'Rol actual: {user.role}')
user.role = 'super_admin'
user.save()
print(f'Rol actualizado a: {user.role}')
