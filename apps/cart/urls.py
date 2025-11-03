from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarritoViewSet

router = DefaultRouter()
router.register(r'', CarritoViewSet, basename='carrito')

urlpatterns = [
    path('', include(router.urls)),
]