#!/usr/bin/env python3
"""
Configurar CORS para permitir imágenes desde localhost:3000
"""
import boto3
import json
from decouple import config

S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default='smart-sales-2025-media')
S3_REGION = config('AWS_S3_REGION_NAME', default='us-east-1')

s3 = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY')
)

print(f"\n⚙️ Configurando CORS para {S3_BUCKET}\n")

# CORS Configuration
cors_config = {
    'CORSRules': [
        {
            'AllowedOrigins': [
                'http://localhost:3000',
                'http://localhost:5173',
                '*'  # Permitir todos (en prod, especifica dominios)
            ],
            'AllowedMethods': ['GET', 'HEAD', 'PUT', 'POST', 'DELETE'],
            'AllowedHeaders': ['*'],
            'ExposeHeaders': ['ETag', 'x-amz-version-id'],
            'MaxAgeSeconds': 3000
        }
    ]
}

print("1️⃣ Aplicando configuración CORS...")
try:
    s3.put_bucket_cors(
        Bucket=S3_BUCKET,
        CORSConfiguration=cors_config
    )
    print("   ✅ CORS configurado exitosamente\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Verificar CORS
print("2️⃣ Verificando CORS...")
try:
    current_cors = s3.get_bucket_cors(Bucket=S3_BUCKET)
    print("   ✅ CORS actual:")
    print(json.dumps(current_cors['CORSRules'], indent=2))
except Exception as e:
    print(f"   ℹ️  No hay CORS configurado: {e}")

print("\n✨ CORS debe permitir ahora que el frontend acceda a imágenes desde S3\n")
