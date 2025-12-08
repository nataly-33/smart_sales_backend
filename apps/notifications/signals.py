"""
Signals para enviar notificaciones automáticas

Eventos que generan notificaciones:
1. Nuevo usuario registrado → Notificar a admin
2. Producto agregado al carrito → Notificar a usuario
3. Pedido creado → Notificar a cliente y admin
4. Cambio de estado del pedido → Notificar a cliente
5. Nueva reseña → Notificar a admin
6. Stock bajo/sin stock → Notificar a admin
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.notifications.services import notification_service
from apps.accounts.models import User
from apps.orders.models import Pedido
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# 1. NUEVO USUARIO REGISTRADO
# ============================================================================

@receiver(post_save, sender=User)
def notify_new_user_registration(sender, instance, created, **kwargs):
    """
    Notificar al admin cuando se registra un nuevo usuario
    """
    if created:
        try:
            # Notificar a todos los admins
            admins = User.objects.filter(is_superuser=True, activo=True)
            
            for admin in admins:
                notification_service.send_to_user(
                    user=admin,
                    title="👤 Nuevo Usuario Registrado",
                    body=f"{instance.email} se registró en Smart Sales",
                    notification_type="new_user",
                    data={
                        'user_id': instance.id,
                        'email': instance.email,
                    },
                    save_to_db=True
                )
            
            # Notificar al usuario que se registró
            notification_service.send_to_user(
                user=instance,
                title="✅ Bienvenido a Smart Sales",
                body="Tu cuenta ha sido creada exitosamente",
                notification_type="registration_success",
                save_to_db=True
            )
            
            logger.info(f"✅ Notificación de registro enviada: {instance.email}")
            
        except Exception as e:
            logger.error(f"❌ Error en notificación de registro: {e}")


# ============================================================================
# 2. PEDIDO CREADO Y CAMBIOS DE ESTADO
# ============================================================================

@receiver(post_save, sender=Pedido)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Envía notificaciones cuando se crea o actualiza un pedido
    """
    
    if created:
        # ✅ NUEVO PEDIDO - Notificar cliente y admin
        try:
            # Notificar al cliente
            notification_service.send_to_user(
                user=instance.cliente,
                title="✅ Pedido Confirmado",
                body=f"Tu pedido #{instance.id} ha sido confirmado. Total: ${instance.monto_total}",
                notification_type="order_created",
                data={
                    'order_id': instance.id,
                    'status': instance.estado,
                    'amount': str(instance.monto_total),
                },
                save_to_db=True
            )
            
            # Notificar a los admins
            admins = User.objects.filter(is_superuser=True, activo=True)
            for admin in admins:
                notification_service.send_to_user(
                    user=admin,
                    title="📦 Nuevo Pedido",
                    body=f"{instance.cliente.email} realizó un pedido. Total: ${instance.monto_total}",
                    notification_type="new_order_admin",
                    data={
                        'order_id': instance.id,
                        'customer_id': instance.cliente.id,
                        'customer_email': instance.cliente.email,
                    },
                    save_to_db=True
                )
            
            logger.info(f"✅ Notificación de pedido creado enviada: {instance.id}")
            
        except Exception as e:
            logger.error(f"❌ Error notificando pedido creado: {e}")
    
    else:
        # PEDIDO ACTUALIZADO - Verificar cambio de estado
        try:
            # Verificar si el estado cambió
            if hasattr(instance, 'tracker') and instance.tracker.has_changed('estado'):
                new_estado = instance.estado
                
                # Mensajes personalizados por estado
                status_messages = {
                    'confirmado': {
                        'title': '✅ Pedido Confirmado',
                        'body': f'Tu pedido #{instance.id} ha sido confirmado',
                        'type': 'order_confirmed'
                    },
                    'preparando': {
                        'title': '⏳ Preparando tu Pedido',
                        'body': f'Estamos preparando tu pedido #{instance.id}',
                        'type': 'order_preparing'
                    },
                    'listo': {
                        'title': '📦 Tu Pedido está Listo',
                        'body': f'Tu pedido #{instance.id} está listo para recoger',
                        'type': 'order_ready'
                    },
                    'enviado': {
                        'title': '🚚 Tu Pedido ha sido Enviado',
                        'body': f'Tu pedido #{instance.id} está en camino',
                        'type': 'order_shipped'
                    },
                    'entregado': {
                        'title': '✨ Pedido Entregado',
                        'body': f'Tu pedido #{instance.id} ha sido entregado',
                        'type': 'order_delivered'
                    },
                    'cancelado': {
                        'title': '❌ Pedido Cancelado',
                        'body': f'Tu pedido #{instance.id} ha sido cancelado',
                        'type': 'order_cancelled'
                    }
                }
                
                if new_estado in status_messages:
                    msg = status_messages[new_estado]
                    
                    # Notificar al cliente
                    notification_service.send_to_user(
                        user=instance.cliente,
                        title=msg['title'],
                        body=msg['body'],
                        notification_type=msg['type'],
                        data={
                            'order_id': instance.id,
                            'status': new_estado,
                        },
                        save_to_db=True
                    )
                    
                    logger.info(f"✅ Notificación de estado enviada al cliente: {new_estado}")
                    
                    # Notificar a admins de cambios importantes
                    if new_estado in ['entregado', 'cancelado']:
                        admins = User.objects.filter(is_superuser=True, activo=True)
                        
                        for admin in admins:
                            notification_service.send_to_user(
                                user=admin,
                                title=f"📊 Pedido {new_estado.upper()}",
                                body=f"Pedido #{instance.id} de {instance.cliente.email}",
                                notification_type=f"order_{new_estado}_admin",
                                data={
                                    'order_id': instance.id,
                                    'status': new_estado,
                                },
                                save_to_db=True
                            )
        
        except Exception as e:
            logger.error(f"❌ Error en cambio de estado del pedido: {e}")
