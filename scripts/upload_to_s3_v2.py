#!/usr/bin/env python3
"""
Script mejorado para subir dataset completo a S3
- Lee del dataset local
- Genera URLs automáticamente
- Crea categorías y marcas automáticamente
- Guarda metadatos en BD
- Crea stock por talla

Uso:
    # Análisis previo
    python scripts/analyze_dataset.py
    
    # Prueba piloto (100 imágenes)
    python scripts/upload_to_s3_v2.py --max-imagenes 100 --lote-size 50
    
    # Subida completa (2500 imágenes)
    python scripts/upload_to_s3_v2.py --max-imagenes 2500 --lote-size 100
    
    # Con verbose mode
    python scripts/upload_to_s3_v2.py --max-imagenes 500 --verbose
"""

import os
import sys
import json
import time
import hashlib
import random
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import re

# Django setup (ANTES de importaciones)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

import django
django.setup()

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("❌ ERROR: boto3 no está instalado")
    print("   Ejecuta: pip install boto3")
    sys.exit(1)

from decouple import config
from django.utils.text import slugify

from apps.products.models import Categoria, Marca, Talla, Prenda, StockPrenda, ImagenPrenda

# Configuración
DATASET_PATH = r"D:\1NATALY\SISTEMAS DE INFORMACIÓN II\nuevo GESTION_DOCUMENTAL\smartsales\clothes"

CATEGORIAS_MAPPING = {
    'dress': 'Vestidos',
    'gown': 'Vestidos',
    'vestido': 'Vestidos',
    'shirt': 'Blusas',
    'blouse': 'Blusas',
    'top': 'Blusas',
    'tshirt': 'Blusas',
    'camisa': 'Blusas',
    'pants': 'Pantalones',
    'trouser': 'Pantalones',
    'jeans': 'Pantalones',
    'pantalon': 'Pantalones',
    'skirt': 'Faldas',
    'falda': 'Faldas',
    'jacket': 'Chaquetas',
    'coat': 'Chaquetas',
    'chaqueta': 'Chaquetas',
    'sweater': 'Suéteres',
    'jumper': 'Suéteres',
    'sueter': 'Suéteres',
    'shoe': 'Zapatos',
    'boot': 'Zapatos',
    'sandal': 'Zapatos',
    'zapato': 'Zapatos',
}

MARCAS_DISPONIBLES = [
    'Nike', 'Adidas', 'Zara', 'H&M', 'Forever 21',
    'Calvin Klein', 'Gucci', 'Prada', 'Louis Vuitton',
    'Tommy Hilfiger', 'Ralph Lauren', 'Gap', 'C&A',
    'Hollister', 'Abercrombie', 'ASOS', 'Uniqlo', 'Mango',
    'Shein', 'Urban Outfitters', 'Vintage Store',
]

COLORES_DISPONIBLES = [
    'Negro', 'Blanco', 'Gris', 'Rojo', 'Azul', 'Verde',
    'Amarillo', 'Naranja', 'Rosa', 'Púrpura', 'Marrón', 'Beige',
    'Marfil', 'Turquesa', 'Coral', 'Champagne', 'Marino', 'Burdeos',
]

RANGOS_PRECIO = {
    'Vestidos': (30, 85),
    'Blusas': (15, 50),
    'Pantalones': (25, 75),
    'Faldas': (20, 65),
    'Chaquetas': (50, 160),
    'Suéteres': (20, 70),
    'Zapatos': (40, 130),
    'Otros': (20, 60),
}

TALLAS = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

# Colores ANSI para terminal
class Colors:
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


