from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, MarcaViewSet, TallaViewSet, PrendaViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'marcas', MarcaViewSet, basename='marca')
router.register(r'tallas', TallaViewSet, basename='talla')
router.register(r'prendas', PrendaViewSet, basename='prenda')

urlpatterns = [
    path('', include(router.urls)),
]