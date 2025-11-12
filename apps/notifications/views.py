from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from apps.notifications.models import DeviceToken, Notification, NotificationPreference
from apps.notifications.serializers import (
    DeviceTokenSerializer,
    NotificationSerializer,
    NotificationPreferenceSerializer,
    SendNotificationSerializer
)
from apps.notifications.services import notification_service


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tokens de dispositivos
    """
    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactivar un token"""
        token = self.get_object()
        token.is_active = False
        token.save()
        return Response({'status': 'Token desactivado'})

    @action(detail=False, methods=['post'])
    def deactivate_all(self, request):
        """Desactivar todos los tokens del usuario"""
        DeviceToken.objects.filter(user=request.user).update(is_active=False)
        return Response({'status': 'Todos los tokens desactivados'})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver notificaciones del usuario
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marcar una notificación como leída"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marcar todas las notificaciones como leídas"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({
            'status': 'success',
            'count': count
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Obtener el conteo de notificaciones no leídas"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'count': count})

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Obtener notificaciones recientes (últimas 20)"""
        notifications = self.get_queryset()[:20]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar preferencias de notificaciones
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_object(self):
        """Obtener o crear preferencias para el usuario"""
        obj, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj

    def list(self, request, *args, **kwargs):
        """Retornar las preferencias del usuario"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Sobrescribir create para usar update en su lugar"""
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Actualizar preferencias"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminNotificationViewSet(viewsets.ViewSet):
    """
    ViewSet para que administradores envíen notificaciones
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def send(self, request):
        """Enviar notificación personalizada"""
        # Verificar que el usuario sea admin
        if not request.user.is_staff and request.user.rol.nombre != 'Admin':
            return Response(
                {'error': 'No tienes permisos para enviar notificaciones'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SendNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        results = []

        if data.get('send_to_all'):
            # Enviar a todos los usuarios
            from apps.accounts.models import User
            users = User.objects.filter(activo=True)

            for user in users:
                result = notification_service.send_to_user(
                    user=user,
                    title=data['title'],
                    body=data['body'],
                    notification_type=data.get('notification_type', 'general'),
                    data=data.get('data'),
                    image_url=data.get('image_url')
                )
                results.append({
                    'user_id': user.id,
                    'success': result.get('success', False)
                })

            return Response({
                'status': 'success',
                'total_sent': len([r for r in results if r['success']]),
                'total_failed': len([r for r in results if not r['success']]),
                'results': results
            })

        elif data.get('user_id'):
            # Enviar a un usuario específico
            from apps.accounts.models import User
            try:
                user = User.objects.get(id=data['user_id'])
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

            result = notification_service.send_to_user(
                user=user,
                title=data['title'],
                body=data['body'],
                notification_type=data.get('notification_type', 'general'),
                data=data.get('data'),
                image_url=data.get('image_url')
            )

            return Response(result)

        else:
            return Response(
                {'error': 'Debes especificar user_id o send_to_all=true'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtener estadísticas de notificaciones"""
        if not request.user.is_staff and request.user.rol.nombre != 'Admin':
            return Response(
                {'error': 'No tienes permisos'},
                status=status.HTTP_403_FORBIDDEN
            )

        from django.db.models import Count
        from datetime import timedelta

        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)

        stats = {
            'total_notifications': Notification.objects.count(),
            'total_sent': Notification.objects.filter(is_sent=True).count(),
            'total_read': Notification.objects.filter(is_read=True).count(),
            'today': Notification.objects.filter(created_at__date=today).count(),
            'last_7_days': Notification.objects.filter(created_at__date__gte=last_7_days).count(),
            'last_30_days': Notification.objects.filter(created_at__date__gte=last_30_days).count(),
            'by_type': list(
                Notification.objects.values('notification_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'total_device_tokens': DeviceToken.objects.count(),
            'active_device_tokens': DeviceToken.objects.filter(is_active=True).count(),
        }

        return Response(stats)
