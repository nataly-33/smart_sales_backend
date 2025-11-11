#!/usr/bin/env python3
"""
🌱 SUPER SEEDER V2 - Datos Realistas de 3 Años para SmartSales365

Genera datos de 2023, 2024 y 2025 con:
- Estacionalidad realista por categoría
- ~1500-1600 prendas por año (total ~4800 prendas)
- ~1000-1200 pedidos por año (total ~3500 pedidos)
- 500 clientes (80% mujeres)
- 100 primeros clientes con carritos (2-10 items)
- Distribución por categorías: Blusas (2000), Vestidos (500), Jeans (1000), Jackets (500)
- Precios realistas redondeados
- Fechas distribuidas coherentemente

⚠️  IMPORTANTE: 2025 solo genera datos hasta el 11 de NOVIEMBRE (fecha actual)
               Esto evita contaminar el modelo de IA con datos del futuro.

Uso:
    python scripts/super_seeder_v2.py
"""

import os
import sys
import django
import random
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

django.setup()

from django.utils import timezone as django_timezone

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

# ============= CONFIGURACIÓN =============
S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default='smart-sales-2025-media')
S3_REGION = config('AWS_S3_REGION_NAME', default='us-east-1')
S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"

fake = Faker(['es_ES', 'es_MX'])
random.seed(42)

# ============= DATOS MAESTROS =============

DEPARTAMENTOS_BOLIVIA = ['La Paz', 'Santa Cruz', 'Cochabamba', 'Tarija', 'Pando', 'Beni', 'Oruro', 'Potosí', 'Chuquisaca']

# Estacionalidad por categoría y mes (multiplicador)
ESTACIONALIDAD = {
    'Blusas': {
        1: 0.9, 2: 0.85, 3: 1.0, 4: 1.1, 5: 1.15,
        6: 1.2, 7: 1.25, 8: 1.5, 9: 1.45, 10: 1.3,
        11: 1.4, 12: 1.5
    },
    'Vestidos': {
        1: 1.3, 2: 1.2, 3: 0.9, 4: 0.85, 5: 0.9,
        6: 0.95, 7: 1.0, 8: 1.1, 9: 1.15, 10: 1.2,
        11: 1.4, 12: 1.6
    },
    'Jeans': {
        1: 1.0, 2: 1.0, 3: 1.05, 4: 1.1, 5: 1.15,
        6: 1.1, 7: 1.05, 8: 1.0, 9: 1.0, 10: 1.05,
        11: 1.1, 12: 1.15
    },
    'Jackets': {
        1: 0.8, 2: 0.75, 3: 0.9, 4: 1.1, 5: 1.4,
        6: 1.6, 7: 1.5, 8: 1.3, 9: 1.0, 10: 0.9,
        11: 0.85, 12: 0.8
    }
}

# Diccionarios para generar nombres de productos
VESTIDOS_DICT = {
    'estilo': ['De gala', 'Cocktail', 'Casual', 'Boho', 'Vintage', 'Playero', 'Urbano', 'Floreal', 'Fiesta', 'Nupcial', 'Sencillo'],
    'corte': ['Corto', 'Largo', 'Mini', 'Midi', 'Asimétrico', 'Tubo', 'Corte A', 'Princesa', 'Sirena', 'Imperio', 'Skater', 'Recto'],
    'escote': ['V', 'Redondo', 'Corazón', 'Halter', 'Cuello alto', 'Barco', 'Strapless', 'Asimétrico', 'Hombros caídos'],
    'manga': ['Larga', 'Corta', 'Tres cuartos', 'Sin mangas', 'Farol', 'Abullonada', 'Puffy', 'Acampanada'],
    'tejido': ['Algodón', 'Seda', 'Satinado', 'Lino', 'Encaje', 'Gasa', 'Terciopelo', 'Tule', 'Denim', 'Lana'],
    'detalle': ['Con cinturón', 'Plisado', 'Volantes', 'Drapeado', 'Lentejuelas', 'Bordado', 'Flecos', 'Abertura lateral'],
    'patron': ['Liso', 'Floreal', 'Geométrico', 'Étnico', 'Rayas', 'Lunares', 'Animal print', 'Abstracto', 'Tie-dye']
}

JEANS_DICT = {
    'corte': ['Skinny', 'Slim fit', 'Regular fit', 'Relaxed fit', 'Boyfriend', 'Mom fit', 'Straight', 'Bootcut', 'Flared'],
    'tiro': ['Tiro alto', 'Tiro medio', 'Tiro bajo', 'Paperbag'],
    'largo': ['Tobillero', 'Crop', 'Completo', 'Desgastado'],
    'color': ['Azul oscuro', 'Azul claro', 'Gris', 'Negro', 'Blanco', 'Lavado ácido', 'Deslavado', 'Raw denim'],
    'detalle': ['Rotos', 'Desgarrados', 'Bordados', 'Parches', 'Bolsillos cargo', 'Con pinzas']
}

