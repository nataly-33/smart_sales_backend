#!/usr/bin/env python3
"""
Script SOLO para subir imágenes a S3 (sin crear seeder)
- Lee imágenes del dataset local
- Sube a S3 con nombres ordenados (000001_1.jpg, 000001_2.jpg, etc.)
- NO crea productos en BD

Uso:
    # Subida de primeras 2500 imágenes
    python scripts/upload_imagenes_s3.py --max-imagenes 2500 --images-per-product 3
    
    # Prueba con 100 imágenes
    python scripts/upload_imagenes_s3.py --max-imagenes 100 --images-per-product 3
    
    # Con verbose mode
    python scripts/upload_imagenes_s3.py --max-imagenes 500 --verbose
"""

import os
import sys
import time
from pathlib import Path
from typing import Tuple
from datetime import datetime

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
    print("❌ ERROR: boto3 no está instalado")
    print("   Ejecuta: pip install boto3")
    sys.exit(1)

from decouple import config

# Configuración
DATASET_PATH = r"D:\1NATALY\SISTEMAS DE INFORMACIÓN II\nuevo GESTION_DOCUMENTAL\smartsales\clothes\clothes"

# Colores ANSI
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
    print(f"{Colors.HEADER}{Colors.BOLD}{texto}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")


def print_progress(paso, total, texto):
    pct = (paso / total * 100)
    bar_length = 40
    filled = int(bar_length * paso // total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"  {Colors.CYAN}[{bar}] {pct:5.1f}% ({paso:4}/{total}){Colors.END} {texto}")


class S3ImageUploader:
    """Uploader SOLO de imágenes a S3"""

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

        self.estadisticas = {
            'imagenes_subidas': 0,
            'imagenes_fallidas': 0,
            'tiempo_inicio': datetime.now(),
            'urls_generadas': []
        }

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

    def upload_image_to_s3(self, local_path: str, s3_key: str) -> Tuple[bool, str]:
        """Sube una imagen a S3 y retorna (éxito, URL)"""
        try:
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(local_path),
                    'ACL': 'public-read',
                    'Metadata': {
                        'uploaded_at': datetime.now().isoformat(),
                    }
                }
            )

            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            return True, url

        except ClientError as e:
            if self.verbose:
                print(f"\n      {Colors.FAIL}Error S3:{Colors.END} {e}")
            return False, ""

    def upload_images_batch(self, max_imagenes: int = 2500, images_per_product: int = 3):
        """
        Sube imágenes a S3 con nombres ordenados
        
        Estructura:
        - productos/Blusas/000001_1.jpg, 000001_2.jpg, 000001_3.jpg
        - productos/Blusas/000002_1.jpg, 000002_2.jpg, 000002_3.jpg
        ...
        """

        dataset_dir = Path(DATASET_PATH)

        # Verificar que la carpeta existe
        if not dataset_dir.exists():
            print(f"{Colors.FAIL}❌ ERROR:{Colors.END} No se encuentra {DATASET_PATH}")
            sys.exit(1)

        extensiones_validas = {'.jpg', '.jpeg', '.png', '.webp'}

        # Obtener todas las imágenes (ordenadas)
        todas_imagenes = sorted([
            f for f in dataset_dir.iterdir()
            if f.is_file() and f.suffix.lower() in extensiones_validas
        ])

        if not todas_imagenes:
            print(f"{Colors.FAIL}❌ ERROR:{Colors.END} No se encontraron imágenes en {DATASET_PATH}")
            sys.exit(1)

        # Limitar a max_imagenes
        total_a_subir = min(max_imagenes, len(todas_imagenes))
        print(f"\n{Colors.HEADER}{Colors.BOLD}📸 UPLOAD DE IMÁGENES A S3{Colors.END}")
        print(f"  {Colors.BOLD}Total de imágenes a procesar:{Colors.END} {total_a_subir}")
        print(f"  {Colors.BOLD}Imágenes disponibles en disco:{Colors.END} {len(todas_imagenes)}")
        print(f"  {Colors.BOLD}Imágenes por producto:{Colors.END} {images_per_product}")
        print(f"  {Colors.BOLD}Productos que se crearán:{Colors.END} {(total_a_subir + images_per_product - 1) // images_per_product}")
        print(f"  {Colors.BOLD}Bucket S3:{Colors.END} {self.bucket_name}")
        print(f"  {Colors.BOLD}Región:{Colors.END} {self.region}\n")

        imagenes_a_procesar = todas_imagenes[:total_a_subir]

        # Variables de control
        imagenes_subidas = 0
        imagenes_fallidas = 0
        producto_num = 1
        imagen_num = 1

        print(f"{Colors.CYAN}{'='*80}{Colors.END}\n")

        for idx, imagen_path in enumerate(imagenes_a_procesar, 1):
            # Mostrar progreso
            if idx % 5 == 0 or idx == len(imagenes_a_procesar):
                print_progress(idx, len(imagenes_a_procesar), f"Subiendo...")

            # Generar nombre ordenado para la imagen
            # 000001_1.jpg, 000001_2.jpg, 000001_3.jpg, 000002_1.jpg, ...
            s3_key = f"productos/Blusas/{str(producto_num).zfill(6)}_{imagen_num}.jpg"

            # Subir imagen
            exito, url_s3 = self.upload_image_to_s3(str(imagen_path), s3_key)

            if exito:
                imagenes_subidas += 1
                self.estadisticas['urls_generadas'].append({
                    'producto_id': producto_num,
                    'imagen_num': imagen_num,
                    'url': url_s3,
                    'key': s3_key
                })
            else:
                imagenes_fallidas += 1

            # Actualizar contadores
            imagen_num += 1
            if imagen_num > images_per_product:
                imagen_num = 1
                producto_num += 1

        # Resumen final
        tiempo_transcurrido = (datetime.now() - self.estadisticas['tiempo_inicio']).total_seconds()
        minutos = int(tiempo_transcurrido // 60)
        segundos = int(tiempo_transcurrido % 60)

        print(f"\n{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}✅ UPLOAD COMPLETADO{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")

        print(f"\n{Colors.BOLD}📊 ESTADÍSTICAS FINALES:{Colors.END}")
        print(f"  • Imágenes subidas: {Colors.OK}{imagenes_subidas}{Colors.END}")
        print(f"  • Imágenes fallidas: {Colors.FAIL if imagenes_fallidas > 0 else Colors.OK}{imagenes_fallidas}{Colors.END}")
        print(f"  • Tiempo total: {minutos}m {segundos}s")
        print(f"  • Bucket S3: {self.bucket_name}")
        print(f"  • Productos creados: {producto_num - 1 if imagen_num == 1 else producto_num}")

        print(f"\n{Colors.BOLD}📋 ESTRUCTURA S3:{Colors.END}")
        print(f"  productos/Blusas/")
        print(f"    ├── 000001_1.jpg")
        print(f"    ├── 000001_2.jpg")
        print(f"    ├── 000001_3.jpg")
        print(f"    ├── 000002_1.jpg")
        print(f"    └── ...")

        print(f"\n{Colors.BOLD}🔗 PRIMERAS URLs GENERADAS:{Colors.END}")
        for item in self.estadisticas['urls_generadas'][:5]:
            print(f"  {item['url']}")

        print(f"\n{Colors.OK}✨ Imágenes cargadas exitosamente en {self.bucket_name}{Colors.END}")
        print(f"\n{Colors.BOLD}📋 PRÓXIMOS PASOS:{Colors.END}")
        final_producto = producto_num - 1 if imagen_num == 1 else producto_num
        print(f"  1. Ejecuta el seeder: {Colors.CYAN}python scripts/super_seeder.py{Colors.END}")
        print(f"  2. El seeder usará imágenes: 000001_1.jpg hasta 000{final_producto:06d}_3.jpg\n")

        return {
            'imagenes_subidas': imagenes_subidas,
            'imagenes_fallidas': imagenes_fallidas,
            'productos_creados': final_producto,
            'tiempo': f"{minutos}m {segundos}s"
        }


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Subir imágenes a S3 (SIN crear seeder)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Subida de primeras 2500 imágenes (3 por producto = ~833 productos)
  python scripts/upload_imagenes_s3.py --max-imagenes 2500

  # Prueba con 100 imágenes
  python scripts/upload_imagenes_s3.py --max-imagenes 100

  # Subida completa (todas disponibles)
  python scripts/upload_imagenes_s3.py --max-imagenes 10000

FLUJO RECOMENDADO:
  1. python scripts/upload_imagenes_s3.py --max-imagenes 2500
  2. (Verificar en AWS Console que se subieron 2500 imágenes)
  3. python scripts/super_seeder.py
        """
    )
    parser.add_argument('--max-imagenes', type=int, default=2500,
                        help='Máximo número de imágenes a subir (default: 2500)')
    parser.add_argument('--images-per-product', type=int, default=1,
                        help='Imágenes por producto (default: 1)')
    parser.add_argument('--verbose', action='store_true',
                        help='Modo verbose')

    args = parser.parse_args()

    if args.max_imagenes < 1:
        print(f"{Colors.FAIL}❌ ERROR:{Colors.END} --max-imagenes debe ser > 0")
        sys.exit(1)

    uploader = S3ImageUploader(verbose=args.verbose)

    try:
        resultado = uploader.upload_images_batch(
            max_imagenes=args.max_imagenes,
            images_per_product=args.images_per_product
        )
    except KeyboardInterrupt:
        print(f"\n{Colors.WARN}⚠️ Proceso interrumpido{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR:{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
