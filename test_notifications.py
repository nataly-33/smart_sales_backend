#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de notificaciones
Ejecutar con: python manage.py shell < test_notifications.py
O directamente: python test_notifications.py (si está en el mismo directorio que manage.py)
"""

import sys
import django
import os

# Configurar Django (si se ejecuta directamente)
if __name__ == "__main__" and not django.apps.apps.ready:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

try:
    from apps.notifications.services import notification_service
    from apps.accounts.models import User
    
    print("\n" + "="*60)
    print("🧪 PRUEBA DEL SISTEMA DE NOTIFICACIONES")
    print("="*60)
    
    # Paso 1: Verificar Firebase
    print("\n[1/3] Verificando Firebase...")
    if hasattr(notification_service, 'fcm_service') and notification_service.fcm_service.initialized:
        print("✅ Firebase inicializado correctamente")
    else:
        print("⚠️  Firebase no está inicializado")
    
    # Paso 2: Buscar usuario
    print("\n[2/3] Buscando usuarios en la BD...")
    user = User.objects.first()
    
    if not user:
        print("❌ No hay usuarios en la base de datos")
        print("   Crea un usuario primero:")
        print("   python manage.py createsuperuser")
        sys.exit(1)
    
    print(f"✅ Usuario encontrado: {user.email}")
    
    # Paso 3: Enviar notificación de prueba
    print("\n[3/3] Enviando notificación de prueba...")
    result = notification_service.send_to_user(
        user=user,
        title="🧪 Prueba de Backend",
        body="Si ves esto en los logs, ¡el backend funciona!",
        notification_type="general",
        save_to_db=True
    )
    
    print("\n📊 RESULTADO:")
    print("-" * 60)
    if result:
        print("✅ Notificación enviada exitosamente!")
        print(f"   Detalles: {result}")
    else:
        print("⚠️  Notificación no pudo ser enviada")
        print("   Posibles causas:")
        print("   - Usuario no tiene tokens de FCM activos")
        print("   - Firebase no está configurado correctamente")
        print("   - Credenciales de Firebase no son válidas")
    
    print("\n" + "="*60)
    print("✅ Prueba completada")
    print("="*60 + "\n")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("   Verifica que las aplicaciones estén en INSTALLED_APPS")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error inesperado: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
