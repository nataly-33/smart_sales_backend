from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerProfileViewSet, DireccionViewSet, FavoritosViewSet

router = DefaultRouter()
router.register(r'profile', CustomerProfileViewSet, basename='customer-profile')
router.register(r'addresses', DireccionViewSet, basename='address')
router.register(r'favorites', FavoritosViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]