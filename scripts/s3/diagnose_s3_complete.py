#!/usr/bin/env python3
"""
Diagnóstico completo de S3 para 403
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

print(f"\n🔍 DIAGNÓSTICO COMPLETO S3: {S3_BUCKET}\n")

# 1. Bucket Policy
print("1️⃣ Bucket Policy:")
try:
    policy = s3.get_bucket_policy(Bucket=S3_BUCKET)
    policy_json = json.loads(policy['Policy'])
    print(json.dumps(policy_json, indent=2))
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Block Public Access
print("\n2️⃣ Block Public Access:")
try:
    bpa = s3.get_public_access_block(Bucket=S3_BUCKET)
    config_data = bpa['PublicAccessBlockConfiguration']
    for key, val in config_data.items():
        print(f"   {key}: {val}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Object Ownership
print("\n3️⃣ Object Ownership:")
try:
    oc = s3.get_bucket_ownership_controls(Bucket=S3_BUCKET)
    ownership = oc['OwnershipControls']['Rules'][0]['ObjectOwnership']
    print(f"   ObjectOwnership: {ownership}")
except Exception as e:
    print(f"   ℹ️  {e}")

# 4. Específico: obtener un objeto y ver sus permisos
print("\n4️⃣ Permisos específicos del objeto 000001_1.jpg:")
key = 'productos/Blusas/000001_1.jpg'
try:
    obj = s3.head_object(Bucket=S3_BUCKET, Key=key)
    print(f"   ✅ Objeto existe")
    print(f"   Content-Type: {obj.get('ContentType')}")
    print(f"   ServerSideEncryption: {obj.get('ServerSideEncryption')}")
    print(f"   Metadata: {obj.get('Metadata', {})}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Intentar acceso público desde Python
print("\n5️⃣ Test acceso público (desde Python):")
try:
    import requests
    url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"
    
    # Sin Origin
    r1 = requests.head(url)
    print(f"   Sin Origin header: {r1.status_code}")
    
    # Con Origin
    r2 = requests.head(url, headers={'Origin': 'http://localhost:3000'})
    print(f"   Con Origin header: {r2.status_code}")
    if r2.status_code == 200:
        print(f"   ✅ Headers CORS presentes:")
        cors_headers = {k: v for k, v in r2.headers.items() if 'access' in k.lower()}
        print(json.dumps(cors_headers, indent=2))
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n")