JACKETS_DICT = {
    'tipo': ['Denim', 'Biker', 'Bomber', 'Parka', 'Blazer', 'Cortavientos', 'Gabardina', 'Plumas', 'Over-shirt'],
    'tejido': ['Cuero', 'Piel sintética', 'Denim', 'Poliéster', 'Lana', 'Pana', 'Terciopelo', 'Nylon', 'Ante'],
    'ajuste': ['Oversize', 'Cropped', 'Entallada', 'Larga', 'Estructurada'],
    'cuello': ['Con capucha', 'Cuello alto', 'Solapa', 'Mao'],
    'color': ['Negro', 'Marrón', 'Caqui', 'Verde militar', 'Rojo', 'Camuflaje', 'Neón'],
    'detalle': ['Con cremalleras', 'Tachuelas', 'Forro polar', 'Acolchada', 'Bolsillos múltiples', 'Ribete']
}

BLUSAS_TIPOS = [
    "Polera Primavera", "Camisa Cuello Tortuga", "Polera Básica", "Polera Crop Top",
    "Blusa Elegante", "Camisa Casual", "Polera Oversized", "Blusa de Lino",
    "Camiseta Estampada", "Blusa Satinada", "Polera con Volantes", "Camisa Oxford",
    "Blusa Floral", "Polera Sport", "Camiseta Básica", "Blusa Asimétrica",
    "Polera de Rayas", "Blusa de Gasa", "Camiseta Tie-Dye", "Blusa Peplum"
]

MARCAS = [
    'Nike', 'Adidas', 'Zara', 'H&M', 'Forever 21',
    'Calvin Klein', 'Gucci', 'Prada', 'Louis Vuitton',
    'Tommy Hilfiger', 'Ralph Lauren', 'Gap', 'C&A',
    'Hollister', 'ASOS', 'Uniqlo', 'Mango', 'Shein',
    'Urban Outfitters', 'Vintage Store', 'Levi\'s'
]

COLORES = [
    'Negro', 'Blanco', 'Gris', 'Rojo', 'Azul', 'Verde', 'Amarillo',
    'Naranja', 'Rosa', 'Púrpura', 'Marrón', 'Beige', 'Marfil', 'Turquesa',
    'Coral', 'Champagne', 'Marino', 'Burdeos', 'Teal', 'Mostaza', 'Denim'
]

