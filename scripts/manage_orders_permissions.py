#!/usr/bin/env python
"""
Script para crear y asignar permisos de órdenes/pedidos
Uso: python manage.py shell < scripts/manage_orders_permissions.py
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User, Permission, Role

def create_orders_permissions():
    """Crear permisos de órdenes con códigos que coincidan con Flutter"""
    print("\n📋 Creando permisos de órdenes...")
    
    permisos_ordenes = [
        ('ordenes.listar', 'Listar Órdenes', 'Puede ver el listado de todas las órdenes'),
        ('ordenes.ver', 'Ver Detalle de Orden', 'Puede ver los detalles de una orden específica'),
        ('ordenes.editar', 'Editar Estado de Órdenes', 'Puede cambiar estado, reembolsar o cancelar órdenes'),
        ('ordenes.crear', 'Crear Órdenes', 'Puede crear nuevas órdenes'),
        ('ordenes.eliminar', 'Eliminar Órdenes', 'Puede eliminar órdenes'),
        ('admin.acceso', 'Acceso al Panel Admin', 'Acceso al panel de administración general'),
    ]
    
    permisos_creados = []
    for codigo, nombre, descripcion in permisos_ordenes:
        permiso, created = Permission.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'modulo': 'ordenes',
                'descripcion': descripcion
            }
        )
        if created:
            permisos_creados.append(permiso)
            print(f"  ✅ Creado: {codigo}")
        else:
            print(f"  ℹ️  Ya existe: {codigo}")
    
    return Permission.objects.filter(codigo__startswith='ordenes')


def assign_permissions_to_admin_role():
    """Asignar permisos de órdenes al rol Admin"""
    print("\n👤 Asignando permisos al rol Admin...")
    
    try:
        admin_role = Role.objects.get(nombre='Admin')
        
        # Permisos a asignar
        permisos_para_asignar = Permission.objects.filter(
            codigo__in=[
                'ordenes.listar',
                'ordenes.ver',
                'ordenes.editar',
                'ordenes.crear',
                'ordenes.eliminar',
                'admin.acceso'
            ]
        )
        
        # Agregar permisos
        count_before = admin_role.permisos.count()
        admin_role.permisos.add(*permisos_para_asignar)
        count_after = admin_role.permisos.count()
        
        print(f"  ✅ Permisos asignados al rol Admin")
        print(f"     Antes: {count_before} permisos")
        print(f"     Después: {count_after} permisos")
        
    except Role.DoesNotExist:
        print("  ❌ El rol 'Admin' no existe")


def assign_permissions_to_admin_user():
    """Verificar que el usuario Admin tiene rol Admin con permisos"""
    print("\n👤 Verificando usuario Admin...")
    
    admin_users = User.objects.filter(
        nombre='Juan',
        apellido='Administrator',
        email='admin@smartsales365.com'
    )
    
    if not admin_users.exists():
        print("  ℹ️  Buscando usuarios Admin alternativos...")
        admin_users = User.objects.filter(rol__nombre='Admin')
    
    if not admin_users.exists():
        print("  ❌ No se encontró usuario Admin")
        return
    
    admin_user = admin_users.first()
    print(f"  ✅ Usuario encontrado: {admin_user.nombre} {admin_user.apellido} ({admin_user.email})")
    print(f"  ✅ Rol: {admin_user.rol.nombre}")
    
    # Obtener permisos del rol
    permisos_rol = admin_user.rol.permisos.all()
    permisos_codigos = [p.codigo for p in permisos_rol]
    
    print(f"\n  📋 Permisos del usuario (vía rol):")
    ordenes_perms = [p for p in permisos_codigos if 'ordenes' in p or 'admin' in p]
    for perm in sorted(ordenes_perms):
        print(f"     ✅ {perm}")



def verify_permissions():
    """Verificar que todos los permisos existen"""
    print("\n✅ Verificando permisos...")
    
    codigos_esperados = [
        'ordenes.listar',
        'ordenes.ver',
        'ordenes.editar',
        'ordenes.crear',
        'ordenes.eliminar',
        'admin.acceso'
    ]
    
    for codigo in codigos_esperados:
        try:
            perm = Permission.objects.get(codigo=codigo)
            print(f"  ✅ {codigo}: {perm.nombre}")
        except Permission.DoesNotExist:
            print(f"  ❌ {codigo}: NO EXISTE")


if __name__ == '__main__':
    print("=" * 60)
    print("🔐 Gestión de Permisos de Órdenes")
    print("=" * 60)
    
    # Crear permisos
    create_orders_permissions()
    
    # Asignar a rol Admin
    assign_permissions_to_admin_role()
    
    # Asignar a usuario Admin
    assign_permissions_to_admin_user()
    
    # Verificar
    verify_permissions()
    
    print("\n" + "=" * 60)
    print("✅ Script completado")
    print("=" * 60)
