#!/usr/bin/env python3
"""
Verificar qué archivos existen en S3
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

import boto3
from decouple import config

# Configuración S3
S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default='smart-sales-2025-media')
S3_REGION = config('AWS_S3_REGION_NAME', default='us-east-1')
S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"

print("=" * 70)
print("🔍 VERIFICANDO S3")
print("=" * 70)
print(f"Bucket: {S3_BUCKET}")
print(f"Region: {S3_REGION}")
print(f"Base URL: {S3_BASE_URL}")
print()

try:
    s3_client = boto3.client('s3', region_name=S3_REGION)
    
    # Probar diferentes prefixes
    prefixes = ['blusas/', 'productos/Blusas/', 'productos/blusas/', 'Blusas/']
    
    for prefix in prefixes:
        print(f"\n📁 Buscando con prefix: '{prefix}'")
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix, MaxKeys=5)
        
        if 'Contents' in response:
            print(f"   ✅ Encontrados: {len(response['Contents'])} archivos")
            for obj in response['Contents'][:3]:
                key = obj['Key']
                url = f"{S3_BASE_URL}/{key}"
                print(f"      - {key}")
                print(f"        URL: {url}")
        else:
            print(f"   ❌ No se encontraron archivos")
    
    print("\n" + "=" * 70)
    print("🔢 CONTEO TOTAL")
    print("=" * 70)
    
    # Contar todos los archivos en productos/Blusas/
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix='productos/Blusas/')
    if 'Contents' in response:
        total = len(response['Contents'])
        print(f"Total archivos en productos/Blusas/: {total}")
        
        # Contar imágenes válidas
        imagenes = [
            obj['Key'] for obj in response['Contents']
            if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        print(f"Total imágenes válidas: {len(imagenes)}")
        
        if imagenes:
            print(f"\nPrimeras 5 imágenes:")
            for img in imagenes[:5]:
                print(f"  - {img}")
    else:
        print("❌ No se encontraron archivos en productos/Blusas/")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
