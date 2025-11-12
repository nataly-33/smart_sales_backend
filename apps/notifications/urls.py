from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.notifications.views import (
    DeviceTokenViewSet,
    NotificationViewSet,
    NotificationPreferenceViewSet,
    AdminNotificationViewSet
)

router = DefaultRouter()
router.register(r'device-tokens', DeviceTokenViewSet, basename='device-token')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'admin', AdminNotificationViewSet, basename='admin-notification')

urlpatterns = [
    path('', include(router.urls)),
]
