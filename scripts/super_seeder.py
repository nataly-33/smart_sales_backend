#!/usr/bin/env python3
"""
🌱 SUPER SEEDER - Datos Completos para SmartSales365

Crea:
- 1 admin, 2 empleados, 500 clientes
- 1500+ pedidos con detalles y pagos
- 2500 prendas distribuidas en TODAS las categorías
- 4 categorías automáticamente desde S3
- Todas las relaciones y datos correlacionados

Uso:
    python scripts/super_seeder.py

Datos creados:
    - Permisos, Roles, Usuarios (admin+empleados+clientes)
    - Direcciones (múltiples por cliente)
    - Favoritos y Carritos
    - Pedidos, Detalles de Pedido, Pagos
    - Categorías (desde S3: blusas, vestidos, jeans, jackets)
    - 2500 Prendas distribuidas en todas las categorías
"""

import os
import sys
import json
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

import django
django.setup()

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None

from django.db import transaction
from decouple import config
from faker import Faker

from apps.accounts.models import User, Role, Permission
from apps.products.models import Categoria, Marca, Talla, Prenda, StockPrenda, ImagenPrendaURL
from apps.core.constants import PERMISSIONS, ROLES
from apps.customers.models import Direccion, Favoritos
from apps.cart.models import Carrito, ItemCarrito
from apps.orders.models import MetodoPago, Pedido, DetallePedido, Pago

# Configuración
DATASET_PATH = r"D:\1NATALY\SISTEMAS DE INFORMACIÓN II\nuevo GESTION_DOCUMENTAL\smartsales\clothes"
S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default='smart-sales-2025-media')
S3_REGION = config('AWS_S3_REGION_NAME', default='us-east-1')
S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"

# ============= TIPOS DE PRENDAS POR CATEGORÍA =============
TIPOS_BLUSAS = [
    "Polera Primavera", "Camisa Cuello Tortuga", "Polera Básica", "Polera Crop Top",
    "Blusa Elegante", "Camisa Casual", "Polera Oversized", "Blusa de Lino",
    "Camiseta Estampada", "Blusa Satinada", "Polera con Volantes", "Camisa Oxford",
    "Blusa Floral", "Polera Sport", "Camiseta Básica", "Blusa Asimétrica",
    "Polera de Rayas", "Blusa de Gasa", "Camiseta Tie-Dye", "Blusa Peplum"
]

TIPOS_VESTIDOS = [
    "Vestido Floral", "Vestido Midi", "Vestido Maxi", "Vestido Coctel",
    "Vestido Casual", "Vestido de Noche", "Vestido Camisero", "Vestido Wrap",
    "Vestido Asimétrico", "Vestido Plisado", "Vestido Cut-Out", "Vestido Tubo",
    "Vestido Imperio", "Vestido A-Line", "Vestido Skater", "Vestido Shift"
]

TIPOS_JEANS = [
    "Jean Skinny", "Jean Recto", "Jean Boyfriend", "Jean Mom",
    "Jean Bootcut", "Jean Flare", "Jean Wide Leg", "Jean Cargo",
    "Jean High-Waist", "Jean Low-Rise", "Jean Destroyed", "Jean Black",
    "Jean Azul Claro", "Jean Oscuro", "Jean Lavado", "Jean Stretch"
]

TIPOS_JACKETS = [
    "Chaqueta Denim", "Chaqueta de Cuero", "Chaqueta Bomber", "Blazer",
    "Chaqueta Oversize", "Chaqueta Crop", "Chaqueta Moto", "Chaqueta Teddy",
    "Cardigan Largo", "Chaqueta Puffer", "Chaqueta Utility", "Chaqueta Biker",
    "Blazer Oversized", "Chaqueta de Pana", "Chaqueta Military", "Chaqueta Parka"
]

# ============= TIPOS DE TELA =============
TIPOS_TELA = [
    "Algodón 100%", "Poliéster", "Mezcla de algodón",
    "Denim", "Seda", "Lino", "Viscosa", "Elastano",
    "Algodón-Poliéster", "Rayon", "Spandex", "Nylon",
    "Lino puro", "Mezcla de seda", "Twill", "Jersey", "Cuero sintético"
]

