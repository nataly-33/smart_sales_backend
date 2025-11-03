from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Categoria, Marca, Talla, Prenda, StockPrenda, ImagenPrenda
from .serializers import (
    CategoriaSerializer, MarcaSerializer, TallaSerializer,
    PrendaListSerializer, PrendaDetailSerializer, PrendaCreateUpdateSerializer,
    StockPrendaSerializer, ImagenPrendaSerializer
)
from apps.core.permissions import IsAdminUser, IsEmpleadoOrAdmin


class CategoriaViewSet(viewsets.ModelViewSet):
    """CRUD de categorías"""
    queryset = Categoria.objects.filter(deleted_at__isnull=True)
    serializer_class = CategoriaSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsEmpleadoOrAdmin()]
    
    def perform_destroy(self, instance):
        instance.soft_delete()


class MarcaViewSet(viewsets.ModelViewSet):
    """CRUD de marcas"""
    queryset = Marca.objects.filter(deleted_at__isnull=True)
    serializer_class = MarcaSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsEmpleadoOrAdmin()]
    
    def perform_destroy(self, instance):
        instance.soft_delete()


class TallaViewSet(viewsets.ModelViewSet):
    """CRUD de tallas"""
    queryset = Talla.objects.filter(deleted_at__isnull=True)
    serializer_class = TallaSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def perform_destroy(self, instance):
        instance.soft_delete()


class PrendaViewSet(viewsets.ModelViewSet):
    """CRUD de prendas con filtros avanzados"""
    queryset = Prenda.objects.filter(deleted_at__isnull=True, activa=True).prefetch_related(
        'marca', 'categorias', 'tallas_disponibles', 'imagenes', 'stocks'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['marca', 'categorias', 'color', 'destacada', 'es_novedad']
    search_fields = ['nombre', 'descripcion', 'color']
    ordering_fields = ['precio', 'created_at', 'nombre']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PrendaListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PrendaCreateUpdateSerializer
        return PrendaDetailSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search']:
            return [AllowAny()]
        return [IsEmpleadoOrAdmin()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por rango de precio
        precio_min = self.request.query_params.get('precio_min')
        precio_max = self.request.query_params.get('precio_max')
        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)
        
        # Filtro por talla
        talla = self.request.query_params.get('talla')
        if talla:
            queryset = queryset.filter(tallas_disponibles__id=talla)
        
        # Filtro por disponibilidad
        solo_con_stock = self.request.query_params.get('con_stock')
        if solo_con_stock == 'true':
            queryset = queryset.filter(stocks__cantidad__gt=0).distinct()
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def destacadas(self, request):
        """Obtener prendas destacadas"""
        prendas = self.get_queryset().filter(destacada=True)[:12]
        serializer = PrendaListSerializer(prendas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def novedades(self, request):
        """Obtener novedades"""
        prendas = self.get_queryset().filter(es_novedad=True)[:12]
        serializer = PrendaListSerializer(prendas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def agregar_imagen(self, request, pk=None):
        """Agregar imagen a una prenda"""
        prenda = self.get_object()
        serializer = ImagenPrendaSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(prenda=prenda)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'put'])
    def stock(self, request, pk=None):
        """Ver o actualizar stock de una prenda"""
        prenda = self.get_object()
        
        if request.method == 'GET':
            stocks = prenda.stocks.all()
            serializer = StockPrendaSerializer(stocks, many=True)
            return Response({
                'prenda': prenda.nombre,
                'stock_total': prenda.stock_total,
                'stocks_por_talla': serializer.data
            })
        
        elif request.method == 'PUT':
            # Actualizar stocks
            stocks_data = request.data.get('stocks', [])
            for stock_data in stocks_data:
                talla_id = stock_data.get('talla')
                cantidad = stock_data.get('cantidad')
                
                stock, created = StockPrenda.objects.get_or_create(
                    prenda=prenda,
                    talla_id=talla_id,
                    defaults={'cantidad': cantidad}
                )
                if not created:
                    stock.cantidad = cantidad
                    stock.save()
            
            stocks = prenda.stocks.all()
            serializer = StockPrendaSerializer(stocks, many=True)
            return Response(serializer.data)
    
    def perform_destroy(self, instance):
        instance.soft_delete()