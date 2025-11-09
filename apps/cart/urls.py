from django.urls import path
from .views import CarritoViewSet
from django.http import JsonResponse

urlpatterns = [
    path('mi_carrito/', CarritoViewSet.as_view({'get': 'mi_carrito'}), name='mi-carrito'),
    path('agregar/', CarritoViewSet.as_view({'post': 'agregar'}), name='agregar-item'),
    path('items/<uuid:item_id>/actualizar/', CarritoViewSet.as_view({'put': 'actualizar_item'}), name='actualizar-item'),
    path('items/<uuid:item_id>/eliminar/', CarritoViewSet.as_view({'delete': 'eliminar_item'}), name='eliminar-item'),
    path('limpiar/', CarritoViewSet.as_view({'post': 'limpiar'}), name='limpiar-carrito'),
]