class S3UploaderV2:
    """Uploader mejorado para dataset completo"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.bucket_name = config('AWS_STORAGE_BUCKET_NAME')
        self.region = config('AWS_S3_REGION_NAME', default='us-east-1')

        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY')
            )
            # Verificar conexión
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"{Colors.OK}✅ Conectado a S3:{Colors.END} {self.bucket_name} ({self.region})")
        except Exception as e:
            print(f"{Colors.FAIL}❌ ERROR de conexión a S3:{Colors.END} {e}")
            sys.exit(1)

        self.categorias_creadas = {}
        self.marcas_creadas = {}
        self.productos_creados = []
        self.estadisticas = {
            'imagenes_subidas': 0,
            'productos_creados': 0,
            'imagenes_fallidas': 0,
            'tiempo_inicio': datetime.now(),
        }

    def obtener_categoria_desde_nombre(self, nombre_archivo: str) -> str:
        """Extrae categoría del nombre del archivo"""
        nombre_lower = nombre_archivo.lower()

        for palabra_clave, categoria in CATEGORIAS_MAPPING.items():
            if palabra_clave in nombre_lower:
                return categoria

        return 'Otros'

    def obtener_marca_consistente(self, nombre_prenda: str) -> str:
        """Asigna marca consistente basada en hash del nombre"""
        hash_val = int(hashlib.md5(nombre_prenda.encode()).hexdigest(), 16)
        indice = hash_val % len(MARCAS_DISPONIBLES)
        return MARCAS_DISPONIBLES[indice]

    def obtener_color_consistente(self, nombre_prenda: str) -> str:
        """Asigna color consistente basada en hash del nombre"""
        hash_val = int(hashlib.md5(nombre_prenda.encode()).hexdigest(), 16)
        indice = hash_val % len(COLORES_DISPONIBLES)
        return COLORES_DISPONIBLES[indice]

    def generar_precio(self, categoria: str) -> float:
        """Genera precio basado en rango de categoría"""
        rango = RANGOS_PRECIO.get(categoria, (20, 100))
        precio = round(random.uniform(rango[0], rango[1]), 2)
        return precio

    def upload_image_to_s3(self, local_path: str, s3_key: str) -> Tuple[bool, str]:
        """Sube imagen individual a S3"""
        try:
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(local_path),
                    'Metadata': {
                        'uploaded_at': datetime.now().isoformat(),
                    }
                }
            )

            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            return True, url

        except ClientError as e:
            if self.verbose:
                print(f"{Colors.FAIL}    Error S3:{Colors.END} {e}")
            return False, ""

    @staticmethod
    def _get_content_type(file_path: str) -> str:
        """Determina MIME type"""
        ext = Path(file_path).suffix.lower()
        tipos = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp'
        }
        return tipos.get(ext, 'image/jpeg')

    def crear_categoria_si_no_existe(self, nombre: str) -> Categoria:
        """Crea categoría en BD si no existe"""
        if nombre in self.categorias_creadas:
            return self.categorias_creadas[nombre]

        categoria, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': f'Ropa y prendas de {nombre.lower()}',
                'activa': True
            }
        )

        self.categorias_creadas[nombre] = categoria
        if created and self.verbose:
            print(f"    {Colors.OK}✅{Colors.END} Categoría creada: {nombre}")

        return categoria

    def crear_marca_si_no_existe(self, nombre: str) -> Marca:
        """Crea marca en BD si no existe"""
        if nombre in self.marcas_creadas:
            return self.marcas_creadas[nombre]

        marca, created = Marca.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': f'{nombre} - Ropa y accesorios de moda',
                'activa': True
            }
        )

        self.marcas_creadas[nombre] = marca
        if created and self.verbose:
            print(f"    {Colors.OK}✅{Colors.END} Marca creada: {nombre}")

        return marca

    def crear_tallas_si_no_existen(self):
        """Crea tallas en BD si no existen"""
        for orden, talla_nombre in enumerate(TALLAS, 1):
            Talla.objects.get_or_create(
                nombre=talla_nombre,
                defaults={'orden': orden}
            )

    def crear_producto_desde_imagen(self, nombre_archivo: str, url_s3: str) -> Tuple[Prenda, bool]:
        """Crea producto en BD desde imagen"""

        # Información del producto
        categoria_nombre = self.obtener_categoria_desde_nombre(nombre_archivo)
        categoria = self.crear_categoria_si_no_existe(categoria_nombre)

        marca_nombre = self.obtener_marca_consistente(nombre_archivo)
        marca = self.crear_marca_si_no_existe(marca_nombre)

        color = self.obtener_color_consistente(nombre_archivo)
        precio = self.generar_precio(categoria_nombre)

        # Crear nombre de producto
        nombre_limpio = Path(nombre_archivo).stem.replace('_', ' ').replace('-', ' ').title()
        nombre_prenda = f"{nombre_limpio} - {color}"

        # Crear prenda
        prenda, created = Prenda.objects.get_or_create(
            nombre=nombre_prenda,
            marca=marca,
            color=color,
            defaults={
                'descripcion': f'{nombre_limpio} en {color} de la marca {marca_nombre}. Ropa de calidad con estilo.',
                'precio': precio,
                'material': 'Algodón/Poliéster',
                'activa': True,
            }
        )

        if created:
            try:
                # Asignar categoría
                prenda.categorias.add(categoria)

                # Asignar tallas disponibles
                prenda.tallas_disponibles.set(Talla.objects.all())

                # Crear imagen
                ImagenPrenda.objects.create(
                    prenda=prenda,
                    imagen=url_s3,
                    es_principal=True,
                    orden=0,
                    alt_text=f"{nombre_prenda} - Imagen principal"
                )

                # Crear stock para cada talla
                for talla in Talla.objects.all():
                    stock_cantidad = random.randint(3, 50)
                    StockPrenda.objects.create(
                        prenda=prenda,
                        talla=talla,
                        cantidad=stock_cantidad,
                        stock_minimo=3
                    )

                self.productos_creados.append(prenda)
                return prenda, True
            except Exception as e:
                if self.verbose:
                    print(f"    {Colors.FAIL}Error creando producto:{Colors.END} {e}")
                return prenda, False

        return prenda, False

    def upload_dataset_completo(self, max_imagenes: int = 2500, lote_size: int = 100):
        """Sube dataset completo a S3"""

        dataset_dir = Path(DATASET_PATH)

        # Verificar que la carpeta existe
        if not dataset_dir.exists():
            print(f"{Colors.FAIL}❌ ERROR:{Colors.END} No se encuentra {DATASET_PATH}")
            sys.exit(1)

        extensiones_validas = {'.jpg', '.jpeg', '.png', '.webp'}

        # Obtener todas las imágenes
        imagenes = sorted([
            f for f in dataset_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensiones_validas
        ])[:max_imagenes]

        if not imagenes:
            print(f"{Colors.FAIL}❌ ERROR:{Colors.END} No se encontraron imágenes en {DATASET_PATH}")
            sys.exit(1)

        print(f"\n{Colors.HEADER}{Colors.BOLD}📦 INICIANDO UPLOAD DE DATASET{Colors.END}")
        print(f"{Colors.HEADER}{'='*80}{Colors.END}")
        print(f"  {Colors.BOLD}Total de imágenes a procesar:{Colors.END} {len(imagenes)}")
        print(f"  {Colors.BOLD}Bucket S3:{Colors.END} {self.bucket_name}")
        print(f"  {Colors.BOLD}Región:{Colors.END} {self.region}")
        print(f"  {Colors.BOLD}Tamaño de lote:{Colors.END} {lote_size}")
        print(f"  {Colors.BOLD}Modo:{Colors.END} {'Verbose' if self.verbose else 'Normal'}")
        print(f"{Colors.HEADER}{'='*80}{Colors.END}\n")

        # Crear tallas primero
        self.crear_tallas_si_no_existen()

        # Variables de control
        imagenes_subidas = 0
        productos_creados = 0
        imagenes_fallidas = 0

        # Procesar en lotes
        num_lotes = (len(imagenes) + lote_size - 1) // lote_size

        for lote_num in range(1, num_lotes + 1):
            inicio = (lote_num - 1) * lote_size
            fin = min(lote_num * lote_size, len(imagenes))
            lote = imagenes[inicio:fin]

            print(f"{Colors.CYAN}📂 LOTE {lote_num}/{num_lotes}:{Colors.END} Procesando {len(lote)} imágenes ({inicio+1}-{fin})")

            for idx, imagen_path in enumerate(lote, 1):
                nombre_archivo = imagen_path.name
                categoria = self.obtener_categoria_desde_nombre(nombre_archivo)

                # Generar key de S3
                s3_key = f"productos/{categoria}/{nombre_archivo}"

                # Mostrar progreso
                print(f"  [{idx:3}/{len(lote)}] {nombre_archivo:45}", end='', flush=True)

                # Subir imagen
                exito, url_s3 = self.upload_image_to_s3(str(imagen_path), s3_key)

                if exito:
                    # Crear producto
                    prenda, creada = self.crear_producto_desde_imagen(nombre_archivo, url_s3)

                    if creada:
                        print(f" {Colors.OK}✅{Colors.END} (nuevo)")
                        productos_creados += 1
                    else:
                        print(f" {Colors.WARN}⚠️ {Colors.END} (existente)")

                    imagenes_subidas += 1
                else:
                    print(f" {Colors.FAIL}❌{Colors.END}")
                    imagenes_fallidas += 1

            # Mostrar resumen de lote
            print(f"{Colors.CYAN}  {'-'*75}{Colors.END}")
            print(f"  Resumen: {imagenes_subidas}↑ subidas, {productos_creados}✓ productos, {imagenes_fallidas}✗ fallidas\n")

        # Resumen final
        tiempo_transcurrido = (datetime.now() - self.estadisticas['tiempo_inicio']).total_seconds()
        minutos = int(tiempo_transcurrido // 60)
        segundos = int(tiempo_transcurrido % 60)

        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.OK}{Colors.BOLD}✅ PROCESO COMPLETADO{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")

        print(f"\n{Colors.BOLD}📊 ESTADÍSTICAS FINALES:{Colors.END}")
        print(f"  • Imágenes subidas a S3: {Colors.OK}{imagenes_subidas}{Colors.END}")
        print(f"  • Productos creados en BD: {Colors.OK}{productos_creados}{Colors.END}")
        print(f"  • Imágenes fallidas: {Colors.FAIL if imagenes_fallidas > 0 else Colors.OK}{imagenes_fallidas}{Colors.END}")
        print(f"  • Tiempo total: {minutos}m {segundos}s")
        print(f"  • Bucket S3: {self.bucket_name}")

        # Contar productos por categoría
        print(f"\n{Colors.BOLD}📁 DISTRIBUCIÓN POR CATEGORÍA:{Colors.END}")
        for categoria_obj in Categoria.objects.filter(activa=True).order_by('nombre'):
            count = categoria_obj.prendas.filter(activa=True).count()
            if count > 0:
                print(f"  • {categoria_obj.nombre:20} : {Colors.BLUE}{count:5} prendas{Colors.END}")

        # Contar marcas
        total_marcas = Marca.objects.filter(activa=True).count()
        print(f"\n{Colors.BOLD}🏷️  MARCAS CREADAS:{Colors.END} {Colors.BLUE}{total_marcas}{Colors.END}")

        print(f"\n{Colors.OK}✨ Dataset cargado exitosamente en {self.bucket_name}{Colors.END}")
        print(f"\n{Colors.BOLD}📋 PRÓXIMOS PASOS:{Colors.END}")
        print(f"  1. Verificar productos en admin: http://52.0.69.138/api/admin/")
        print(f"  2. Ver frontend: http://52.0.69.138")
        print(f"  3. Ver API: http://52.0.69.138/api/docs\n")


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Subir dataset completo a S3 y crear productos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Análisis previo (sin subir)
  python scripts/analyze_dataset.py

  # Prueba piloto (100 imágenes)
  python scripts/upload_to_s3_v2.py --max-imagenes 100 --lote-size 50

  # Subida completa (2500 imágenes)
  python scripts/upload_to_s3_v2.py --max-imagenes 2500 --lote-size 100

  # Modo verbose (más detalles)
  python scripts/upload_to_s3_v2.py --max-imagenes 500 --verbose
        """
    )
    parser.add_argument('--max-imagenes', type=int, default=2500,
                        help='Máximo número de imágenes a subir (default: 2500)')
    parser.add_argument('--lote-size', type=int, default=100,
                        help='Tamaño del lote de procesamiento (default: 100)')
    parser.add_argument('--verbose', action='store_true',
                        help='Modo verbose - más detalles')

    args = parser.parse_args()

    # Validaciones
    if args.max_imagenes < 1:
        print(f"{Colors.FAIL}❌ ERROR:{Colors.END} --max-imagenes debe ser mayor a 0")
        sys.exit(1)

    if args.lote_size < 1:
        print(f"{Colors.FAIL}❌ ERROR:{Colors.END} --lote-size debe ser mayor a 0")
        sys.exit(1)

    uploader = S3UploaderV2(verbose=args.verbose)

    try:
        uploader.upload_dataset_completo(
            max_imagenes=args.max_imagenes,
            lote_size=args.lote_size
        )
    except KeyboardInterrupt:
        print(f"\n{Colors.WARN}⚠️ Proceso interrumpido por el usuario{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR:{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
