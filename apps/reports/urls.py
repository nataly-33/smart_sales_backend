"""
URLs para la app de reportes
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ReportsViewSet, AnalyticsViewSet

# Crear router
router = DefaultRouter()
router.register(r'reports', ReportsViewSet, basename='reports')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]