TIPOS_TELA = [
    "Algodón 100%", "Poliéster", "Mezcla de algodón",
    "Denim", "Seda", "Lino", "Viscosa", "Elastano",
    "Algodón-Poliéster", "Rayon", "Spandex", "Nylon",
    "Lino puro", "Mezcla de seda", "Twill", "Jersey", "Cuero sintético"
]

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
    "",  # Sin nota
    "",
    ""
]

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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{texto.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")

def print_progress(paso, total, texto):
    pct = (paso / total * 100) if total > 0 else 0
    print(f"  {Colors.CYAN}[{paso:4}/{total}] {pct:5.1f}%{Colors.END} {texto}")

# ============= GENERADORES DE NOMBRES =============

def generar_nombre_vestido():
    """Genera nombre realista para vestido"""
    estilo = random.choice(VESTIDOS_DICT['estilo'])
    corte = random.choice(VESTIDOS_DICT['corte'])
    
    if random.random() > 0.5:
        return f"Vestido {estilo} {corte}"
    else:
        detalle = random.choice(VESTIDOS_DICT['detalle'])
        return f"Vestido {corte} {detalle}"

def generar_descripcion_vestido():
    """Genera descripción realista para vestido"""
    escote = random.choice(VESTIDOS_DICT['escote'])
    manga = random.choice(VESTIDOS_DICT['manga'])
    tejido = random.choice(VESTIDOS_DICT['tejido'])
    patron = random.choice(VESTIDOS_DICT['patron'])
    
    descripciones = [
        f"Elegante vestido con escote {escote} y manga {manga.lower()}. Confeccionado en {tejido.lower()} de alta calidad. Patrón {patron.lower()}.",
        f"Vestido moderno de {tejido.lower()} con escote {escote} y diseño {patron.lower()}. Manga {manga.lower()} para mayor comodidad.",
        f"Hermoso vestido {patron.lower()} con escote {escote}. Material: {tejido}. Perfecto para cualquier ocasión.",
    ]
    
    return random.choice(descripciones)

def generar_nombre_jeans():
    """Genera nombre realista para jeans"""
    corte = random.choice(JEANS_DICT['corte'])
    tiro = random.choice(JEANS_DICT['tiro'])
    
    if random.random() > 0.6:
        return f"Jeans {corte} {tiro}"
    else:
        return f"Jeans {corte}"

def generar_descripcion_jeans():
    """Genera descripción realista para jeans"""
    corte = random.choice(JEANS_DICT['corte'])
    tiro = random.choice(JEANS_DICT['tiro'])
    color = random.choice(JEANS_DICT['color'])
    detalle = random.choice(JEANS_DICT['detalle'])
    
    descripciones = [
        f"Jeans {corte} de {tiro.lower()} en color {color.lower()}. Denim de alta calidad con {detalle.lower()}.",
        f"Pantalón jean {corte} con {tiro.lower()}. Acabado {color.lower()}. Estilo moderno y cómodo.",
        f"Jeans {corte} en tonalidad {color.lower()}. Corte {tiro.lower()} con detalles {detalle.lower()}.",
    ]
    
    return random.choice(descripciones)

def generar_nombre_jacket():
    """Genera nombre realista para jacket"""
    tipo = random.choice(JACKETS_DICT['tipo'])
    ajuste = random.choice(JACKETS_DICT['ajuste'])
    
    if random.random() > 0.5:
        return f"Chaqueta {tipo} {ajuste}"
    else:
        return f"Chaqueta {tipo}"

def generar_descripcion_jacket():
    """Genera descripción realista para jacket"""
    tipo = random.choice(JACKETS_DICT['tipo'])
    tejido = random.choice(JACKETS_DICT['tejido'])
    cuello = random.choice(JACKETS_DICT['cuello'])
    detalle = random.choice(JACKETS_DICT['detalle'])
    
    descripciones = [
        f"Chaqueta {tipo} de {tejido.lower()} con {cuello.lower()}. {detalle} para mayor estilo.",
        f"Moderna chaqueta tipo {tipo} confeccionada en {tejido.lower()}. Diseño {cuello.lower()} y {detalle.lower()}.",
        f"Chaqueta {tipo} en {tejido.lower()}. {cuello} y {detalle.lower()}. Perfecta para cualquier temporada.",
    ]
    
    return random.choice(descripciones)

def generar_fecha_realista(año, mes, categoria):
    """
    Genera fecha con distribución realista según estacionalidad (timezone-aware)
    
    ⚠️  IMPORTANTE: Para 2025, no genera fechas posteriores al 11 de Noviembre
    """
    dias_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if año % 4 == 0 and mes == 2:
        dias_mes[1] = 29
    
    # LÍMITE PARA 2025: 11 de Noviembre
    if año == 2025:
        if mes > 11:
            raise ValueError(f"No se pueden generar datos para 2025 después de Noviembre (mes {mes})")
        if mes == 11:
            # Noviembre 2025: máximo hasta día 11
            max_dia = 11
        else:
            max_dia = dias_mes[mes - 1]
    else:
        max_dia = dias_mes[mes - 1]
    
    # Más probabilidad en días laborables
    while True:
        dia = random.randint(1, max_dia)
        fecha = django_timezone.make_aware(datetime(año, mes, dia, random.randint(8, 20), random.randint(0, 59)))
        
        # 70% días laborables, 30% fines de semana
        if fecha.weekday() < 5:  # Lunes a Viernes
            if random.random() < 0.7:
                return fecha
        else:  # Sábado y Domingo
            if random.random() < 0.3:
                return fecha

def redondear_precio(precio):
    """Redondea precio a números enteros"""
    return int(round(precio))

# ============= FUNCIONES DE SEEDING =============

def seed_permissions():
    """Crear permisos del sistema"""
    print_header("👮 CREANDO PERMISOS")
    
    permisos_creados = []
    for modulo, acciones in PERMISSIONS.items():
        for accion in acciones:
            codigo = f"{modulo}.{accion}"
            permiso, created = Permission.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': f"{modulo.title()} - {accion.title()}",
                    'descripcion': f"Permiso para {accion} en módulo {modulo}",
                    'modulo': modulo
                }
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
            defaults={'descripcion': rol_info['descripcion'], 'es_rol_sistema': True}
        )
        if created:
            rol.permisos.set(rol_info['permisos'])
            print(f"  {Colors.OK}✓{Colors.END} Rol '{rol_nombre}' creado")
    
    return Role.objects.all()

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
        rol = Role.objects.get(nombre=u['rol'])
        user, created = User.objects.get_or_create(
            email=u['email'],
            defaults={
                'nombre': u['nombre'],
                'apellido': u['apellido'],
                'rol': rol,
                'is_staff': u.get('is_staff', False),
                'is_superuser': u.get('is_superuser', False),
                'activo': True,
                'email_verificado': True
            }
        )
        
        if created:
            user.set_password(u['password'])
            user.save()
            print(f"  {Colors.OK}✓{Colors.END} {u['email']} creado")
            usuarios_creados.append(user)
    
    return usuarios_creados

