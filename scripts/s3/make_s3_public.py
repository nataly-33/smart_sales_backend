#!/usr/bin/env python3
"""
Cambiar Object Ownership y hacer objetos públicos
"""
import boto3
from decouple import config

S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default='smart-sales-2025-media')
S3_REGION = config('AWS_S3_REGION_NAME', default='us-east-1')

s3 = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY')
)

print(f"\n🔧 Configurando acceso público para {S3_BUCKET}\n")

# 1. Cambiar Object Ownership a ObjectWriter (permite ACLs)
print("1️⃣ Cambiando Object Ownership a ObjectWriter...")
try:
    s3.put_bucket_ownership_controls(
        Bucket=S3_BUCKET,
        OwnershipControls={
            'Rules': [
                {
                    'ObjectOwnership': 'ObjectWriter'
                }
            ]
        }
    )
    print("   ✅ Object Ownership cambiado a ObjectWriter\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# 2. Listar objetos y hacer públicos
print("2️⃣ Haciendo objetos públicos (PutObjectAcl)...")
response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix='productos/')

if 'Contents' in response:
    total = len(response['Contents'])
    print(f"   Total de objetos: {total}")
    
    failed = 0
    success = 0
    
    for idx, obj in enumerate(response['Contents'], 1):
        key = obj['Key']
        try:
            s3.put_object_acl(Bucket=S3_BUCKET, Key=key, ACL='public-read')
            success += 1
            if idx % 50 == 0:
                print(f"   [{idx}/{total}] ✅ {success} exitosos, {failed} fallidos")
        except Exception as e:
            failed += 1
            print(f"   ❌ Error en {key}: {e}")
    
    print(f"\n   ✅ COMPLETADO: {success} públicos, {failed} fallidos\n")
else:
    print("   ❌ No hay objetos\n")

# 3. Test
print("3️⃣ Verificando acceso público...")
try:
    import requests
    url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/productos/Blusas/000003_1.jpg"
    response = requests.head(url, timeout=5)
    if response.status_code == 200:
        print(f"   ✅ ACCESO PÚBLICO FUNCIONA! ({response.status_code})")
    else:
        print(f"   ❌ Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n")
