import os
import django
import sys
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User, Role, Permission
from apps.products.models import Categoria, Marca, Talla, Prenda, StockPrenda, ImagenPrenda
from apps.core.constants import PERMISSIONS, ROLES
from apps.customers.models import Direccion, Favoritos
from apps.cart.models import Carrito, ItemCarrito

from decimal import Decimal
import random

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

def seed_categorias():
    """Crear categorías de ropa femenina"""
    print("\n📂 Creando categorías...")
    
    categorias_data = [
        {'nombre': 'Vestidos', 'descripcion': 'Vestidos elegantes y casuales'},
        {'nombre': 'Blusas', 'descripcion': 'Blusas y tops para toda ocasión'},
        {'nombre': 'Pantalones', 'descripcion': 'Pantalones de vestir y casuales'},
        {'nombre': 'Faldas', 'descripcion': 'Faldas de diferentes estilos'},
        {'nombre': 'Jeans', 'descripcion': 'Denim de alta calidad'},
        {'nombre': 'Chaquetas', 'descripcion': 'Chaquetas y abrigos'},
        {'nombre': 'Conjuntos', 'descripcion': 'Conjuntos coordinados'},
        {'nombre': 'Ropa Deportiva', 'descripcion': 'Activewear y sportswear'},
    ]
    
    categorias = []
    for cat_data in categorias_data:
        cat, created = Categoria.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'descripcion': cat_data['descripcion'], 'activa': True}
        )
        if created:
            print(f"  ✅ {cat.nombre}")
        categorias.append(cat)
    
    return categorias


def seed_marcas():
    """Crear marcas"""
    print("\n🏷️ Creando marcas...")
    
    marcas_data = [
        'Zara', 'H&M', 'Forever 21', 'Mango', 'Pull&Bear',
        'Bershka', 'Stradivarius', 'Shein', 'Pretty Little Thing', 'Boohoo'
    ]
    
    marcas = []
    for nombre in marcas_data:
        marca, created = Marca.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'Ropa de {nombre}', 'activa': True}
        )
        if created:
            print(f"  ✅ {nombre}")
        marcas.append(marca)
    
    return marcas


def seed_tallas():
    """Crear tallas"""
    print("\n📏 Creando tallas...")
    
    tallas_data = [
        ('XS', 1), ('S', 2), ('M', 3), ('L', 4), ('XL', 5), ('XXL', 6)
    ]
    
    tallas = []
    for nombre, orden in tallas_data:
        talla, created = Talla.objects.get_or_create(
            nombre=nombre,
            defaults={'orden': orden}
        )
        if created:
            print(f"  ✅ {nombre}")
        tallas.append(talla)
    
    return tallas


def seed_prendas(categorias, marcas, tallas):
    """Crear 50+ prendas de ejemplo"""
    print("\n👗 Creando prendas...")
    
    from faker import Faker
    fake = Faker('es_ES')
    
    colores = [
        'Negro', 'Blanco', 'Azul', 'Rojo', 'Verde', 'Amarillo',
        'Rosa', 'Morado', 'Gris', 'Beige', 'Naranja', 'Turquesa'
    ]
    
    materiales = [
        'Algodón 100%', 'Poliéster', 'Mezcla de algodón',
        'Denim', 'Seda', 'Lino', 'Viscosa', 'Elastano'
    ]
    
    nombres_base = [
        'Vestido Elegante', 'Blusa Casual', 'Pantalón de Vestir',
        'Falda Midi', 'Jean Skinny', 'Chaqueta Denim',
        'Conjunto Deportivo', 'Top Crop', 'Cardigan',
        'Blazer', 'Vestido Maxi', 'Short', 'Palazzo',
        'Camisa', 'Sudadera', 'Leggings', 'Jumpsuit'
    ]
    
    prendas_creadas = []
    
    for i in range(60):  # Crear 60 prendas
        nombre_base = random.choice(nombres_base)
        color = random.choice(colores)
        nombre = f"{nombre_base} {color}"
        
        # Evitar duplicados
        if Prenda.objects.filter(nombre=nombre).exists():
            nombre = f"{nombre} {i+1}"
        
        prenda = Prenda.objects.create(
            nombre=nombre,
            descripcion=fake.text(max_nb_chars=200),
            precio=Decimal(random.randint(100, 800)),
            marca=random.choice(marcas),
            color=color,
            material=random.choice(materiales),
            activa=True,
            destacada=random.random() < 0.3,  # 30% destacadas
            es_novedad=random.random() < 0.2   # 20% novedades
        )
        
        # Asignar 1-3 categorías aleatorias
        num_categorias = random.randint(1, 3)
        prenda.categorias.set(random.sample(categorias, num_categorias))
        
        # Asignar todas las tallas o algunas aleatorias
        if random.random() < 0.7:  # 70% tienen todas las tallas
            prenda.tallas_disponibles.set(tallas)
        else:
            num_tallas = random.randint(3, 5)
            prenda.tallas_disponibles.set(random.sample(tallas, num_tallas))
        
        # Crear stocks para cada talla disponible
        for talla in prenda.tallas_disponibles.all():
            StockPrenda.objects.create(
                prenda=prenda,
                talla=talla,
                cantidad=random.randint(0, 50),
                stock_minimo=5
            )
        
        prendas_creadas.append(prenda)
        
        if (i + 1) % 10 == 0:
            print(f"  ✅ {i + 1} prendas creadas...")
    
    print(f"Total: {len(prendas_creadas)} prendas creadas")
    return prendas_creadas

