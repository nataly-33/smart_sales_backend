from rest_framework import serializers
from apps.notifications.models import DeviceToken, Notification, NotificationPreference


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer para tokens de dispositivos"""

    class Meta:
        model = DeviceToken
        fields = [
            'id',
            'token',
            'device_type',
            'device_name',
            'is_active',
            'last_used',
            'created_at'
        ]
        read_only_fields = ['id', 'last_used', 'created_at']

    def create(self, validated_data):
        # Obtener el usuario del contexto
        user = self.context['request'].user

        # Verificar si el token ya existe para este usuario
        token_str = validated_data.get('token')
        existing_token = DeviceToken.objects.filter(
            user=user,
            token=token_str
        ).first()

        if existing_token:
            # Actualizar el token existente
            for attr, value in validated_data.items():
                setattr(existing_token, attr, value)
            existing_token.is_active = True
            existing_token.save()
            return existing_token

        # Crear nuevo token
        validated_data['user'] = user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""

    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'body',
            'notification_type',
            'data',
            'image_url',
            'is_read',
            'read_at',
            'created_at'
        ]
        read_only_fields = ['id', 'read_at', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer para preferencias de notificaciones"""

    class Meta:
        model = NotificationPreference
        fields = [
            'id',
            'order_notifications',
            'payment_notifications',
            'promotion_notifications',
            'stock_notifications',
            'general_notifications',
            'quiet_hours_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class SendNotificationSerializer(serializers.Serializer):
    """Serializer para enviar notificaciones (admin)"""

    user_id = serializers.IntegerField(required=False, help_text="ID del usuario (opcional para envío masivo)")
    title = serializers.CharField(max_length=100, help_text="Título de la notificación")
    body = serializers.CharField(help_text="Cuerpo de la notificación")
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPES,
        default='general',
        help_text="Tipo de notificación"
    )
    data = serializers.JSONField(required=False, default=dict, help_text="Datos adicionales")
    image_url = serializers.URLField(required=False, allow_blank=True, help_text="URL de imagen")
    send_to_all = serializers.BooleanField(default=False, help_text="Enviar a todos los usuarios")
