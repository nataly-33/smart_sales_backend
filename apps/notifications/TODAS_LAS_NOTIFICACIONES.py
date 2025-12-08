"""
NOTIFICACIONES COMPLETAS PARA SMART SALES

Este archivo contiene TODOS los eventos que generan notificaciones.
Copiar en: apps/notifications/signals_completo.py

Eventos:
1. Usuario inicia sesión
2. Nuevo usuario registrado (notificar a admin)
3. Producto agregado al carrito
4. Pedido creado
5. Pedido enviado
6. Pedido entregado
7. Pedido cancelado
8. Pago recibido
9. Nuevo comentario/reseña
10. Producto sin stock
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from apps.notifications.services import notification_service
from apps.accounts.models import User
from apps.orders.models import Pedido, DetallePedido
from apps.cart.models import Cart, CartItem
from apps.products.models import Producto, ProductReview
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# 1. USUARIO INICIA SESIÓN (opcional - puede ser en views)
# ============================================================================

# Este se implementa mejor en views.py del login
# Porque el signal post_save no se activa en login


# ============================================================================
# 2. NUEVO USUARIO REGISTRADO
# ============================================================================

@receiver(post_save, sender=User)
def notify_new_user_registration(sender, instance, created, **kwargs):
    """
    Notificar al admin cuando se registra un nuevo usuario
    """
    if created:
        try:
            # Obtener todos los admins
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
            
            # También notificar al usuario que se registró
            notification_service.send_to_user(
                user=instance,
                title="✅ Bienvenido a Smart Sales",
                body="Tu cuenta ha sido creada exitosamente",
                notification_type="registration_success",
                save_to_db=True
            )
            
            logger.info(f"Notificación enviada: nuevo usuario {instance.email}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de registro: {e}")


# ============================================================================
# 3. PRODUCTO AGREGADO AL CARRITO
# ============================================================================

@receiver(post_save, sender=CartItem)
def notify_product_added_to_cart(sender, instance, created, **kwargs):
    """
    Notificar al usuario cuando agrega producto al carrito
    (Opcional - puede ser muy invasivo)
    """
    if created:
        try:
            notification_service.send_to_user(
                user=instance.cart.usuario,
                title="🛒 Producto Agregado",
                body=f"{instance.producto.nombre} agregado a tu carrito",
                notification_type="cart_item_added",
                data={
                    'product_id': instance.producto.id,
                    'cart_id': instance.cart.id,
                },
                save_to_db=True
            )
            
        except Exception as e:
            logger.error(f"Error enviando notificación de carrito: {e}")


# ============================================================================
# 4. PEDIDO CREADO
# ============================================================================

@receiver(post_save, sender=Pedido)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Envía notificaciones cuando se crea o actualiza un pedido
    """
    
    if created:
        # 4.1 NOTIFICAR AL CLIENTE QUE HIZO EL PEDIDO
        try:
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
            logger.info(f"Notificación de pedido enviada al cliente: {instance.cliente.email}")
        except Exception as e:
            logger.error(f"Error notificando cliente nuevo pedido: {e}")
        
        # 4.2 NOTIFICAR A LOS ADMINS
        try:
            admins = User.objects.filter(is_superuser=True, activo=True)
            
            for admin in admins:
                notification_service.send_to_user(
                    user=admin,
                    title="📦 Nuevo Pedido",
                    body=f"{instance.cliente.email} ha realizado un pedido. Total: ${instance.monto_total}",
                    notification_type="new_order_admin",
                    data={
                        'order_id': instance.id,
                        'customer_id': instance.cliente.id,
                        'customer_email': instance.cliente.email,
                    },
                    save_to_db=True
                )
            
            logger.info(f"Notificación de pedido enviada a admins: {instance.id}")
        except Exception as e:
            logger.error(f"Error notificando admins nuevo pedido: {e}")
    
    else:
        # PEDIDO ACTUALIZADO - VERIFICAR CAMBIO DE ESTADO
        try:
            from model_utils import FieldTracker
            tracker = instance.tracker
            
            if tracker.has_changed('estado'):
                old_estado = tracker.previous('estado')
                new_estado = instance.estado
                
                # 4.3 NOTIFICAR AL CLIENTE CAMBIOS DE ESTADO
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
                    
                    logger.info(f"Notificación de estado enviada al cliente: {new_estado}")
                
                # 4.4 NOTIFICAR A ADMINS DE CAMBIOS IMPORTANTES
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
            logger.error(f"Error en notificación de cambio de estado: {e}")


# ============================================================================
# 5. PAGO RECIBIDO
# ============================================================================