def seed_clientes(cantidad=1000):
    """Crear clientes con fechas distribuidas en 3 años (80% mujeres)"""
    print_header(f"👥 CREANDO {cantidad} CLIENTES (80% MUJERES)")
    
    rol_cliente = Role.objects.get(nombre='Cliente')
    clientes = []
    
    fecha_inicio = django_timezone.make_aware(datetime(2023, 1, 1))
    fecha_fin = django_timezone.make_aware(datetime(2025, 11, 11))
    
    for i in range(cantidad):
        # 80% mujeres
        es_mujer = random.random() < 0.8
        
        if es_mujer:
            nombre = fake.first_name_female()
        else:
            nombre = fake.first_name_male()
        
        apellido = fake.last_name()
        
        # Fecha de registro distribuida
        dias_totales = (fecha_fin - fecha_inicio).days
        dias_random = random.randint(0, dias_totales)
        fecha_registro = fecha_inicio + timedelta(days=dias_random)
        
        email = f"cliente{i+1}@{fake.domain_name()}"
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'telefono': f"+591 {random.randint(60000000, 79999999)}",
                'rol': rol_cliente,
                'activo': True,
                'email_verificado': True,
            }
        )
        
        if created:
            user.set_password('Cliente2024!')
            # Forzar la fecha de created_at
            User.objects.filter(id=user.id).update(created_at=fecha_registro)
            user.refresh_from_db()
            clientes.append(user)
        
        if (i + 1) % 100 == 0:
            print_progress(i + 1, cantidad, f"{i+1} clientes creados")
    
    print(f"{Colors.OK}✅ {len(clientes)} clientes creados (contraseña: Cliente2024!){Colors.END}")
    return clientes

def seed_categorias():
    """Crear categorías principales"""
    print_header("📦 CREANDO CATEGORÍAS")
    
    categorias_data = [
        {
            'nombre': 'Blusas',
            'descripcion': 'Blusas, camisas y tops para toda ocasión',
            'imagen': f'{S3_BASE_URL}/categories/blusas.jpg'
        },
        {
            'nombre': 'Vestidos',
            'descripcion': 'Vestidos elegantes y casuales',
            'imagen': f'{S3_BASE_URL}/categories/vestidos.jpg'
        },
        {
            'nombre': 'Jeans',
            'descripcion': 'Pantalones jean de mezclilla',
            'imagen': f'{S3_BASE_URL}/categories/jeans.jpg'
        },
        {
            'nombre': 'Jackets',
            'descripcion': 'Chaquetas y abrigos',
            'imagen': f'{S3_BASE_URL}/categories/jackets.jpg'
        }
    ]
    
    categorias = []
    for cat_data in categorias_data:
        cat, created = Categoria.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={
                'descripcion': cat_data['descripcion'],
                'imagen': cat_data['imagen'],
                'activa': True
            }
        )
        categorias.append(cat)
        if created:
            print(f"  {Colors.OK}✓{Colors.END} Categoría '{cat_data['nombre']}' creada")
    
    return categorias

def seed_tallas():
    """Crear tallas"""
    print_header("📏 CREANDO TALLAS")
    
    tallas_orden = [
        ('XXS', 1), ('XS', 2), ('S', 3), ('M', 4),
        ('L', 5), ('XL', 6), ('XXL', 7), ('XXXL', 8)
    ]
    
    tallas = []
    for nombre, orden in tallas_orden:
        talla, created = Talla.objects.get_or_create(
            nombre=nombre,
            defaults={'orden': orden}
        )
        tallas.append(talla)
    
    print(f"{Colors.OK}✅ {len(tallas)} tallas creadas{Colors.END}")
    return tallas

def seed_marcas():
    """Crear marcas"""
    print_header("🏷️ CREANDO MARCAS")
    
    marcas = []
    for marca_nombre in MARCAS:
        marca, created = Marca.objects.get_or_create(
            nombre=marca_nombre,
            defaults={
                'descripcion': f'Marca {marca_nombre}',
                'activa': True
            }
        )
        marcas.append(marca)
    
    print(f"{Colors.OK}✅ {len(marcas)} marcas creadas{Colors.END}")
    return marcas

