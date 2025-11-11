#!/usr/bin/env python3
"""
🖼️ ASIGNAR IMÁGENES A BLUSAS EXISTENTES

Este script asigna las imágenes de S3 a las blusas que ya existen en la base de datos.
Solo crea los registros en ImagenPrendaURL sin modificar las prendas existentes.

Uso:
    python scripts/asignar_imagenes_blusas.py
"""

import os
import sys
import django
from pathlib import Path

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.db import transaction
from decouple import config
from apps.products.models import Prenda, ImagenPrendaURL

# ============= CONFIGURACIÓN S3 =============
S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default='smart-sales-2025-media')
S3_REGION = config('AWS_S3_REGION_NAME', default='us-east-1')
S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"

# ============= COLORES PARA TERMINAL =============
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    OK = '\033[92m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'=' * 70}")
    print(f"{text:^70}")
    print(f"{'=' * 70}{Colors.END}\n")

def generar_urls_imagenes():
    """
    Genera las URLs de las imágenes basándose en la estructura de S3.
    Las imágenes están en: productos/Blusas/000001_1.jpg hasta 002000_1.jpg
    """
    print(f"{Colors.CYAN}📸 Generando URLs de imágenes de S3...{Colors.END}")
    
    imagenes = []
    for i in range(1, 2001):  # 000001 hasta 002000
        numero = str(i).zfill(6)
        # Solo la imagen _1.jpg (la principal)
        key = f"productos/Blusas/{numero}_1.jpg"
        url = f"{S3_BASE_URL}/{key}"
        imagenes.append(url)
    
    print(f"{Colors.OK}✅ {len(imagenes)} URLs generadas{Colors.END}")
    print(f"{Colors.CYAN}Ejemplo: {imagenes[0]}{Colors.END}")
    return imagenes

def asignar_imagenes_a_blusas():
    """
    Asigna imágenes a las blusas existentes en la base de datos.
    """
    print_header("🖼️ ASIGNANDO IMÁGENES A BLUSAS")
    
    # Obtener todas las blusas
    blusas = Prenda.objects.filter(categorias__nombre='Blusas').order_by('id')
    total_blusas = blusas.count()
    
    print(f"{Colors.BLUE}📊 Total de blusas en BD: {total_blusas}{Colors.END}")
    
    if total_blusas == 0:
        print(f"{Colors.WARN}⚠️ No se encontraron blusas en la base de datos{Colors.END}")
        return
    
    # Generar URLs de imágenes
    imagenes_urls = generar_urls_imagenes()
    
    # Verificar cuántas blusas ya tienen imágenes
    blusas_con_imagenes = ImagenPrendaURL.objects.filter(prenda__in=blusas).values_list('prenda_id', flat=True).distinct()
    print(f"{Colors.CYAN}📸 Blusas que ya tienen imágenes: {len(blusas_con_imagenes)}{Colors.END}")
    
    # Contador
    imagenes_creadas = 0
    imagenes_actualizadas = 0
    errores = 0
    
    print(f"\n{Colors.CYAN}🔄 Procesando blusas...{Colors.END}\n")
    
    with transaction.atomic():
        for idx, blusa in enumerate(blusas, start=0):
            try:
                # Usar el índice para asignar la imagen correspondiente
                if idx < len(imagenes_urls):
                    imagen_url = imagenes_urls[idx]
                else:
                    # Si hay más blusas que imágenes, usar la última imagen disponible
                    imagen_url = imagenes_urls[-1]
                
                # Verificar si ya tiene imagen
                imagen_existente = ImagenPrendaURL.objects.filter(prenda=blusa).first()
                
                if imagen_existente:
                    # Actualizar la URL si es diferente
                    if imagen_existente.imagen_url != imagen_url:
                        imagen_existente.imagen_url = imagen_url
                        imagen_existente.save()
                        imagenes_actualizadas += 1
                else:
                    # Crear nueva imagen
                    ImagenPrendaURL.objects.create(
                        prenda=blusa,
                        imagen_url=imagen_url,
                        es_principal=True,
                        orden=1,
                        alt_text=blusa.nombre
                    )
                    imagenes_creadas += 1
                
                # Mostrar progreso cada 100 blusas
                if (idx + 1) % 100 == 0:
                    print(f"  [{idx + 1:4d}/{total_blusas}] Procesando...")
                    
            except Exception as e:
                errores += 1
                print(f"{Colors.FAIL}❌ Error en blusa ID {blusa.id}: {e}{Colors.END}")
    
    # Resumen final
    print_header("📊 RESUMEN")
    print(f"{Colors.OK}✅ Imágenes creadas:      {imagenes_creadas}{Colors.END}")
    print(f"{Colors.CYAN}🔄 Imágenes actualizadas: {imagenes_actualizadas}{Colors.END}")
    print(f"{Colors.FAIL}❌ Errores:               {errores}{Colors.END}")
    print(f"{Colors.BOLD}{'━' * 35}")
    print(f"📸 Total procesado:       {imagenes_creadas + imagenes_actualizadas}{Colors.END}")
    
    # Mostrar ejemplos
    print(f"\n{Colors.CYAN}📋 EJEMPLOS DE IMÁGENES ASIGNADAS:{Colors.END}\n")
    ejemplos = ImagenPrendaURL.objects.filter(prenda__in=blusas)[:3]
    for img in ejemplos:
        print(f"  {Colors.GREEN}✓{Colors.END} {img.prenda.nombre}")
        print(f"    URL: {Colors.CYAN}{img.imagen_url}{Colors.END}")
    
    print(f"\n{Colors.OK}✅ ¡Asignación completada exitosamente!{Colors.END}\n")

if __name__ == '__main__':
    try:
        asignar_imagenes_a_blusas()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARN}⚠️ Proceso interrumpido por el usuario{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ ERROR: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