@receiver(post_save, sender=Pedido)
def notify_payment_received(sender, instance, created, **kwargs):
    """
    Notificar cuando se recibe un pago
    (Se puede mejorar si tienes modelo de Pago separado)
    """
    if not created:
        try:
            # Si el estado cambió a 'confirmado', significa que el pago fue procesado
            from model_utils import FieldTracker
            tracker = instance.tracker
            
            if tracker.has_changed('estado') and instance.estado == 'confirmado':
                if instance.pagado:  # Si hay campo pagado
                    # Notificar cliente
                    notification_service.send_to_user(
                        user=instance.cliente,
                        title="💳 Pago Recibido",
                        body=f"Hemos recibido tu pago de ${instance.monto_total}",
                        notification_type="payment_received",
                        data={
                            'order_id': instance.id,
                            'amount': str(instance.monto_total),
                        },
                        save_to_db=True
                    )
                    
                    # Notificar admins
                    admins = User.objects.filter(is_superuser=True, activo=True)
                    for admin in admins:
                        notification_service.send_to_user(
                            user=admin,
                            title="💰 Pago Confirmado",
                            body=f"Pago recibido de {instance.cliente.email}: ${instance.monto_total}",
                            notification_type="payment_confirmed_admin",
                            save_to_db=True
                        )
                    
                    logger.info(f"Notificación de pago enviada: pedido {instance.id}")
        
        except Exception as e:
            logger.error(f"Error en notificación de pago: {e}")


# ============================================================================
# 6. NUEVO COMENTARIO / RESEÑA
# ============================================================================

@receiver(post_save, sender=ProductReview)
def notify_new_review(sender, instance, created, **kwargs):
    """
    Notificar cuando hay un nuevo comentario/reseña
    """
    if created:
        try:
            # Notificar al admin
            admins = User.objects.filter(is_superuser=True, activo=True)
            
            for admin in admins:
                notification_service.send_to_user(
                    user=admin,
                    title="⭐ Nueva Reseña",
                    body=f"Nueva reseña de {instance.usuario.email} en {instance.producto.nombre}",
                    notification_type="new_review",
                    data={
                        'product_id': instance.producto.id,
                        'review_id': instance.id,
                        'rating': instance.calificacion,
                    },
                    save_to_db=True
                )
            
            logger.info(f"Notificación de reseña enviada: {instance.id}")
        
        except Exception as e:
            logger.error(f"Error en notificación de reseña: {e}")


# ============================================================================
# 7. PRODUCTO SIN STOCK
# ============================================================================

@receiver(post_save, sender=Producto)
def notify_low_stock(sender, instance, created, **kwargs):
    """
    Notificar cuando el stock de un producto es bajo o llega a 0
    """
    if not created:
        try:
            # Si el stock cambió a 0
            if instance.stock == 0:
                admins = User.objects.filter(is_superuser=True, activo=True)
                
                for admin in admins:
                    notification_service.send_to_user(
                        user=admin,
                        title="⚠️ Producto Sin Stock",
                        body=f"{instance.nombre} se ha agotado",
                        notification_type="product_out_of_stock",
                        data={
                            'product_id': instance.id,
                            'stock': 0,
                        },
                        save_to_db=True
                    )
                
                logger.info(f"Notificación de stock enviada: {instance.nombre}")
            
            # Si el stock es bajo (ej: < 5)
            elif instance.stock < 5 and instance.stock > 0:
                admins = User.objects.filter(is_superuser=True, activo=True)
                
                for admin in admins:
                    notification_service.send_to_user(
                        user=admin,
                        title="📉 Stock Bajo",
                        body=f"{instance.nombre} tiene solo {instance.stock} unidades",
                        notification_type="product_low_stock",
                        data={
                            'product_id': instance.id,
                            'stock': instance.stock,
                        },
                        save_to_db=True
                    )
        
        except Exception as e:
            logger.error(f"Error en notificación de stock: {e}")


# ============================================================================
# 8. LOGIN - Registrar en views.py
# ============================================================================

# Este código va en tu views.py de login:
"""
from apps.notifications.services import notification_service

def login_view(request):
    # ... código de login ...
    
    if user_autenticado:
        # Notificar login
        notification_service.send_to_user(
            user=user,
            title="🔐 Nuevo Acceso",
            body="Iniciaste sesión en Smart Sales",
            notification_type="user_login",
            data={
                'timestamp': timezone.now().isoformat(),
                'ip': request.META.get('REMOTE_ADDR'),
            },
            save_to_db=True
        )
"""