def seed_prendas_por_año(año, categorias_dict, marcas, tallas):
    """
    Crear prendas para un año específico con distribución realista
    ~1500-1600 prendas por año
    
    ⚠️  IMPORTANTE: Para 2025, solo genera prendas hasta el 11 de Noviembre
    """
    print_header(f"👗 CREANDO PRENDAS PARA {año}")
    
    # Obtener imágenes de S3 para blusas
    imagenes_blusas = []
    if boto3:
        try:
            s3_client = boto3.client('s3', region_name=S3_REGION)
            response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix='productos/Blusas/')
            if 'Contents' in response:
                imagenes_blusas = [
                    f"{S3_BASE_URL}/{obj['Key']}"
                    for obj in response['Contents']
                    if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png'))
                ][:2000]  # Solo las primeras 2000
        except Exception as e:
            print(f"{Colors.WARN}⚠️ No se pudieron cargar imágenes de S3: {e}{Colors.END}")
    
    # Imágenes por defecto para otras categorías
    imagen_default = {
        'Vestidos': f'{S3_BASE_URL}/categories/vestidos.jpg',
        'Jeans': f'{S3_BASE_URL}/categories/jeans.jpg',
        'Jackets': f'{S3_BASE_URL}/categories/jackets.jpg'
    }
    
    # Distribución de prendas por categoría para el año
    if año == 2023:
        distribucion = {'Blusas': 650, 'Vestidos': 150, 'Jeans': 350, 'Jackets': 150}
    elif año == 2024:
        distribucion = {'Blusas': 700, 'Vestidos': 180, 'Jeans': 380, 'Jackets': 180}
    else:  # 2025
        distribucion = {'Blusas': 650, 'Vestidos': 170, 'Jeans': 270, 'Jackets': 170}
    
    prendas_creadas = []
    idx_imagen_blusa = 0
    
    for categoria_nombre, cantidad in distribucion.items():
        categoria = categorias_dict[categoria_nombre]
        
        print(f"\n  {Colors.BLUE}Categoría: {categoria_nombre} ({cantidad} prendas){Colors.END}")
        
        for i in range(cantidad):
            # Generar nombre y descripción según categoría
            if categoria_nombre == 'Blusas':
                nombre = random.choice(BLUSAS_TIPOS)
                descripcion = f"{nombre} de alta calidad. Material: {random.choice(TIPOS_TELA)}. Perfecta para el día a día."
                # Precio: 10-90
                precio_base = random.choice([10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90])
            elif categoria_nombre == 'Vestidos':
                nombre = generar_nombre_vestido()
                descripcion = generar_descripcion_vestido()
                # Precio: 20-180
                precio_base = random.choice([20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180])
            elif categoria_nombre == 'Jeans':
                nombre = generar_nombre_jeans()
                descripcion = generar_descripcion_jeans()
                # Precio: 30-110
                precio_base = random.choice([30, 40, 50, 60, 70, 80, 90, 100, 110])
            else:  # Jackets
                nombre = generar_nombre_jacket()
                descripcion = generar_descripcion_jacket()
                # Precio: 40-250
                precio_base = random.choice([40, 50, 60, 70, 80, 90, 100, 120, 150, 180, 200, 250])
            
            # Calcular mes de creación con estacionalidad
            estacionalidad_cat = ESTACIONALIDAD[categoria_nombre]
            
            # Ponderación de meses según estacionalidad
            meses_ponderados = []
            max_mes = 11 if año == 2025 else 12  # 2025: solo hasta noviembre
            
            for mes in range(1, max_mes + 1):
                peso = int(estacionalidad_cat[mes] * 10)
                meses_ponderados.extend([mes] * peso)
            
            mes_creacion = random.choice(meses_ponderados)
            fecha_creacion = generar_fecha_realista(año, mes_creacion, categoria_nombre)
            
            marca = random.choice(marcas)
            color = random.choice(COLORES)
            material = random.choice(TIPOS_TELA)
            
            # 40% destacadas, 30% novedades
            destacada = random.random() < 0.4
            es_novedad = random.random() < 0.3
            
            prenda = Prenda.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=Decimal(str(precio_base)),
                marca=marca,
                color=color,
                material=material,
                activa=True,
                destacada=destacada,
                es_novedad=es_novedad
            )
            
            # Forzar fecha de creación
            Prenda.objects.filter(id=prenda.id).update(created_at=fecha_creacion)
            prenda.refresh_from_db()
            
            # Asignar categoría
            prenda.categorias.add(categoria)
            
            # Asignar tallas (3-6 tallas por prenda)
            num_tallas = random.randint(3, 6)
            tallas_seleccionadas = random.sample(tallas, num_tallas)
            prenda.tallas_disponibles.set(tallas_seleccionadas)
            
            # Crear stock para cada talla
            for talla in tallas_seleccionadas:
                cantidad_stock = random.randint(5, 50)
                StockPrenda.objects.create(
                    prenda=prenda,
                    talla=talla,
                    cantidad=cantidad_stock,
                    stock_minimo=5
                )
            
            # Asignar imagen
            if categoria_nombre == 'Blusas' and imagenes_blusas:
                if idx_imagen_blusa < len(imagenes_blusas):
                    imagen_url = imagenes_blusas[idx_imagen_blusa]
                    idx_imagen_blusa += 1
                else:
                    # Si se acabaron las imágenes, usar la imagen de categoría
                    imagen_url = imagen_default.get(categoria_nombre, '')
            else:
                imagen_url = imagen_default.get(categoria_nombre, '')
            
            if imagen_url:
                ImagenPrendaURL.objects.create(
                    prenda=prenda,
                    imagen_url=imagen_url,
                    es_principal=True,
                    orden=1,
                    alt_text=nombre
                )
            
            prendas_creadas.append(prenda)
        
        print(f"  {Colors.OK}✓{Colors.END} {cantidad} prendas de {categoria_nombre} creadas")
    
    print(f"\n{Colors.OK}✅ Total: {len(prendas_creadas)} prendas creadas para {año}{Colors.END}")
    return prendas_creadas

