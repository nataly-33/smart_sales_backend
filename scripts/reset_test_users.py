#!/usr/bin/env python
"""
Script para resetear contraseñas de usuarios de prueba
"""
import os
import sys
import django
from pathlib import Path

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

django.setup()

from apps.accounts.models import User

def main():
    print("=" * 80)
    print("🔑 RESETEAR CONTRASEÑAS DE USUARIOS DE PRUEBA".center(80))
    print("=" * 80)
    print()

    # Contraseña por defecto
    password = "Admin2024!"

    # Lista de usuarios a resetear
    test_users = [
        {'email': 'admin@smartsales365.com', 'rol': 'Administrador'},
        {'email': 'cliente2@laboratorios.com', 'rol': 'Cliente'},
        {'email': 'cliente@example.com', 'rol': 'Cliente'},
    ]

    for user_data in test_users:
        email = user_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            # Resetear contraseña
            user.set_password(password)
            user.is_active = True
            user.save()

            print(f"✅ Usuario: {email}")
            print(f"   Rol: {user.rol}")
            print(f"   Activo: {user.is_active}")
            print(f"   Contraseña reseteada a: {password}")
            print()
        else:
            print(f"❌ Usuario no encontrado: {email}")
            print()

    print("=" * 80)
    print("✅ CONTRASEÑAS RESETEADAS".center(80))
    print("=" * 80)
    print()
    print("📋 Credenciales para login:")
    print()
    print("   🔹 ADMINISTRADOR:")
    print(f"      Email: admin@smartsales365.com")
    print(f"      Password: {password}")
    print()
    print("   🔹 CLIENTE:")
    print(f"      Email: cliente2@laboratorios.com")
    print(f"      Password: {password}")
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
