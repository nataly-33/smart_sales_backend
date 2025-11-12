#!/usr/bin/env python
"""
Script para probar el sistema de notificaciones

Este script funciona SIN Firebase configurado, solo prueba la estructura
"""
import os
import sys
import django
from pathlib import Path

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

django.setup()

from apps.accounts.models import User
from apps.notifications.models import DeviceToken, Notification, NotificationPreference


def main():
    print("=" * 80)
    print("🧪 PRUEBA DEL SISTEMA DE NOTIFICACIONES".center(80))
    print("=" * 80)
    print()

    # 1. Obtener un usuario
    print("📋 Paso 1: Obtener usuario de prueba...")
    user = User.objects.filter(email='admin@smartsales365.com').first()
    if not user:
        user = User.objects.first()

    if not user:
        print("❌ No hay usuarios en la base de datos")
        return

    print(f"✅ Usuario encontrado: {user.email}")
    print()

    # 2. Crear token de dispositivo
    print("📋 Paso 2: Crear token de dispositivo...")
    token, created = DeviceToken.objects.get_or_create(
        user=user,
        token='test_fcm_token_12345',
        defaults={
            'device_type': 'android',
            'device_name': 'Dispositivo de Prueba',
            'is_active': True
        }
    )

    if created:
        print(f"✅ Token creado: {token.token[:30]}...")
    else:
        print(f"✅ Token ya existía: {token.token[:30]}...")
        token.is_active = True
        token.save()
    print()

    # 3. Crear preferencias de notificación
    print("📋 Paso 3: Crear preferencias de notificación...")
    prefs, created = NotificationPreference.objects.get_or_create(
        user=user,
        defaults={
            'order_notifications': True,
            'payment_notifications': True,
            'promotion_notifications': True,
            'general_notifications': True
        }
    )

    if created:
        print("✅ Preferencias creadas")
    else:
        print("✅ Preferencias ya existían")

    print(f"   - Notificaciones de pedidos: {'✅' if prefs.order_notifications else '❌'}")
    print(f"   - Notificaciones de pagos: {'✅' if prefs.payment_notifications else '❌'}")
    print(f"   - Notificaciones de promociones: {'✅' if prefs.promotion_notifications else '❌'}")
    print()

    # 4. Crear notificación de prueba (sin enviarla)
    print("📋 Paso 4: Crear notificación de prueba...")
    notification = Notification.objects.create(
        user=user,
        title="🎉 ¡Bienvenido!",
        body="Esta es una notificación de prueba del sistema SmartSales365",
        notification_type="general",
        data={
            "test": True,
            "timestamp": "2025-11-12"
        },
        is_sent=False  # NO enviar por FCM (solo prueba de BD)
    )
    print(f"✅ Notificación creada: ID {notification.id}")
    print(f"   Título: {notification.title}")
    print(f"   Cuerpo: {notification.body}")
    print()

    # 5. Marcar como leída
    print("📋 Paso 5: Marcar notificación como leída...")
    notification.mark_as_read()
    print(f"✅ Notificación marcada como leída")
    print(f"   Fecha de lectura: {notification.read_at}")
    print()

    # 6. Estadísticas
    print("📋 Paso 6: Mostrar estadísticas...")
    total_notifications = Notification.objects.filter(user=user).count()
    total_read = Notification.objects.filter(user=user, is_read=True).count()
    total_unread = Notification.objects.filter(user=user, is_read=False).count()
    total_tokens = DeviceToken.objects.filter(user=user).count()
    active_tokens = DeviceToken.objects.filter(user=user, is_active=True).count()

    print(f"✅ Estadísticas del usuario {user.email}:")
    print(f"   - Total notificaciones: {total_notifications}")
    print(f"   - Notificaciones leídas: {total_read}")
    print(f"   - Notificaciones no leídas: {total_unread}")
    print(f"   - Total tokens: {total_tokens}")
    print(f"   - Tokens activos: {active_tokens}")
    print()

    # 7. Probar envío (simulado)
    print("📋 Paso 7: Simular envío de notificación...")
    print("ℹ️  NOTA: Firebase no está configurado, por lo que no se enviará realmente")
    print("   Para enviar notificaciones reales, configura Firebase según INSTALL_NOTIFICATIONS.md")

    from apps.notifications.services import notification_service

    result = notification_service.send_to_user(
        user=user,
        title="📦 Pedido Enviado",
        body="Tu pedido #12345 está en camino",
        notification_type="order_shipped",
        data={"order_id": "12345"},
        save_to_db=True
    )

    print(f"   Resultado: {result}")
    print()

    # Resumen final
    print("=" * 80)
    print("✅ PRUEBA COMPLETADA EXITOSAMENTE".center(80))
    print("=" * 80)
    print()
    print("📚 Próximos pasos:")
    print("   1. Configura Firebase siguiendo INSTALL_NOTIFICATIONS.md")
    print("   2. Ve al admin de Django: /admin/notifications/")
    print("   3. Prueba los endpoints de la API:")
    print("      - GET /api/notifications/notifications/")
    print("      - GET /api/notifications/device-tokens/")
    print("      - GET /api/notifications/preferences/")
    print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
