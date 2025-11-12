"""
Servicio de notificaciones push con Firebase Cloud Messaging (FCM)
"""
import logging
from typing import List, Dict, Optional, Union
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Intentar importar firebase-admin
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("firebase-admin no está instalado. Las notificaciones push no estarán disponibles.")


class FCMService:
    """
    Servicio para enviar notificaciones push usando Firebase Cloud Messaging
    """

    def __init__(self):
        self.initialized = False
        if FIREBASE_AVAILABLE:
            self._initialize_firebase()

    def _initialize_firebase(self):
        """Inicializa Firebase Admin SDK"""
        if self.initialized or not FIREBASE_AVAILABLE:
            return

        try:
            # Verificar si ya está inicializado
            firebase_admin.get_app()
            self.initialized = True
            logger.info("Firebase ya estaba inicializado")
        except ValueError:
            # No está inicializado, inicializar ahora
            try:
                # Opción 1: Usar archivo de credenciales
                firebase_cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
                if firebase_cred_path:
                    cred = credentials.Certificate(firebase_cred_path)
                    firebase_admin.initialize_app(cred)
                    self.initialized = True
                    logger.info("Firebase inicializado con archivo de credenciales")

                # Opción 2: Usar credenciales de variables de entorno
                elif hasattr(settings, 'FIREBASE_CREDENTIALS_DICT'):
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_DICT)
                    firebase_admin.initialize_app(cred)
                    self.initialized = True
                    logger.info("Firebase inicializado con diccionario de credenciales")

                else:
                    logger.warning("No se encontraron credenciales de Firebase configuradas")

            except Exception as e:
                logger.error(f"Error al inicializar Firebase: {e}")
                self.initialized = False

    def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Envía una notificación push a un dispositivo específico

        Args:
            token: Token FCM del dispositivo
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
            image_url: URL de imagen (opcional)

        Returns:
            Dict con el resultado del envío
        """
        if not FIREBASE_AVAILABLE:
            return {
                'success': False,
                'error': 'Firebase no está disponible'
            }

        if not self.initialized:
            self._initialize_firebase()
            if not self.initialized:
                return {
                    'success': False,
                    'error': 'Firebase no está inicializado'
                }

        try:
            # Construir el mensaje
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url if image_url else None
                ),
                data=data if data else {},
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        color='#FF6B6B'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )

            # Enviar el mensaje
            response = messaging.send(message)

            logger.info(f"Notificación enviada exitosamente: {response}")

            return {
                'success': True,
                'message_id': response,
                'token': token
            }

        except messaging.UnregisteredError:
            logger.warning(f"Token no registrado o inválido: {token}")
            return {
                'success': False,
                'error': 'Token no registrado',
                'token': token,
                'should_delete_token': True
            }

        except Exception as e:
            logger.error(f"Error al enviar notificación: {e}")
            return {
                'success': False,
                'error': str(e),
                'token': token
            }

    def send_multicast_notification(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Envía una notificación a múltiples dispositivos

        Args:
            tokens: Lista de tokens FCM
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
            image_url: URL de imagen (opcional)

        Returns:
            Dict con el resultado del envío
        """
        if not FIREBASE_AVAILABLE:
            return {
                'success': False,
                'error': 'Firebase no está disponible'
            }

        if not self.initialized:
            self._initialize_firebase()
            if not self.initialized:
                return {
                    'success': False,
                    'error': 'Firebase no está inicializado'
                }

        if not tokens:
            return {
                'success': False,
                'error': 'No se proporcionaron tokens'
            }

        try:
            # Construir el mensaje multicast
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url if image_url else None
                ),
                data=data if data else {},
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        color='#FF6B6B'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )

            # Enviar el mensaje
            response = messaging.send_multicast(message)

            logger.info(
                f"Notificaciones enviadas: {response.success_count} exitosas, "
                f"{response.failure_count} fallidas"
            )

            # Procesar tokens que fallaron
            failed_tokens = []
            if response.failure_count > 0:
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        failed_tokens.append({
                            'token': tokens[idx],
                            'error': str(resp.exception)
                        })

            return {
                'success': True,
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'failed_tokens': failed_tokens
            }

        except Exception as e:
            logger.error(f"Error al enviar notificaciones multicast: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Envía una notificación a todos los dispositivos suscritos a un topic

        Args:
            topic: Nombre del topic
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
            image_url: URL de imagen (opcional)

        Returns:
            Dict con el resultado del envío
        """
        if not FIREBASE_AVAILABLE:
            return {
                'success': False,
                'error': 'Firebase no está disponible'
            }

        if not self.initialized:
            self._initialize_firebase()
            if not self.initialized:
                return {
                    'success': False,
                    'error': 'Firebase no está inicializado'
                }

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url if image_url else None
                ),
                data=data if data else {},
                topic=topic,
            )

            response = messaging.send(message)

            logger.info(f"Notificación enviada al topic {topic}: {response}")

            return {
                'success': True,
                'message_id': response,
                'topic': topic
            }

        except Exception as e:
            logger.error(f"Error al enviar notificación al topic: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class NotificationService:
    """
    Servicio de alto nivel para gestionar notificaciones
    """

    def __init__(self):
        self.fcm_service = FCMService()

    def send_to_user(
        self,
        user,
        title: str,
        body: str,
        notification_type: str = 'general',
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        save_to_db: bool = True
    ) -> Dict:
        """
        Envía una notificación a un usuario específico

        Args:
            user: Usuario destino
            title: Título de la notificación
            body: Cuerpo de la notificación
            notification_type: Tipo de notificación
            data: Datos adicionales
            image_url: URL de imagen
            save_to_db: Si se debe guardar en BD

        Returns:
            Dict con el resultado del envío
        """
        from apps.notifications.models import Notification, DeviceToken, NotificationPreference

        # Verificar preferencias del usuario
        try:
            prefs = user.notification_preferences
            if not prefs.can_receive_notification(notification_type):
                return {
                    'success': False,
                    'error': 'Usuario no desea recibir este tipo de notificaciones'
                }

            if prefs.is_in_quiet_hours():
                return {
                    'success': False,
                    'error': 'Usuario en horas silenciosas'
                }
        except NotificationPreference.DoesNotExist:
            # Si no tiene preferencias, crear con valores por defecto
            NotificationPreference.objects.create(user=user)

        # Obtener tokens activos del usuario
        tokens = list(
            DeviceToken.objects.filter(user=user, is_active=True)
            .values_list('token', flat=True)
        )

        if not tokens:
            return {
                'success': False,
                'error': 'Usuario no tiene tokens activos'
            }

        # Guardar notificación en BD si se solicita
        notification = None
        if save_to_db:
            notification = Notification.objects.create(
                user=user,
                title=title,
                body=body,
                notification_type=notification_type,
                data=data or {},
                image_url=image_url
            )

        # Enviar notificación
        if len(tokens) == 1:
            result = self.fcm_service.send_notification(
                token=tokens[0],
                title=title,
                body=body,
                data=data,
                image_url=image_url
            )
        else:
            result = self.fcm_service.send_multicast_notification(
                tokens=tokens,
                title=title,
                body=body,
                data=data,
                image_url=image_url
            )

        # Actualizar notificación en BD
        if notification and result.get('success'):
            notification.mark_as_sent(result)

        return result

    def send_order_notification(self, order, status: str):
        """Envía notificación específica de pedido"""
        status_messages = {
            'created': {
                'title': '🎉 ¡Pedido Confirmado!',
                'body': f'Tu pedido #{order.numero_pedido} ha sido confirmado exitosamente.'
            },
            'shipped': {
                'title': '📦 Pedido Enviado',
                'body': f'Tu pedido #{order.numero_pedido} está en camino.'
            },
            'delivered': {
                'title': '✅ Pedido Entregado',
                'body': f'Tu pedido #{order.numero_pedido} ha sido entregado.'
            },
            'cancelled': {
                'title': '❌ Pedido Cancelado',
                'body': f'Tu pedido #{order.numero_pedido} ha sido cancelado.'
            }
        }

        msg = status_messages.get(status, {})
        if not msg:
            return

        return self.send_to_user(
            user=order.usuario,
            title=msg['title'],
            body=msg['body'],
            notification_type=f'order_{status}',
            data={
                'order_id': str(order.id),
                'order_number': order.numero_pedido,
                'status': status
            }
        )


# Instancia global del servicio
notification_service = NotificationService()