def seed_direcciones(clientes):
    """Crear 1-3 direcciones por cliente"""
    print_header(f"📍 CREANDO DIRECCIONES")
    
    direcciones = []
    for cliente in clientes:
        num_direcciones = random.randint(1, 3)
        
        for i in range(num_direcciones):
            direccion = Direccion.objects.create(
                usuario=cliente,
                nombre_completo=f"{cliente.nombre} {cliente.apellido}",
                telefono=cliente.telefono or f"+591 {random.randint(60000000, 79999999)}",
                direccion_linea1=fake.street_address(),
                direccion_linea2=fake.secondary_address() if random.random() > 0.5 else '',
                ciudad=fake.city(),
                departamento=random.choice(DEPARTAMENTOS_BOLIVIA),
                codigo_postal=fake.postcode(),
                pais='Bolivia',
                referencia=fake.sentence() if random.random() > 0.6 else '',
                es_principal=(i == 0),
                activa=True
            )
            direcciones.append(direccion)
    
    print(f"{Colors.OK}✅ {len(direcciones)} direcciones creadas{Colors.END}")
    return direcciones

def seed_favoritos(clientes, prendas):
    """Crear favoritos aleatorios"""
    print_header(f"❤️ CREANDO FAVORITOS")
    
    favoritos = []
    for cliente in random.sample(clientes, min(300, len(clientes))):
        num_favoritos = random.randint(1, 15)
        prendas_fav = random.sample(prendas, min(num_favoritos, len(prendas)))
        
        for prenda in prendas_fav:
            fav, created = Favoritos.objects.get_or_create(
                usuario=cliente,
                prenda=prenda
            )
            if created:
                favoritos.append(fav)
    
    print(f"{Colors.OK}✅ {len(favoritos)} favoritos creados{Colors.END}")
    return favoritos

def seed_metodos_pago():
    """Crear métodos de pago"""
    print_header("💳 CREANDO MÉTODOS DE PAGO")
    
    metodos = [
        {'codigo': 'efectivo', 'nombre': 'Efectivo', 'descripcion': 'Pago en efectivo contra entrega'},
        {'codigo': 'tarjeta', 'nombre': 'Tarjeta de Crédito/Débito', 'descripcion': 'Pago con tarjeta'},
        {'codigo': 'transferencia', 'nombre': 'Transferencia Bancaria', 'descripcion': 'Transferencia directa'},
        {'codigo': 'qr', 'nombre': 'QR Simple/Tigo Money', 'descripcion': 'Pago mediante código QR'},
    ]
    
    metodos_creados = []
    for m in metodos:
        metodo, created = MetodoPago.objects.get_or_create(
            codigo=m['codigo'],
            defaults={
                'nombre': m['nombre'],
                'descripcion': m['descripcion'],
                'activo': True
            }
        )
        metodos_creados.append(metodo)
    
    print(f"{Colors.OK}✅ {len(metodos_creados)} métodos de pago creados{Colors.END}")
    return metodos_creados

def seed_pedidos_por_año(año, clientes, prendas_año, metodos_pago):
    """
    Crear ~1000-1200 pedidos para un año específico
    Cada cliente mínimo 1 pedido
    
    ⚠️  IMPORTANTE: Para 2025, solo genera pedidos hasta el 11 de Noviembre
    """
    print_header(f"🛒 CREANDO PEDIDOS PARA {año}")
    
    # Calcular número de pedidos para el año
    if año == 2023:
        num_pedidos = 1000
    elif año == 2024:
        num_pedidos = 1100
    else:  # 2025
        num_pedidos = 1200
    
    # Filtrar clientes que ya existían en ese año
    clientes_disponibles = [
        c for c in clientes
        if c.created_at.year <= año
    ]
    
    if not clientes_disponibles:
        print(f"{Colors.WARN}⚠️ No hay clientes disponibles para {año}{Colors.END}")
        return []
    
    # Asegurar que todos los clientes tengan al menos 1 pedido
    clientes_con_pedido = set()
    pedidos = []
    
    estados_posibles = ['completado', 'enviado', 'entregado']
    
    for i in range(num_pedidos):
        # Seleccionar cliente
        if len(clientes_con_pedido) < len(clientes_disponibles):
            # Asignar a cliente sin pedido
            cliente = random.choice([c for c in clientes_disponibles if c.id not in clientes_con_pedido])
        else:
            # Cliente aleatorio
            cliente = random.choice(clientes_disponibles)
        
        clientes_con_pedido.add(cliente.id)
        
        # Dirección del cliente
        direccion = Direccion.objects.filter(usuario=cliente).first()
        if not direccion:
            # Crear dirección si no tiene
            direccion = Direccion.objects.create(
                usuario=cliente,
                nombre_completo=f"{cliente.nombre} {cliente.apellido}",
                telefono=cliente.telefono or f"+591 {random.randint(60000000, 79999999)}",
                direccion_linea1=fake.street_address(),
                ciudad=fake.city(),
                departamento=random.choice(DEPARTAMENTOS_BOLIVIA),
                pais='Bolivia',
                es_principal=True,
                activa=True
            )
        
        # Seleccionar mes con estacionalidad global
        # (Noviembre y Diciembre con más peso, excepto para 2025)
        if año == 2025:
            # 2025: Solo enero-noviembre (11 meses)
            # Dar más peso a los últimos meses disponibles (Sep-Nov)
            meses_ponderados = list(range(1, 12))  # 1-11
            meses_ponderados.extend([9, 9, 10, 10, 11, 11, 11, 11])  # Más ventas en Sep-Nov
        else:
            # 2023-2024: Todo el año (12 meses)
            meses_ponderados = list(range(1, 13))
            meses_ponderados.extend([11, 11, 12, 12])  # Más ventas en Nov-Dic
        
        mes_pedido = random.choice(meses_ponderados)
        
        fecha_pedido = generar_fecha_realista(año, mes_pedido, 'Blusas')
        
        # Filtrar prendas creadas antes de la fecha del pedido
        prendas_disponibles = [
            p for p in prendas_año
            if p.created_at <= fecha_pedido
        ]
        
        if not prendas_disponibles:
            continue
        
        # Número de items en el pedido (1-5)
        num_items = random.randint(1, 5)
        prendas_pedido = random.sample(prendas_disponibles, min(num_items, len(prendas_disponibles)))
        
        # Crear pedido
        subtotal = Decimal('0')
        
        pedido = Pedido.objects.create(
            usuario=cliente,
            direccion_envio=direccion,
            subtotal=Decimal('0'),  # Se calculará después
            descuento=Decimal('0'),
            costo_envio=Decimal('0'),
            total=Decimal('0'),
            estado=random.choice(estados_posibles),
            notas_cliente=random.choice(NOTAS_PLANTILLAS)
        )
        
        # Forzar fecha
        Pedido.objects.filter(id=pedido.id).update(created_at=fecha_pedido)
        pedido.refresh_from_db()
        
        # Crear detalles
        for prenda in prendas_pedido:
            talla = random.choice(list(prenda.tallas_disponibles.all()))
            cantidad = random.randint(1, 3)
            precio_unitario = prenda.precio
            subtotal_item = precio_unitario * cantidad
            
            DetallePedido.objects.create(
                pedido=pedido,
                prenda=prenda,
                talla=talla,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal_item
            )
            
            subtotal += subtotal_item
        
        # Actualizar totales del pedido
        pedido.subtotal = subtotal
        pedido.total = subtotal
        pedido.save(update_fields=['subtotal', 'total'])
        
        # Crear pago
        metodo = random.choice(metodos_pago)
        Pago.objects.create(
            pedido=pedido,
            metodo_pago=metodo,
            monto=pedido.total,
            estado='completado'
        )
        
        pedidos.append(pedido)
        
        if (i + 1) % 200 == 0:
            print_progress(i + 1, num_pedidos, f"{i+1} pedidos creados")
    
    print(f"{Colors.OK}✅ {len(pedidos)} pedidos creados para {año}{Colors.END}")
    return pedidos