def seed_direcciones(usuarios):
    """Crear direcciones para clientes"""
    print("\n🏠 Creando direcciones...")
    
    # Solo para el cliente de prueba
    cliente = next((u for u in usuarios if u.email == 'cliente@gmail.com'), None)
    
    if not cliente:
        print("  ⚠️  Cliente de prueba no encontrado")
        return []
    
    direcciones_data = [
        {
            'nombre_completo': 'Carlos Cliente',
            'telefono': '+591 70000003',
            'direccion_linea1': 'Av. Heroínas #1234',
            'direccion_linea2': 'Entre Av. Oquendo y San Martín',
            'ciudad': 'Cochabamba',
            'departamento': 'Cochabamba',
            'codigo_postal': '',
            'pais': 'Bolivia',
            'referencia': 'Cerca del centro comercial',
            'es_principal': True
        },
        {
            'nombre_completo': 'Carlos Cliente',
            'telefono': '+591 70000003',
            'direccion_linea1': 'Calle Sucre #567',
            'direccion_linea2': '',
            'ciudad': 'Cochabamba',
            'departamento': 'Cochabamba',
            'codigo_postal': '',
            'pais': 'Bolivia',
            'referencia': 'Casa color amarillo',
            'es_principal': False
        }
    ]
    
    direcciones = []
    for dir_data in direcciones_data:
        direccion = Direccion.objects.create(
            usuario=cliente,
            **dir_data
        )
        direcciones.append(direccion)
        print(f"  ✅ {direccion.ciudad} - {'Principal' if direccion.es_principal else 'Secundaria'}")
    
    return direcciones


def seed_favoritos(usuarios, prendas):
    """Crear favoritos para el cliente"""
    print("\n⭐ Creando favoritos...")
    
    cliente = next((u for u in usuarios if u.email == 'cliente@gmail.com'), None)
    
    if not cliente or len(prendas) < 5:
        print("  ⚠️  Cliente o prendas insuficientes")
        return []
    
    # Agregar 5 prendas aleatorias a favoritos
    import random
    prendas_favoritas = random.sample(prendas, 5)
    
    favoritos = []
    for prenda in prendas_favoritas:
        favorito = Favoritos.objects.create(
            usuario=cliente,
            prenda=prenda
        )
        favoritos.append(favorito)
        print(f"  ✅ {prenda.nombre}")
    
    return favoritos


def seed_carritos(usuarios, prendas, tallas):
    """Crear carritos con items para clientes"""
    print("\n🛒 Creando carritos...")
    
    cliente = next((u for u in usuarios if u.email == 'cliente@gmail.com'), None)
    
    if not cliente or len(prendas) < 3:
        print("  ⚠️  Cliente o prendas insuficientes")
        return None
    
    # Crear carrito
    carrito = Carrito.objects.create(usuario=cliente)
    
    # Agregar 3 items aleatorios
    import random
    prendas_carrito = random.sample(prendas, 3)
    
    for prenda in prendas_carrito:
        talla_disponible = prenda.tallas_disponibles.first()
        if talla_disponible:
            ItemCarrito.objects.create(
                carrito=carrito,
                prenda=prenda,
                talla=talla_disponible,
                cantidad=random.randint(1, 3),
                precio_unitario=prenda.precio
            )
            print(f"  ✅ {prenda.nombre} - Talla {talla_disponible.nombre}")
    
    return carrito

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
    
     # 4. Categorías
    categorias = seed_categorias()
    
    # 5. Marcas
    marcas = seed_marcas()
    
    # 6. Tallas
    tallas = seed_tallas()
    
    # 7. Prendas (50+)
    prendas = seed_prendas(categorias, marcas, tallas)
    
    # 8. Direcciones
    direcciones = seed_direcciones(usuarios_creados)
    
    # 9. Favoritos
    favoritos = seed_favoritos(usuarios_creados, prendas)
    
    # 10. Carritos
    carrito = seed_carritos(usuarios_creados, prendas, tallas)
    
    # Resumen final
    print("\n" + "="*60)
    print("🎉 ¡SEEDERS COMPLETADOS!")
    print("="*60)
    print(f"\n📊 RESUMEN:")
    print(f"  - Permisos: {Permission.objects.count()}")
    print(f"  - Roles: {Role.objects.count()}")
    print(f"  - Usuarios: {User.objects.count()}")
    print(f"  - Categorías: {Categoria.objects.count()}")
    print(f"  - Marcas: {Marca.objects.count()}")
    print(f"  - Tallas: {Talla.objects.count()}")
    print(f"  - Prendas: {Prenda.objects.count()}")
    print(f"  - Stocks: {StockPrenda.objects.count()}")
    print(f"  - Direcciones: {Direccion.objects.count()}")
    print(f"  - Favoritos: {Favoritos.objects.count()}")
    print(f"  - Carritos: {Carrito.objects.count()}")
    if carrito:
        print(f"  - Items en carrito: {carrito.total_items}")
    
    print("\n📋 CREDENCIALES DE ACCESO:")
    print("-" * 60)
    
    usuarios_test = [
        ('Admin', 'admin@smartsales365.com', 'Admin2024!'),
        ('Empleado', 'empleado@smartsales365.com', 'Empleado2024!'),
        ('Cliente', 'cliente@gmail.com', 'Cliente2024!'),
        ('Delivery', 'delivery@smartsales365.com', 'Delivery2024!')
    ]
    
    for rol, email, password in usuarios_test:
        print(f"  {rol:10} → {email:35} / {password}")
    
    print("-" * 60)
    print("\n✅ Puedes iniciar sesión con cualquiera de estas cuentas")
    print("🚀 Ejecuta: python manage.py runserver")
    print("📚 Swagger: http://localhost:8000/api/docs/\n")

if __name__ == '__main__':
    seed_all()