# ============= COLORES =============
COLORES = [
    'Negro', 'Blanco', 'Gris', 'Rojo', 'Azul', 'Verde', 'Amarillo',
    'Naranja', 'Rosa', 'Púrpura', 'Marrón', 'Beige', 'Marfil', 'Turquesa',
    'Coral', 'Champagne', 'Marino', 'Burdeos', 'Teal', 'Mostaza', 'Denim'
]

# ============= MARCAS =============
MARCAS = [
    'Nike', 'Adidas', 'Zara', 'H&M', 'Forever 21',
    'Calvin Klein', 'Gucci', 'Prada', 'Louis Vuitton',
    'Tommy Hilfiger', 'Ralph Lauren', 'Gap', 'C&A',
    'Hollister', 'ASOS', 'Uniqlo', 'Mango', 'Shein',
    'Urban Outfitters', 'Vintage Store', 'Levi\'s'
]

fake = Faker('es_ES')

# ============= COLORES ANSI =============
class Colors:
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(texto):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{texto}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")


def print_progress(paso, total, texto):
    pct = (paso / total * 100)
    print(f"  {Colors.CYAN}[{paso:4}/{total}] {pct:5.1f}%{Colors.END} {texto}")


# ============= PERMISOS Y ROLES =============

def seed_permissions():
    """Crear permisos del sistema"""
    print_header("👮 CREANDO PERMISOS")
    
    permisos_creados = []
    for modulo, acciones in PERMISSIONS.items():
        for accion in acciones:
            permiso, created = Permission.objects.get_or_create(
                codigo=f'{modulo}.{accion}',
                defaults={'modulo': modulo, 'nombre': accion}
            )
            if created:
                permisos_creados.append(permiso)
    
    print(f"{Colors.OK}✅ {len(permisos_creados)} permisos creados{Colors.END}")
    return Permission.objects.all()


def seed_roles(all_permissions):
    """Crear roles del sistema"""
    print_header("👥 CREANDO ROLES")
    
    roles_data = {
        'Admin': {
            'descripcion': 'Administrador con acceso total',
            'permisos': all_permissions
        },
        'Empleado': {
            'descripcion': 'Empleado de ventas',
            'permisos': all_permissions.filter(modulo__in=['productos', 'pedidos', 'clientes'])
        },
        'Cliente': {
            'descripcion': 'Cliente del sistema',
            'permisos': all_permissions.filter(codigo__in=['productos.leer', 'pedidos.crear'])
        }
    }
    
    for rol_nombre, rol_info in roles_data.items():
        rol, created = Role.objects.get_or_create(
            nombre=rol_nombre,
            defaults={'descripcion': rol_info['descripcion']}
        )
        rol.permisos.set(rol_info['permisos'])
        if created:
            print(f"  {Colors.OK}✅ Rol {rol_nombre}{Colors.END}")
    
    return Role.objects.all()


# ============= USUARIOS =============

def seed_usuarios_principales():
    """Crear admin y empleados"""
    print_header("👤 CREANDO USUARIOS PRINCIPALES")
    
    usuarios = [
        {
            'email': 'admin@smartsales365.com',
            'nombre': 'Juan',
            'apellido': 'Admin',
            'password': 'Admin2024!',
            'rol': 'Admin',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'email': 'empleado1@smartsales365.com',
            'nombre': 'María',
            'apellido': 'Vendedora',
            'password': 'Empleado2024!',
            'rol': 'Empleado',
            'is_staff': True
        },
        {
            'email': 'empleado2@smartsales365.com',
            'nombre': 'Carlos',
            'apellido': 'Vendedor',
            'password': 'Empleado2024!',
            'rol': 'Empleado',
            'is_staff': True
        }
    ]
    
    usuarios_creados = []
    for u in usuarios:
        rol = Role.objects.get(nombre=u.pop('rol'))
        user, created = User.objects.get_or_create(
            email=u['email'],
            defaults={
                'nombre': u['nombre'],
                'apellido': u['apellido'],
                'rol': rol,
                'activo': True,
                'email_verificado': True,
                'is_staff': u.get('is_staff', False),
                'is_superuser': u.get('is_superuser', False),
                'telefono': f'+591 {random.randint(60000000, 79999999)}'
            }
        )
        if created:
            user.set_password(u['password'])
            user.save()
            usuarios_creados.append(user)
            print(f"  {Colors.OK}✅ {u['email']}{Colors.END}")
    
    return usuarios_creados