def seed_carritos(clientes, prendas):
    """Crear carritos para los primeros 100 clientes con 2-10 items"""
    print_header(f"🛒 CREANDO CARRITOS (PRIMEROS 100 CLIENTES)")
    
    clientes_con_carrito = clientes[:100]
    carritos = []
    
    for cliente in clientes_con_carrito:
        # Crear o obtener carrito
        carrito, created = Carrito.objects.get_or_create(usuario=cliente)
        
        # Número de items (2-10)
        num_items = random.randint(2, 10)
        prendas_carrito = random.sample(prendas, min(num_items, len(prendas)))
        
        for prenda in prendas_carrito:
            if prenda.tallas_disponibles.exists():
                talla = random.choice(list(prenda.tallas_disponibles.all()))
                cantidad = random.randint(1, 3)
                
                ItemCarrito.objects.create(
                    carrito=carrito,
                    prenda=prenda,
                    talla=talla,
                    cantidad=cantidad,
                    precio_unitario=prenda.precio
                )
        
        carritos.append(carrito)
    
    print(f"{Colors.OK}✅ {len(carritos)} carritos creados con items{Colors.END}")
    return carritos

# ============= MAIN =============

@transaction.atomic
def run():
    """Ejecutar todo el seeding"""
    print_header("🌱 SUPER SEEDER V2 - INICIO")
    print(f"{Colors.CYAN}Generando datos de 3 años (2023-2025) con estacionalidad realista{Colors.END}\n")
    
    inicio = datetime.now()
    
    # Contadores
    stats = {
        'permisos': 0,
        'roles': 0,
        'usuarios_principales': 0,
        'clientes': 0,
        'categorias': 0,
        'tallas': 0,
        'marcas': 0,
        'prendas_2023': 0,
        'prendas_2024': 0,
        'prendas_2025': 0,
        'direcciones': 0,
        'favoritos': 0,
        'metodos_pago': 0,
        'pedidos_2023': 0,
        'pedidos_2024': 0,
        'pedidos_2025': 0,
        'carritos': 0
    }
    
    # 1. Permisos y Roles
    all_permissions = seed_permissions()
    stats['permisos'] = all_permissions.count()
    
    all_roles = seed_roles(all_permissions)
    stats['roles'] = all_roles.count()
    
    # 2. Usuarios
    usuarios_principales = seed_usuarios_principales()
    stats['usuarios_principales'] = len(usuarios_principales)
    
    clientes = seed_clientes(1000)
    stats['clientes'] = len(clientes)
    
    # 3. Productos - Estructura base
    categorias_list = seed_categorias()
    categorias_dict = {cat.nombre: cat for cat in categorias_list}
    stats['categorias'] = len(categorias_list)
    
    tallas = seed_tallas()
    stats['tallas'] = len(tallas)
    
    marcas = seed_marcas()
    stats['marcas'] = len(marcas)
    
    # 4. Prendas por año (con estacionalidad)
    prendas_2023 = seed_prendas_por_año(2023, categorias_dict, marcas, tallas)
    stats['prendas_2023'] = len(prendas_2023)
    
    prendas_2024 = seed_prendas_por_año(2024, categorias_dict, marcas, tallas)
    stats['prendas_2024'] = len(prendas_2024)
    
    prendas_2025 = seed_prendas_por_año(2025, categorias_dict, marcas, tallas)
    stats['prendas_2025'] = len(prendas_2025)
    
    todas_las_prendas = prendas_2023 + prendas_2024 + prendas_2025
    
    # 5. Direcciones y Favoritos
    direcciones = seed_direcciones(clientes)
    stats['direcciones'] = len(direcciones)
    
    favoritos = seed_favoritos(clientes, todas_las_prendas)
    stats['favoritos'] = len(favoritos)
    
    # 6. Métodos de pago
    metodos_pago = seed_metodos_pago()
    stats['metodos_pago'] = len(metodos_pago)
    
    # 7. Pedidos por año
    pedidos_2023 = seed_pedidos_por_año(2023, clientes, prendas_2023, metodos_pago)
    stats['pedidos_2023'] = len(pedidos_2023)
    
    pedidos_2024 = seed_pedidos_por_año(2024, clientes, prendas_2023 + prendas_2024, metodos_pago)
    stats['pedidos_2024'] = len(pedidos_2024)
    
    pedidos_2025 = seed_pedidos_por_año(2025, clientes, todas_las_prendas, metodos_pago)
    stats['pedidos_2025'] = len(pedidos_2025)
    
    # 8. Carritos
    carritos = seed_carritos(clientes, todas_las_prendas)
    stats['carritos'] = len(carritos)
    
    # ============= RESUMEN FINAL =============
    print_header("📊 RESUMEN FINAL DE DATOS CREADOS")
    
    print(f"\n{Colors.BOLD}👥 USUARIOS:{Colors.END}")
    print(f"  ├─ Permisos:              {stats['permisos']:>6}")
    print(f"  ├─ Roles:                 {stats['roles']:>6}")
    print(f"  ├─ Admin + Empleados:     {stats['usuarios_principales']:>6}")
    print(f"  └─ Clientes:              {stats['clientes']:>6}")
    
    print(f"\n{Colors.BOLD}📦 PRODUCTOS:{Colors.END}")
    print(f"  ├─ Categorías:            {stats['categorias']:>6}")
    print(f"  ├─ Tallas:                {stats['tallas']:>6}")
    print(f"  ├─ Marcas:                {stats['marcas']:>6}")
    print(f"  ├─ Prendas 2023:          {stats['prendas_2023']:>6}")
    print(f"  ├─ Prendas 2024:          {stats['prendas_2024']:>6}")
    print(f"  ├─ Prendas 2025:          {stats['prendas_2025']:>6}")
    print(f"  └─ {Colors.BOLD}Total Prendas:         {stats['prendas_2023'] + stats['prendas_2024'] + stats['prendas_2025']:>6}{Colors.END}")
    
    print(f"\n{Colors.BOLD}🏠 CLIENTES:{Colors.END}")
    print(f"  ├─ Direcciones:           {stats['direcciones']:>6}")
    print(f"  ├─ Favoritos:             {stats['favoritos']:>6}")
    print(f"  └─ Carritos activos:      {stats['carritos']:>6}")
    
    print(f"\n{Colors.BOLD}🛒 PEDIDOS:{Colors.END}")
    print(f"  ├─ Métodos de pago:       {stats['metodos_pago']:>6}")
    print(f"  ├─ Pedidos 2023:          {stats['pedidos_2023']:>6}")
    print(f"  ├─ Pedidos 2024:          {stats['pedidos_2024']:>6}")
    print(f"  ├─ Pedidos 2025:          {stats['pedidos_2025']:>6}")
    print(f"  └─ {Colors.BOLD}Total Pedidos:         {stats['pedidos_2023'] + stats['pedidos_2024'] + stats['pedidos_2025']:>6}{Colors.END}")
    
    # Calcular totales generales
    total_registros = sum(stats.values())
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.OK}{Colors.BOLD}TOTAL DE REGISTROS CREADOS: {total_registros:,}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    
    fin = datetime.now()
    duracion = (fin - inicio).total_seconds()
    
    print(f"\n{Colors.CYAN}⏱️  Tiempo de ejecución: {duracion:.2f} segundos{Colors.END}")
    print(f"{Colors.OK}✅ ¡SEEDING COMPLETADO EXITOSAMENTE!{Colors.END}\n")

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ ERROR: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
