#!/usr/bin/env python
"""
Script para subir datasets de imágenes de productos a AWS S3

Uso:
    python scripts/upload_to_s3.py --category vestidos --folder ./datasets/vestidos/

Requisitos:
    - Tener configuradas las variables de entorno AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY
    - Tener un bucket creado en S3 (AWS_STORAGE_BUCKET_NAME en .env)
    - Dataset de imágenes en la carpeta especificada
"""

import os
import sys
import argparse
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from decouple import config

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Importar configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
import django
django.setup()


class S3Uploader:
    """Clase para subir imágenes de productos a S3"""

    def __init__(self):
        self.bucket_name = config('AWS_STORAGE_BUCKET_NAME')
        self.region = config('AWS_S3_REGION_NAME', default='us-east-1')

        # Cliente de S3
        self.s3_client = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY')
        )

        print(f"✅ Conectado a bucket: {self.bucket_name}")

    def upload_image(self, local_path: str, s3_key: str) -> str:
        """
        Sube una imagen a S3

        Args:
            local_path: Ruta local del archivo
            s3_key: Ruta en S3 (ej: productos/vestidos/vestido_001.jpg)

        Returns:
            URL pública de la imagen en S3
        """
        try:
            # Subir archivo
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'image/jpeg',  # Ajustar según el tipo
                    'ACL': 'public-read'  # Hacer pública la imagen
                }
            )

            # Generar URL pública
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

            return url

        except ClientError as e:
            print(f"❌ Error al subir {local_path}: {e}")
            return None

    def upload_category_folder(self, category: str, folder_path: str) -> list:
        """
        Sube todas las imágenes de una categoría a S3

        Args:
            category: Nombre de la categoría (vestidos, blusas, pantalones, faldas)
            folder_path: Ruta local de la carpeta con las imágenes

        Returns:
            Lista de URLs de las imágenes subidas
        """
        folder = Path(folder_path)

        if not folder.exists():
            print(f"❌ Carpeta no encontrada: {folder_path}")
            return []

        # Extensiones de imagen soportadas
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

        # Obtener todas las imágenes
        image_files = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        if not image_files:
            print(f"❌ No se encontraron imágenes en {folder_path}")
            return []

        print(f"\n📂 Subiendo {len(image_files)} imágenes de la categoría '{category}'...")

        uploaded_urls = []

        for i, image_file in enumerate(image_files, 1):
            # Generar key de S3: productos/{categoria}/imagen_{numero}.{extension}
            file_extension = image_file.suffix.lower()
            s3_key = f"productos/{category}/imagen_{i:04d}{file_extension}"

            # Subir imagen
            url = self.upload_image(str(image_file), s3_key)

            if url:
                uploaded_urls.append(url)
                print(f"  ✅ [{i}/{len(image_files)}] {image_file.name} → {url}")
            else:
                print(f"  ❌ [{i}/{len(image_files)}] {image_file.name} FALLÓ")

        print(f"\n✅ {len(uploaded_urls)}/{len(image_files)} imágenes subidas exitosamente")

        return uploaded_urls

    def create_bucket_if_not_exists(self):
        """Crea el bucket si no existe"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' existe")
        except ClientError:
            print(f"⚠️  Bucket '{self.bucket_name}' no existe, creando...")
            try:
                if self.region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                print(f"✅ Bucket '{self.bucket_name}' creado")
            except ClientError as e:
                print(f"❌ Error al crear bucket: {e}")
                raise


def save_urls_to_file(category: str, urls: list):
    """
    Guarda las URLs en un archivo de texto para usar en el seeder

    Args:
        category: Nombre de la categoría
        urls: Lista de URLs
    """
    output_file = BASE_DIR / 'scripts' / f's3_urls_{category}.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')

    print(f"\n📄 URLs guardadas en: {output_file}")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Subir imágenes de productos a AWS S3'
    )
    parser.add_argument(
        '--category',
        type=str,
        required=True,
        choices=['vestidos', 'blusas', 'pantalones', 'faldas'],
        help='Categoría de los productos'
    )
    parser.add_argument(
        '--folder',
        type=str,
        required=True,
        help='Ruta de la carpeta con las imágenes'
    )
    parser.add_argument(
        '--create-bucket',
        action='store_true',
        help='Crear bucket si no existe'
    )

    args = parser.parse_args()

    # Crear uploader
    uploader = S3Uploader()

    # Crear bucket si se especificó
    if args.create_bucket:
        uploader.create_bucket_if_not_exists()

    # Subir imágenes
    urls = uploader.upload_category_folder(args.category, args.folder)

    if urls:
        # Guardar URLs en archivo
        save_urls_to_file(args.category, urls)

        print("\n" + "="*70)
        print("✅ PROCESO COMPLETADO")
        print("="*70)
        print(f"\n📊 Resumen:")
        print(f"  • Categoría: {args.category}")
        print(f"  • Imágenes subidas: {len(urls)}")
        print(f"  • Bucket: {uploader.bucket_name}")
        print(f"\n💡 Próximo paso:")
        print(f"  Ejecuta el seeder para crear productos con estas imágenes:")
        print(f"  python manage.py shell < scripts/seed_data.py")
    else:
        print("\n❌ No se subieron imágenes")
        sys.exit(1)


if __name__ == '__main__':
    main()