def seed_clientes(cantidad=500):
    """Crear clientes con contraseña fija Cliente2024! y fechas distribuidas"""
    print_header(f"👥 CREANDO {cantidad} CLIENTES")
    
    rol_cliente = Role.objects.get(nombre='Cliente')
    clientes = []
    
    # Rango de fechas: enero 2024 hasta hoy
    fecha_inicio = datetime(2024, 1, 1)
    fecha_fin = datetime.now()
    
    for i in range(cantidad):
        if (i + 1) % 50 == 0:
            print_progress(i + 1, cantidad, f"Creando clientes...")
        
        email = f"cliente_{i+1}@example.com"
        
        # Generar fecha aleatoria de registro
        dias_diferencia = (fecha_fin - fecha_inicio).days
        dias_random = random.randint(0, dias_diferencia)
        fecha_registro = fecha_inicio + timedelta(days=dias_random)
        fecha_registro = fecha_registro.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'nombre': fake.first_name(),
                'apellido': fake.last_name(),
                'rol': rol_cliente,
                'activo': True,
                'email_verificado': True,
                'telefono': f'+591 {random.randint(60000000, 79999999)}',
                'created_at': fecha_registro,
                'updated_at': fecha_registro + timedelta(hours=random.randint(0, 24))
            }
        )
        # SIEMPRE establecer contraseña Cliente2024! (creado o existente)
        user.set_password('Cliente2024!')
        user.save()
        clientes.append(user)
    
    print(f"{Colors.OK}✅ {len(clientes)} clientes creados (contraseña: Cliente2024!){Colors.END}")
    return clientes


# ============= CATEGORÍAS DESDE S3 =============

def seed_categorias_desde_s3():
    """Detecta categorías en S3 y las crea automáticamente"""
    print_header("📂 CREANDO CATEGORÍAS DESDE S3")
    
    # Categorías a detectar en S3
    categorias_s3 = {
        'blusas': 'Blusas',
        'vestidos': 'Vestidos',
        'jeans': 'Jeans',
        'jackets': 'Jackets'
    }
    
    categorias = []
    
    for nombre_archivo, nombre_categoria in categorias_s3.items():
        # Construir URL
        url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/categorias/{nombre_archivo}.webp"
        # Intentar con jpg
        url_jpg = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/categorias/{nombre_archivo}.jpg"
        # Intentar con jfif
        url_jfif = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/categorias/{nombre_archivo}.jfif"
        
        cat, created = Categoria.objects.get_or_create(
            nombre=nombre_categoria,
            defaults={
                'descripcion': f'Colección de {nombre_categoria.lower()}',
                'imagen': url,  # Guardar URL directa
                'activa': True
            }
        )
        
        if created:
            print(f"  {Colors.OK}✅ {nombre_categoria}{Colors.END}")
            print(f"     Imagen: {url}")
        
        categorias.append(cat)
    
    return categorias


# ============= TALLAS =============

def seed_tallas():
    """Crear tallas"""
    print_header("📏 CREANDO TALLAS")
    
    tallas_data = [('XS', 1), ('S', 2), ('M', 3), ('L', 4), ('XL', 5), ('XXL', 6)]
    
    tallas = []
    for nombre, orden in tallas_data:
        talla, created = Talla.objects.get_or_create(
            nombre=nombre,
            defaults={'orden': orden}
        )
        if created:
            tallas.append(talla)
            print(f"  {Colors.OK}✅ Talla {nombre}{Colors.END}")
    
    return Talla.objects.all()


# ============= MARCAS =============

def seed_marcas():
    """Crear marcas"""
    print_header("🏷️  CREANDO MARCAS")
    
    marcas = []
    for nombre in MARCAS:
        marca, created = Marca.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'{nombre} - Colección oficial'}
        )
        if created:
            marcas.append(marca)
    
    print(f"{Colors.OK}✅ {len(marcas)} marcas creadas{Colors.END}")
    return marcas


# ============= BLUSAS CON 40% DESTACADAS Y 30% NOVEDADES =============

