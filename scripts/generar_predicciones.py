#!/usr/bin/env python3
"""
Script para generar predicciones de ventas POR CATEGORÍA
"""
import os
import sys
import django
from pathlib import Path

# Configuración del entorno Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.ai.services.prediction import PredictionService

print("🔮 Iniciando generador de predicciones...")
service = PredictionService()

# Definimos las categorías que queremos predecir
# (Asegúrate que coincidan con las de tu base de datos)
CATEGORIAS = ['Blusas', 'Vestidos', 'Jeans', 'Jackets']
N_MONTHS = 6

total_preds = 0

print(f"\n📅 Generando predicciones para los próximos {N_MONTHS} meses...\n")

# 1. Generar predicciones por cada categoría (Esto llena las barras de colores)
for cat in CATEGORIAS:
    print(f"   👉 Procesando categoría: {cat}...")
    preds = service.predict_next_n_months(n_months=N_MONTHS, categoria=cat)
    total_preds += len(preds)

# 2. Generar predicción del total general (Opcional, para métricas globales)
print(f"   👉 Procesando Total General...")
service.predict_next_n_months(n_months=N_MONTHS, categoria=None)

print("\n" + "="*50)
print(f"✅ PROCESO COMPLETADO")
print(f"📊 Se generaron {total_preds} predicciones detalladas")
print("="*50)
print("\n✨ Ahora revisa tu Dashboard en: /api/ai/dashboard/")