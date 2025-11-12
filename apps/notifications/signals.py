"""
Signals para enviar notificaciones automáticas
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import Pedido
from apps.notifications.services import notification_service


@receiver(post_save, sender=Pedido)
def send_order_notification(sender, instance, created, **kwargs):
    """
    Envía notificación cuando se crea o actualiza un pedido
    """
    if created:
        # Pedido creado
        notification_service.send_order_notification(instance, 'created')
    else:
        # Pedido actualizado - verificar cambio de estado
        if instance.tracker.has_changed('estado'):
            old_estado = instance.tracker.previous('estado')
            new_estado = instance.estado

            # Mapear estados a tipos de notificación
            status_map = {
                'enviado': 'shipped',
                'entregado': 'delivered',
                'cancelado': 'cancelled'
            }

            if new_estado in status_map:
                notification_service.send_order_notification(
                    instance,
                    status_map[new_estado]
                )