def seed_blusas(cantidad=2500):
    """Crear 2500 blusas desde S3 (40% destacadas, 30% novedades, fechas distribuidas, nombres sin color)"""
    print_header(f"👗 CREANDO {cantidad} BLUSAS")
    
    categoria_blusas = Categoria.objects.get(nombre='Blusas')
    marcas_list = list(Marca.objects.all())
    tallas_list = list(Talla.objects.all())
    
    # Rango de fechas: enero 2024 hasta hoy
    fecha_inicio = datetime(2024, 1, 1)
    fecha_fin = datetime.now()
    
    blusas = []
    
    for idx in range(1, cantidad + 1):
        if idx % 100 == 0:
            print_progress(idx, cantidad, f"Creando blusas...")
        
        # Generar datos realistas
        tipo_blusa = random.choice(TIPOS_BLUSAS)
        color = random.choice(COLORES)
        marca = random.choice(marcas_list)
        tela = random.choice(TIPOS_TELA)
        precio = round(Decimal(random.uniform(19.99, 89.99)), 2)
        
        # 40% destacadas, 30% novedades
        es_destacada = random.random() < 0.40
        es_novedad = random.random() < 0.30
        
        # NOMBRE SIN COLOR (solo tipo de blusa)
        nombre = tipo_blusa
        
        # Generar descripción realista con color en descripción
        descripciones = [
            f"Hermosa {tipo_blusa.lower()} en color {color.lower()}, elaborada en {tela.lower()}. Perfecta para cualquier ocasión, cómoda y elegante.",
            f"Blusa de alta calidad de {marca.nombre} en {color.lower()}, confeccionada con {tela.lower()}. Ideal para el día a día o para ocasiones especiales.",
            f"{tipo_blusa} moderna y versátil en {color.lower()}. Elaborada en tela de {tela.lower()}, ofrece comodidad y estilo.",
            f"Prenda versátil de marca {marca.nombre}. {tipo_blusa} en {color.lower()} con acabados de calidad en {tela.lower()}.",
            f"Diseño exclusivo en {color.lower()} confeccionado en {tela.lower()}. {tipo_blusa} que combina elegancia y comodidad.",
        ]
        descripcion = random.choice(descripciones)
        
        # Generar fecha aleatoria de creación
        dias_diferencia = (fecha_fin - fecha_inicio).days
        dias_random = random.randint(0, dias_diferencia)
        fecha_creacion = fecha_inicio + timedelta(days=dias_random)
        fecha_creacion = fecha_creacion.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        # Crear blusa (sin get_or_create para evitar duplicados por nombre)
        blusa = Prenda.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            marca=marca,
            color=color,
            material=tela,
            activa=True,
            destacada=es_destacada,
            es_novedad=es_novedad,
            created_at=fecha_creacion,
            updated_at=fecha_creacion + timedelta(hours=random.randint(0, 24))
        )
        
        blusa.categorias.add(categoria_blusas)
        blusa.tallas_disponibles.set(tallas_list)
        
        # Usar número de producto como referencia a las imágenes
        # Si upload_imagenes_s3.py subió 2500 imágenes con nombres 000001_1.jpg hasta 002500_1.jpg
        # entonces usamos idx como el número del producto
        codigo_img = idx
        
        # Crear 1 imagen por producto desde S3
        url_s3 = f"{S3_BASE_URL}/productos/Blusas/{str(codigo_img).zfill(6)}_1.jpg"
        ImagenPrendaURL.objects.create(
            prenda=blusa,
            imagen_url=url_s3,
            es_principal=True,
            orden=1,
            alt_text=f"{nombre} - Imagen principal"
        )
        
        # Crear stock para cada talla
        for talla in tallas_list:
            stock = random.randint(5, 50)
            StockPrenda.objects.create(
                prenda=blusa,
                talla=talla,
                cantidad=stock,
                stock_minimo=3
            )
        
        blusas.append(blusa)
    
    # Estadísticas
    total = Prenda.objects.filter(categorias=categoria_blusas).count()
    destacadas = Prenda.objects.filter(categorias=categoria_blusas, destacada=True).count()
    novedades = Prenda.objects.filter(categorias=categoria_blusas, es_novedad=True).count()
    
    print(f"{Colors.OK}✅ {len(blusas)} blusas creadas{Colors.END}")
    print(f"{Colors.CYAN}   📊 {destacadas} destacadas ({destacadas/total*100:.1f}%){Colors.END}")
    print(f"{Colors.CYAN}   📊 {novedades} novedades ({novedades/total*100:.1f}%){Colors.END}")
    
    return blusas


