#!/usr/bin/env python
"""
Script para asignar TODOS los permisos al rol Administrador
Uso: python manage.py shell < scripts/assign_all_permissions_to_admin.py
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User, Permission, Role

def create_all_permissions():
    """Crear todos los permisos necesarios del sistema"""
    print("\n📋 Creando permisos del sistema...")
    
    all_permissions = [
        # Usuarios
        ('usuarios.listar', 'Listar Usuarios', 'usuarios', 'Puede ver el listado de todos los usuarios'),
        ('usuarios.ver', 'Ver Detalle de Usuario', 'usuarios', 'Puede ver los detalles de un usuario específico'),
        ('usuarios.crear', 'Crear Usuarios', 'usuarios', 'Puede crear nuevos usuarios'),
        ('usuarios.editar', 'Editar Usuarios', 'usuarios', 'Puede editar usuarios existentes'),
        ('usuarios.eliminar', 'Eliminar Usuarios', 'usuarios', 'Puede eliminar usuarios'),
        
        # Roles
        ('roles.listar', 'Listar Roles', 'roles', 'Puede ver el listado de todos los roles'),
        ('roles.ver', 'Ver Detalle de Rol', 'roles', 'Puede ver los detalles de un rol específico'),
        ('roles.crear', 'Crear Roles', 'roles', 'Puede crear nuevos roles'),
        ('roles.editar', 'Editar Roles', 'roles', 'Puede editar roles existentes'),
        ('roles.eliminar', 'Eliminar Roles', 'roles', 'Puede eliminar roles'),
        
        # Permisos
        ('permisos.listar', 'Listar Permisos', 'permisos', 'Puede ver el listado de todos los permisos'),
        ('permisos.ver', 'Ver Detalle de Permiso', 'permisos', 'Puede ver los detalles de un permiso específico'),
        
        # Productos
        ('productos.listar', 'Listar Productos', 'productos', 'Puede ver el listado de todos los productos'),
        ('productos.ver', 'Ver Detalle de Producto', 'productos', 'Puede ver los detalles de un producto específico'),
        ('productos.crear', 'Crear Productos', 'productos', 'Puede crear nuevos productos'),
        ('productos.editar', 'Editar Productos', 'productos', 'Puede editar productos existentes'),
        ('productos.eliminar', 'Eliminar Productos', 'productos', 'Puede eliminar productos'),
        
        # Categorías
        ('categorias.listar', 'Listar Categorías', 'categorias', 'Puede ver el listado de todas las categorías'),
        ('categorias.ver', 'Ver Detalle de Categoría', 'categorias', 'Puede ver los detalles de una categoría específica'),
        ('categorias.crear', 'Crear Categorías', 'categorias', 'Puede crear nuevas categorías'),
        ('categorias.editar', 'Editar Categorías', 'categorias', 'Puede editar categorías existentes'),
        ('categorias.eliminar', 'Eliminar Categorías', 'categorias', 'Puede eliminar categorías'),
        
        # Clientes
        ('clientes.listar', 'Listar Clientes', 'clientes', 'Puede ver el listado de todos los clientes'),
        ('clientes.ver', 'Ver Detalle de Cliente', 'clientes', 'Puede ver los detalles de un cliente específico'),
        ('clientes.crear', 'Crear Clientes', 'clientes', 'Puede crear nuevos clientes'),
        ('clientes.editar', 'Editar Clientes', 'clientes', 'Puede editar clientes existentes'),
        ('clientes.eliminar', 'Eliminar Clientes', 'clientes', 'Puede eliminar clientes'),
        
        # Órdenes
        ('ordenes.listar', 'Listar Órdenes', 'ordenes', 'Puede ver el listado de todas las órdenes'),
        ('ordenes.ver', 'Ver Detalle de Orden', 'ordenes', 'Puede ver los detalles de una orden específica'),
        ('ordenes.crear', 'Crear Órdenes', 'ordenes', 'Puede crear nuevas órdenes'),
        ('ordenes.editar', 'Editar Estado de Órdenes', 'ordenes', 'Puede cambiar estado, reembolsar o cancelar órdenes'),
        ('ordenes.eliminar', 'Eliminar Órdenes', 'ordenes', 'Puede eliminar órdenes'),
        
        # Reportes
        ('reportes.generar', 'Generar Reportes', 'reportes', 'Puede generar reportes del sistema'),
        ('reportes.ver', 'Ver Reportes', 'reportes', 'Puede ver reportes generados'),
        
        # Admin
        ('admin.acceso', 'Acceso al Panel Admin', 'admin', 'Acceso al panel de administración general'),
    ]
    
    created_count = 0
    existing_count = 0
    
    for codigo, nombre, modulo, descripcion in all_permissions:
        permiso, created = Permission.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'modulo': modulo,
                'descripcion': descripcion
            }
        )
        if created:
            created_count += 1
            print(f"  ✅ Creado: {codigo}")
        else:
            existing_count += 1
            print(f"  ℹ️  Ya existe: {codigo}")
    
    print(f"\n  📊 Total creados: {created_count}")
    print(f"  📊 Total existentes: {existing_count}")
    
    return Permission.objects.all()


def assign_all_permissions_to_admin():
    """Asignar TODOS los permisos al rol Administrador"""
    print("\n👤 Asignando todos los permisos al rol Administrador...")
    
    try:
        # Buscar el rol Administrador
        admin_role = Role.objects.filter(nombre__icontains='admin').first()
        
        if not admin_role:
            print("  ❌ No se encontró el rol Administrador")
            return
        
        print(f"  ✅ Rol encontrado: {admin_role.nombre}")
        
        # Obtener TODOS los permisos
        all_permisos = Permission.objects.all()
        count_before = admin_role.permisos.count()
        
        # Asignar todos los permisos
        admin_role.permisos.set(all_permisos)
        count_after = admin_role.permisos.count()
        
        print(f"  ✅ Permisos asignados al rol {admin_role.nombre}")
        print(f"     Antes: {count_before} permisos")
        print(f"     Después: {count_after} permisos")
        
        # Mostrar permisos por módulo
        print(f"\n  📋 Permisos por módulo:")
        modulos = Permission.objects.values_list('modulo', flat=True).distinct()
        for modulo in sorted(modulos):
            permisos_modulo = admin_role.permisos.filter(modulo=modulo)
            print(f"     {modulo}: {permisos_modulo.count()} permisos")
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")


def verify_admin_user():
    """Verificar que el usuario admin tiene todos los permisos"""
    print("\n👤 Verificando usuario Admin...")
    
    admin_user = User.objects.filter(email='admin@smartsales365.com').first()
    
    if not admin_user:
        print("  ❌ No se encontró el usuario admin@smartsales365.com")
        return
    
    print(f"  ✅ Usuario encontrado: {admin_user.nombre_completo} ({admin_user.email})")
    print(f"  ✅ Rol: {admin_user.rol.nombre}")
    
    # Obtener permisos del rol
    permisos_rol = admin_user.rol.permisos.all()
    print(f"  ✅ Total permisos: {permisos_rol.count()}")
    
    # Mostrar algunos permisos clave
    print(f"\n  📋 Permisos clave verificados:")
    permisos_clave = ['usuarios.listar', 'roles.listar', 'permisos.listar', 'ordenes.listar', 'reportes.generar']
    for codigo in permisos_clave:
        tiene = permisos_rol.filter(codigo=codigo).exists()
        status = "✅" if tiene else "❌"
        print(f"     {status} {codigo}")


if __name__ == '__main__':
    print("=" * 60)
    print("🔐 Asignación de Todos los Permisos al Administrador")
    print("=" * 60)
    
    # Crear todos los permisos
    create_all_permissions()
    
    # Asignar todos al rol Administrador
    assign_all_permissions_to_admin()
    
    # Verificar usuario
    verify_admin_user()
    
    print("\n" + "=" * 60)
    print("✅ Script completado - Recarga la app para ver los cambios")
    print("=" * 60)
