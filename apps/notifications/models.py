from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class DeviceToken(BaseModel):
    """
    Almacena los tokens FCM de los dispositivos de los usuarios
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        verbose_name='Usuario'
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Token FCM'
    )
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('android', 'Android'),
            ('ios', 'iOS'),
            ('web', 'Web'),
        ],
        default='android',
        verbose_name='Tipo de dispositivo'
    )
    device_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nombre del dispositivo'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    last_used = models.DateTimeField(
        auto_now=True,
        verbose_name='Último uso'
    )

    class Meta:
        db_table = 'device_tokens'
        verbose_name = 'Token de dispositivo'
        verbose_name_plural = 'Tokens de dispositivos'
        ordering = ['-last_used']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.token[:20]}..."


class Notification(BaseModel):
    """
    Almacena el historial de notificaciones enviadas
    """
    NOTIFICATION_TYPES = [
        ('order_created', 'Pedido Creado'),
        ('order_shipped', 'Pedido Enviado'),
        ('order_delivered', 'Pedido Entregado'),
        ('order_cancelled', 'Pedido Cancelado'),
        ('payment_success', 'Pago Exitoso'),
        ('payment_failed', 'Pago Fallido'),
        ('stock_alert', 'Alerta de Stock'),
        ('new_product', 'Nuevo Producto'),
        ('promotion', 'Promoción'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuario',
        null=True,
        blank=True
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Título'
    )
    body = models.TextField(
        verbose_name='Cuerpo'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default='general',
        verbose_name='Tipo de notificación'
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos adicionales'
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL de imagen'
    )

    # Estado de envío
    is_sent = models.BooleanField(
        default=False,
        verbose_name='Enviada'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de envío'
    )

    # Estado de lectura
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leída'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de lectura'
    )

    # Información del envío
    fcm_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Respuesta de FCM'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensaje de error'
    )

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email if self.user else 'Todos'}"

    def mark_as_read(self):
        """Marcar notificación como leída"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])

    def mark_as_sent(self, response=None):
        """Marcar notificación como enviada"""
        from django.utils import timezone
        self.is_sent = True
        self.sent_at = timezone.now()
        if response:
            self.fcm_response = response
        self.save(update_fields=['is_sent', 'sent_at', 'fcm_response'])


class NotificationPreference(BaseModel):
    """
    Preferencias de notificaciones por usuario
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='Usuario'
    )

    # Tipos de notificaciones habilitadas
    order_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificaciones de pedidos'
    )
    payment_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificaciones de pagos'
    )
    promotion_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificaciones de promociones'
    )
    stock_notifications = models.BooleanField(
        default=False,
        verbose_name='Notificaciones de stock'
    )
    general_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificaciones generales'
    )

    # Horario
    quiet_hours_enabled = models.BooleanField(
        default=False,
        verbose_name='Horas silenciosas habilitadas'
    )
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Inicio horas silenciosas'
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Fin horas silenciosas'
    )

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Preferencia de notificación'
        verbose_name_plural = 'Preferencias de notificaciones'

    def __str__(self):
        return f"Preferencias de {self.user.email}"

    def can_receive_notification(self, notification_type):
        """Verifica si el usuario puede recibir un tipo de notificación"""
        type_map = {
            'order_created': self.order_notifications,
            'order_shipped': self.order_notifications,
            'order_delivered': self.order_notifications,
            'order_cancelled': self.order_notifications,
            'payment_success': self.payment_notifications,
            'payment_failed': self.payment_notifications,
            'stock_alert': self.stock_notifications,
            'new_product': self.stock_notifications,
            'promotion': self.promotion_notifications,
            'general': self.general_notifications,
        }
        return type_map.get(notification_type, True)

    def is_in_quiet_hours(self):
        """Verifica si está en horas silenciosas"""
        if not self.quiet_hours_enabled or not self.quiet_hours_start or not self.quiet_hours_end:
            return False

        from django.utils import timezone
        now = timezone.now().time()

        if self.quiet_hours_start < self.quiet_hours_end:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
