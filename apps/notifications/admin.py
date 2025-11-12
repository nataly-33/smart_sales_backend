from django.contrib import admin
from apps.notifications.models import DeviceToken, Notification, NotificationPreference


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_type', 'device_name', 'is_active', 'last_used', 'created_at']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'user__nombre', 'token', 'device_name']
    readonly_fields = ['created_at', 'updated_at', 'last_used']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user',)
        }),
        ('Información del Dispositivo', {
            'fields': ('token', 'device_type', 'device_name', 'is_active')
        }),
        ('Fechas', {
            'fields': ('last_used', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_sent', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_sent', 'is_read', 'created_at']
    search_fields = ['title', 'body', 'user__email', 'user__nombre']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'read_at', 'fcm_response']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'title', 'body', 'notification_type', 'data', 'image_url')
        }),
        ('Estado de Envío', {
            'fields': ('is_sent', 'sent_at', 'fcm_response', 'error_message')
        }),
        ('Estado de Lectura', {
            'fields': ('is_read', 'read_at')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read', 'resend_notification']

    def mark_as_read(self, request, queryset):
        """Marcar notificaciones como leídas"""
        count = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                count += 1
        self.message_user(request, f'{count} notificaciones marcadas como leídas')
    mark_as_read.short_description = 'Marcar como leídas'

    def resend_notification(self, request, queryset):
        """Reenviar notificaciones"""
        from apps.notifications.services import notification_service

        count = 0
        for notification in queryset:
            if notification.user:
                result = notification_service.send_to_user(
                    user=notification.user,
                    title=notification.title,
                    body=notification.body,
                    notification_type=notification.notification_type,
                    data=notification.data,
                    image_url=notification.image_url,
                    save_to_db=False
                )
                if result.get('success'):
                    count += 1

        self.message_user(request, f'{count} notificaciones reenviadas exitosamente')
    resend_notification.short_description = 'Reenviar notificaciones'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'order_notifications',
        'payment_notifications',
        'promotion_notifications',
        'quiet_hours_enabled'
    ]
    list_filter = [
        'order_notifications',
        'payment_notifications',
        'promotion_notifications',
        'quiet_hours_enabled'
    ]
    search_fields = ['user__email', 'user__nombre']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Tipos de Notificaciones', {
            'fields': (
                'order_notifications',
                'payment_notifications',
                'promotion_notifications',
                'stock_notifications',
                'general_notifications'
            )
        }),
        ('Horas Silenciosas', {
            'fields': (
                'quiet_hours_enabled',
                'quiet_hours_start',
                'quiet_hours_end'
            )
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