# ============= DIRECCIONES =============

def seed_direcciones(clientes):
    """Crear direcciones para clientes"""
    print_header("🏠 CREANDO DIRECCIONES")
    
    direcciones = []
    
    for idx, cliente in enumerate(clientes):
        if (idx + 1) % 100 == 0:
            print_progress(idx + 1, len(clientes), "Creando direcciones...")
        
        # Cada cliente tiene 1-3 direcciones
        num_direcciones = random.randint(1, 3)
        
        for i in range(num_direcciones):
            dir_obj = Direccion.objects.create(
                usuario=cliente,
                nombre_completo=f"{cliente.nombre} {cliente.apellido}",
                telefono=cliente.telefono,
                direccion_linea1=fake.street_address(),
                ciudad=fake.city(),
                departamento=fake.state(),
                pais='Bolivia',
                es_principal=(i == 0)
            )
            direcciones.append(dir_obj)
    
    print(f"{Colors.OK}✅ {len(direcciones)} direcciones creadas{Colors.END}")
    return direcciones


# ============= FAVORITOS =============

def seed_favoritos(clientes, prendas):
    """Crear favoritos aleatorios"""
    print_header("⭐ CREANDO FAVORITOS")
    
    favoritos = []
    
    for idx, cliente in enumerate(clientes):
        if (idx + 1) % 100 == 0:
            print_progress(idx + 1, len(clientes), "Creando favoritos...")
        
        # Cada cliente favoritas 0-5 prendas
        num_favoritos = random.randint(0, 5)
        prendas_favoritas = random.sample(prendas, min(num_favoritos, len(prendas)))
        
        for prenda in prendas_favoritas:
            fav, created = Favoritos.objects.get_or_create(
                usuario=cliente,
                prenda=prenda
            )
            if created:
                favoritos.append(fav)
    
    print(f"{Colors.OK}✅ {len(favoritos)} favoritos creados{Colors.END}")
    return favoritos


# ============= MÉTODOS DE PAGO =============

def seed_metodos_pago():
    """Crear métodos de pago"""
    print_header("💳 CREANDO MÉTODOS DE PAGO")
    
    metodos = [
        {'codigo': 'efectivo', 'nombre': 'Efectivo'},
        {'codigo': 'tarjeta', 'nombre': 'Tarjeta de Crédito/Débito'},
        {'codigo': 'paypal', 'nombre': 'PayPal'},
        {'codigo': 'billetera', 'nombre': 'Billetera Virtual'}
    ]
    
    for metodo in metodos:
        obj, created = MetodoPago.objects.get_or_create(
            codigo=metodo['codigo'],
            defaults={'nombre': metodo['nombre'], 'activo': True}
        )
        if created:
            print(f"  {Colors.OK}✅ {metodo['nombre']}{Colors.END}")
    
    return MetodoPago.objects.all()


# ============= PEDIDOS CON FECHAS DISTRIBUIDAS Y NOTAS REALISTAS =============

NOTAS_PLANTILLAS = [
    "Por favor, entregar antes de las 18:00",
    "Dejar con el portero si no estoy",
    "Tocar el timbre dos veces",
    "Llamar antes de entregar",
    "Es un regalo, por favor envolver con cuidado",
    "Entregar en la oficina, segundo piso",
    "Prefiero entrega en horario de mañana",
    "Si no hay nadie, dejar en recepción",
    "Envío urgente, favor priorizar",
    "Verificar tallas antes de enviar",
    "Incluir factura en el paquete",
    "Empacar por separado cada prenda",
    "Notificar cuando esté en camino",
    "Entregar solo en manos del destinatario",
    "Es para un evento el fin de semana",
]


def generar_nota_realista():
    """Genera una nota de cliente realista"""
    # 30% sin nota
    if random.random() < 0.3:
        return ""
    
    # 70% con nota
    if random.random() < 0.7:
        return random.choice(NOTAS_PLANTILLAS)
    else:
        # Generar nota personalizada con Faker
        opciones = [
            f"Entregar en {fake.street_address()}",
            f"Contactar al {fake.phone_number()} antes de llegar",
            f"Buzón en la entrada, dejar ahí si no respondo",
            f"Entrega para {fake.name()}, departamento {random.randint(101, 605)}",
            f"Horario preferido: {random.randint(9, 18)}:00-{random.randint(9, 18)}:00",
        ]
        return random.choice(opciones)


