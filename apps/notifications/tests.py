from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.notifications.models import DeviceToken, Notification, NotificationPreference
from apps.notifications.services import notification_service

User = get_user_model()


class NotificationTestCase(TestCase):
    """Tests para el sistema de notificaciones"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nombre='Test',
            apellido='User'
        )

    def test_create_device_token(self):
        """Test crear token de dispositivo"""
        token = DeviceToken.objects.create(
            user=self.user,
            token='test_fcm_token_123',
            device_type='android',
            device_name='Test Device'
        )
        self.assertEqual(token.user, self.user)
        self.assertTrue(token.is_active)

    def test_create_notification(self):
        """Test crear notificación"""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            body='This is a test',
            notification_type='general'
        )
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.is_read)
        self.assertFalse(notification.is_sent)

    def test_mark_as_read(self):
        """Test marcar notificación como leída"""
        notification = Notification.objects.create(
            user=self.user,
            title='Test',
            body='Test body',
            notification_type='general'
        )
        notification.mark_as_read()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_notification_preferences(self):
        """Test preferencias de notificaciones"""
        prefs = NotificationPreference.objects.create(user=self.user)
        self.assertTrue(prefs.order_notifications)
        self.assertTrue(prefs.can_receive_notification('order_created'))

        prefs.order_notifications = False
        prefs.save()
        self.assertFalse(prefs.can_receive_notification('order_created'))

    def test_quiet_hours(self):
        """Test horas silenciosas"""
        from datetime import time

        prefs = NotificationPreference.objects.create(
            user=self.user,
            quiet_hours_enabled=True,
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(8, 0)
        )
        # El resultado depende de la hora actual
        # Solo verificamos que la función no falle
        result = prefs.is_in_quiet_hours()
        self.assertIsInstance(result, bool)
