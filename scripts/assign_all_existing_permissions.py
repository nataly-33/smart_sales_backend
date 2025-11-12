#!/usr/bin/env python
"""
Script para asignar TODOS los permisos existentes en la BD al rol Administrador
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User, Permission, Role

def list_all_permissions():
    """Listar todos los permisos en la base de datos"""
    print("\n📋 Listando TODOS los permisos en la base de datos...")
    
    all_permissions = Permission.objects.all().order_by('modulo', 'codigo')
    
    if not all_permissions.exists():
        print("  ❌ No hay permisos en la base de datos")
        return []
    
    print(f"  ✅ Total de permisos encontrados: {all_permissions.count()}")
    print("\n  Permisos por módulo:")
    
    modulos = Permission.objects.values_list('modulo', flat=True).distinct().order_by('modulo')
    for modulo in modulos:
        permisos_modulo = all_permissions.filter(modulo=modulo)
        print(f"\n  📦 {modulo.upper()} ({permisos_modulo.count()} permisos):")
        for perm in permisos_modulo:
            print(f"     • {perm.codigo} - {perm.nombre}")
    
    return all_permissions


def assign_all_to_admin():
    """Asignar absolutamente TODOS los permisos al rol Administrador"""
    print("\n👤 Asignando TODOS los permisos al rol Administrador...")
    
    try:
        # Buscar el rol Administrador
        admin_role = Role.objects.filter(nombre__icontains='admin').first()
        
        if not admin_role:
            print("  ❌ No se encontró el rol Administrador")
            print("  Buscando roles disponibles...")
            roles = Role.objects.all()
            for role in roles:
                print(f"     • {role.nombre}")
            return
        
        print(f"  ✅ Rol encontrado: {admin_role.nombre} (ID: {admin_role.id})")
        
        # Obtener TODOS los permisos existentes
        all_permisos = Permission.objects.all()
        count_before = admin_role.permisos.count()
        
        # Asignar TODOS los permisos
        admin_role.permisos.set(all_permisos)
        admin_role.save()
        
        count_after = admin_role.permisos.count()
        
        print(f"\n  ✅ TODOS los permisos han sido asignados")
        print(f"     Antes: {count_before} permisos")
        print(f"     Después: {count_after} permisos")
        print(f"     Total en BD: {all_permisos.count()} permisos")
        
        if count_after == all_permisos.count():
            print(f"\n  ✅ ¡Perfecto! El Administrador tiene el 100% de los permisos")
        else:
            print(f"\n  ⚠️  Advertencia: Faltan {all_permisos.count() - count_after} permisos")
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


def verify_admin_user():
    """Verificar el usuario admin"""
    print("\n👤 Verificando usuario admin@smartsales365.com...")
    
    admin_user = User.objects.filter(email='admin@smartsales365.com').first()
    
    if not admin_user:
        print("  ❌ No se encontró el usuario")
        return
    
    print(f"  ✅ Usuario: {admin_user.nombre_completo}")
    print(f"  ✅ Email: {admin_user.email}")
    print(f"  ✅ Rol: {admin_user.rol.nombre}")
    print(f"  ✅ Permisos del rol: {admin_user.rol.permisos.count()}")
    
    # Mostrar algunos permisos
    permisos = admin_user.rol.permisos.all()[:10]
    print(f"\n  Primeros 10 permisos:")
    for perm in permisos:
        print(f"     ✅ {perm.codigo}")


if __name__ == '__main__':
    print("=" * 70)
    print("🔐 ASIGNAR TODOS LOS PERMISOS EXISTENTES AL ADMINISTRADOR")
    print("=" * 70)
    
    # Listar todos los permisos
    list_all_permissions()
    
    # Asignar TODOS al rol Administrador
    assign_all_to_admin()
    
    # Verificar usuario
    verify_admin_user()
    
    print("\n" + "=" * 70)
    print("✅ COMPLETADO - Cierra sesión en la app y vuelve a iniciar sesión")
    print("=" * 70)