def seed_pedidos(clientes, blusas, cantidad_pedidos=1500):
    """Crear 1500+ pedidos con fechas distribuidas (2024-2025) y notas realistas"""
    print_header(f"📦 CREANDO {cantidad_pedidos} PEDIDOS")
    
    metodos_pago = list(MetodoPago.objects.all())
    tallas = list(Talla.objects.all())
    estados_pedido = ['pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado']
    estados_pago = ['pendiente', 'completado', 'fallido']
    
    # Rango de fechas: enero 2024 hasta hoy
    fecha_inicio = datetime(2024, 1, 1)
    fecha_fin = datetime.now()
    
    pedidos = []
    
    for i in range(cantidad_pedidos):
        if (i + 1) % 100 == 0:
            print_progress(i + 1, cantidad_pedidos, "Creando pedidos...")
        
        cliente = random.choice(clientes)
        direccion = Direccion.objects.filter(usuario=cliente).first()
        
        if not direccion:
            continue
        
        # Generar fecha aleatoria de pedido
        dias_diferencia = (fecha_fin - fecha_inicio).days
        dias_random = random.randint(0, dias_diferencia)
        fecha_pedido = fecha_inicio + timedelta(days=dias_random)
        fecha_pedido = fecha_pedido.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        # Generar nota realista
        nota_cliente = generar_nota_realista()
        
        # Crear pedido con campos correctos del modelo
        pedido = Pedido.objects.create(
            usuario=cliente,
            direccion_envio=direccion,
            estado=random.choice(estados_pedido),
            notas_cliente=nota_cliente,
            subtotal=Decimal('0'),
            total=Decimal('0'),
            created_at=fecha_pedido,
            updated_at=fecha_pedido + timedelta(hours=random.randint(1, 48))
        )
        
        # Agregar 1-5 items
        num_items = random.randint(1, 5)
        prendas_pedido = random.sample(blusas, min(num_items, len(blusas)))
        
        subtotal_pedido = Decimal('0')
        
        for prenda in prendas_pedido:
            cantidad = random.randint(1, 3)
            subtotal = prenda.precio * cantidad
            
            DetallePedido.objects.create(
                pedido=pedido,
                prenda=prenda,
                talla=random.choice(tallas),
                cantidad=cantidad,
                precio_unitario=prenda.precio,
                subtotal=subtotal
            )
            
            subtotal_pedido += subtotal
        
        # Aplicar descuento aleatorio (10% de los pedidos)
        descuento = Decimal('0')
        if random.choice([True] * 9 + [False]):
            descuento = subtotal_pedido * Decimal('0.10')
        
        # Calcular total
        total_pedido = subtotal_pedido - descuento
        
        # Actualizar pedido con montos
        pedido.subtotal = subtotal_pedido
        pedido.descuento = descuento
        pedido.total = total_pedido
        pedido.save()
        
        # Crear pago
        metodo = random.choice(metodos_pago)
        estado_pago = random.choice(estados_pago)
        
        Pago.objects.create(
            pedido=pedido,
            metodo_pago=metodo,
            monto=total_pedido,
            estado=estado_pago,
            transaction_id=f"TRX-{fecha_pedido.timestamp()}-{i}"
        )
        
        pedidos.append(pedido)
    
    print(f"{Colors.OK}✅ {len(pedidos)} pedidos creados{Colors.END}")
    return pedidos


# ============= CARRITOS PARA CLIENTES 1-20 =============

