import os
import django
import sys
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User, Role, Permission
from apps.core.constants import PERMISSIONS, ROLES


def seed_permissions():
    """Crear permisos del sistema"""
    print("\n📝 Creando permisos...")
    permisos_creados = []
    
    for modulo, acciones in PERMISSIONS.items():
        for accion in acciones:
            codigo = f'{modulo}.{accion}'
            permiso, created = Permission.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': f'{accion.title()} {modulo}',
                    'modulo': modulo,
                    'descripcion': f'Permite {accion} en el módulo de {modulo}'
                }
            )
            if created:
                permisos_creados.append(permiso)
                print(f"  ✅ {codigo}")
    
    print(f"Total: {len(permisos_creados)} permisos creados")
    return Permission.objects.all()


def seed_roles(all_permissions):
    """Crear roles del sistema"""
    print("\n👥 Creando roles...")
    
    roles_data = {
        'Admin': {
            'descripcion': 'Administrador con acceso total al sistema',
            'permisos': all_permissions  # Todos los permisos
        },
        'Empleado': {
            'descripcion': 'Empleado con acceso a ventas y productos',
            'permisos': all_permissions.filter(
                modulo__in=['productos', 'categorias', 'marcas', 'pedidos', 'ventas', 'clientes']
            )
        },
        'Cliente': {
            'descripcion': 'Cliente del sistema con acceso limitado',
            'permisos': all_permissions.filter(
                codigo__in=[
                    'productos.leer', 
                    'pedidos.crear', 
                    'pedidos.leer',
                    'categorias.leer',
                    'marcas.leer'
                ]
            )
        },
        'Delivery': {
            'descripcion': 'Personal de delivery para gestión de envíos',
            'permisos': all_permissions.filter(modulo__in=['envios', 'pedidos'])
        }
    }
    
    roles_created = []
    for rol_nombre, rol_info in roles_data.items():
        rol, created = Role.objects.get_or_create(
            nombre=rol_nombre,
            defaults={
                'descripcion': rol_info['descripcion'], 
                'es_rol_sistema': True
            }
        )
        rol.permisos.set(rol_info['permisos'])
        
        if created:
            roles_created.append(rol)
        
        print(f"  ✅ {rol_nombre} ({rol.permisos.count()} permisos)")
    
    return roles_created


def seed_users():
    """Crear usuarios de prueba"""
    print("\n👤 Creando usuarios de prueba...")
    
    usuarios = [
        {
            'email': 'admin@smartsales365.com',
            'password': 'Admin2024!',
            'nombre': 'Juan',
            'apellido': 'Administrador',
            'telefono': '+591 70000001',
            'rol': 'Admin',
            'codigo_empleado': 'EMP-ADMIN-001',
            'activo': True,
            'email_verificado': True,
            'is_staff': True,
            'is_superuser': True
        },
        {
            'email': 'empleado@smartsales365.com',
            'password': 'Empleado2024!',
            'nombre': 'María',
            'apellido': 'Vendedora',
            'telefono': '+591 70000002',
            'rol': 'Empleado',
            'codigo_empleado': 'EMP-VEND-001',
            'activo': True,
            'email_verificado': True
        },
        {
            'email': 'cliente@gmail.com',
            'password': 'Cliente2024!',
            'nombre': 'Carlos',
            'apellido': 'Cliente',
            'telefono': '+591 70000003',
            'rol': 'Cliente',
            'saldo_billetera': Decimal('500.00'),
            'activo': True,
            'email_verificado': True
        },
        {
            'email': 'delivery@smartsales365.com',
            'password': 'Delivery2024!',
            'nombre': 'Pedro',
            'apellido': 'Repartidor',
            'telefono': '+591 70000004',
            'rol': 'Delivery',
            'codigo_empleado': 'EMP-DEL-001',
            'activo': True,
            'email_verificado': True
        }
    ]
    
    usuarios_creados = []
    for user_data in usuarios:
        rol_nombre = user_data.pop('rol')
        rol = Role.objects.get(nombre=rol_nombre)
        
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'nombre': user_data['nombre'],
                'apellido': user_data['apellido'],
                'telefono': user_data.get('telefono', ''),
                'codigo_empleado': user_data.get('codigo_empleado', ''),
                'rol': rol,
                'activo': user_data.get('activo', True),
                'email_verificado': user_data.get('email_verificado', True),
                'saldo_billetera': user_data.get('saldo_billetera', Decimal('0.00')),
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False)
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            usuarios_creados.append(user)
            print(f"  ✅ {user.email} ({rol_nombre}) - Pass: {user_data['password']}")
    
    return usuarios_creados


def seed_all():
    """Ejecutar todos los seeders"""
    print("\n" + "="*60)
    print("🌱 INICIANDO SEEDERS - SMARTSALES365")
    print("="*60)
    
    # 1. Crear permisos
    all_permissions = seed_permissions()
    
    # 2. Crear roles
    roles_created = seed_roles(all_permissions)
    
    # 3. Crear usuarios
    usuarios_creados = seed_users()
    
    # Resumen final
    print("\n" + "="*60)
    print("🎉 ¡SEEDERS COMPLETADOS!")
    print("="*60)
    print(f"\n📊 RESUMEN:")
    print(f"  - Permisos: {Permission.objects.count()}")
    print(f"  - Roles: {Role.objects.count()}")
    print(f"  - Usuarios: {User.objects.count()}")
    print("\n📋 CREDENCIALES DE ACCESO:")
    print("-" * 60)
    
    usuarios_test = [
        ('Admin', 'admin@smartsales.com', 'admin2024*'),
        ('Empleado', 'empleado@smartsales.com', 'empleado2024*'),
        ('Cliente', 'cliente@gmail.com', 'cliente2024*'),
        ('Delivery', 'delivery@smartsales.com', 'delivery2024*')
    ]
    
    for rol, email, password in usuarios_test:
        print(f"  {rol:10} → {email:35} / {password}")
    
    print("-" * 60)
    print("\n✅ Puedes iniciar sesión con cualquiera de estas cuentas")
    print("🚀 Ejecuta: python manage.py runserver\n")


if __name__ == '__main__':
    seed_all()