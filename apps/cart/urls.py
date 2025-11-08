from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarritoViewSet

router = DefaultRouter()
router.register(r'', CarritoViewSet, basename='carrito')

urlpatterns = [
    path('', include(router.urls)),
    # Direct access to cart item operations with path parameters
    path('items/<uuid:item_id>/actualizar/', CarritoViewSet.as_view({'put': 'actualizar_item'}), name='actualizar-item'),
    path('items/<uuid:item_id>/eliminar/', CarritoViewSet.as_view({'delete': 'eliminar_item'}), name='eliminar-item'),
]