def seed_carritos(clientes, blusas):
    """Llenar carritos de clientes 1-20"""
    print_header("🛒 LLENANDO CARRITOS DE CLIENTES 1-20")
    
    tallas = list(Talla.objects.all())
    carritos_creados = 0
    items_creados = 0
    
    # Primeros 20 clientes
    clientes_con_carrito = clientes[:20]
    
    for idx, cliente in enumerate(clientes_con_carrito, start=1):
        # Obtener o crear carrito
        carrito, created = Carrito.objects.get_or_create(
            usuario=cliente,
            defaults={'activo': True}
        )
        
        if created:
            carritos_creados += 1
        else:
            # Limpiar items existentes
            ItemCarrito.objects.filter(carrito=carrito).delete()
        
        # Agregar 2-8 items al carrito
        num_items = random.randint(2, 8)
        prendas_seleccionadas = random.sample(blusas, min(num_items, len(blusas)))
        
        for prenda in prendas_seleccionadas:
            talla = random.choice(tallas)
            cantidad = random.randint(1, 3)
            
            ItemCarrito.objects.create(
                carrito=carrito,
                prenda=prenda,
                talla=talla,
                cantidad=cantidad,
                precio_unitario=prenda.precio
            )
            items_creados += 1
        
        # Calcular total del carrito
        items = ItemCarrito.objects.filter(carrito=carrito)
        total = sum([item.precio_unitario * item.cantidad for item in items])
        carrito.total = total
        carrito.save()
    
    print(f"{Colors.OK}✅ {carritos_creados} carritos llenos para primeros 20 clientes{Colors.END}")
    print(f"{Colors.OK}✅ {items_creados} items agregados en total{Colors.END}")


# ============= MAIN =============

@transaction.atomic
def seed_all():
    """Ejecutar super seeder completo"""
    
    print_header("🌱 SUPER SEEDER - SMARTSALES365")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Dataset: {DATASET_PATH}")
    
    try:
        # 1. Permisos y Roles
        all_permisos = seed_permissions()
        seed_roles(all_permisos)
        
        # 2. Usuarios
        usuarios_principales = seed_usuarios_principales()
        clientes = seed_clientes(cantidad=500)
        
        # 3. Categorías (desde S3)
        categorias = seed_categorias_desde_s3()
        
        # 4. Tallas y Marcas
        seed_tallas()
        seed_marcas()
        
        # 5. Blusas desde dataset local
        blusas = seed_blusas(cantidad=2500)
        
        # 6. Clientes y direcciones
        seed_direcciones(clientes)
        
        # 7. Favoritos
        seed_favoritos(clientes, blusas)
        
        # 8. Métodos de pago
        seed_metodos_pago()
        
        # 9. Pedidos
        seed_pedidos(clientes, blusas, cantidad_pedidos=1500)
        
        # 10. Carritos para primeros 20 clientes
        seed_carritos(clientes, blusas)
        
        # Resumen final
        print_header("✅ SEEDER COMPLETADO")
        
        from apps.accounts.models import User
        from apps.products.models import Prenda, Categoria, Marca, Talla, StockPrenda
        from apps.customers.models import Direccion, Favoritos
        from apps.orders.models import Pedido, MetodoPago
        from apps.cart.models import Carrito
        
        print(f"\n{Colors.BOLD}📊 ESTADÍSTICAS:{Colors.END}")
        print(f"  • Usuarios: {User.objects.count()} (1 admin, 2 empleados, {User.objects.filter(rol__nombre='Cliente').count()} clientes)")
        print(f"  • Roles: {Role.objects.count()}")
        print(f"  • Categorías: {Categoria.objects.count()}")
        print(f"  • Marcas: {Marca.objects.count()}")
        print(f"  • Tallas: {Talla.objects.count()}")
        print(f"  • Prendas: {Prenda.objects.count()}")
        print(f"  • Stocks: {StockPrenda.objects.count()}")
        print(f"  • Direcciones: {Direccion.objects.count()}")
        print(f"  • Favoritos: {Favoritos.objects.count()}")
        print(f"  • Métodos de Pago: {MetodoPago.objects.count()}")
        print(f"  • Pedidos: {Pedido.objects.count()}")
        print(f"  • Carritos activos: {Carrito.objects.filter(activo=True).count()}")
        
        print(f"\n{Colors.BOLD}📋 CREDENCIALES:{Colors.END}")
        print(f"  • Admin: admin@smartsales365.com / Admin2024!")
        print(f"  • Empleado: empleado1@smartsales365.com / Empleado2024!")
        print(f"  • Cliente (1-20): cliente_1@example.com hasta cliente_20@example.com / Cliente2024!")
        
        print(f"\n{Colors.OK}✨ Todo listo para usar SmartSales365{Colors.END}\n")
        
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ ERROR:{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    seed_all()
