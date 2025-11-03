from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Carrito, ItemCarrito
from .serializers import (
    CarritoSerializer, ItemCarritoSerializer,
    AgregarItemCarritoSerializer, ActualizarCantidadSerializer
)


class CarritoViewSet(viewsets.GenericViewSet):
    """Gestión del carrito de compras"""
    permission_classes = [IsAuthenticated]
    serializer_class = CarritoSerializer
    
    def get_or_create_carrito(self):
        """Obtener o crear carrito del usuario"""
        carrito, created = Carrito.objects.get_or_create(usuario=self.request.user)
        return carrito
    
    @action(detail=False, methods=['get'])
    def mi_carrito(self, request):
        """Obtener carrito del usuario actual"""
        carrito = self.get_or_create_carrito()
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def agregar(self, request):
        """Agregar item al carrito"""
        serializer = AgregarItemCarritoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        carrito = self.get_or_create_carrito()
        prenda = serializer.validated_data['prenda_obj']
        talla = serializer.validated_data['talla_obj']
        cantidad = serializer.validated_data['cantidad']
        
        with transaction.atomic():
            # Verificar si el item ya existe en el carrito
            item, created = ItemCarrito.objects.get_or_create(
                carrito=carrito,
                prenda=prenda,
                talla=talla,
                deleted_at__isnull=True,
                defaults={'cantidad': cantidad, 'precio_unitario': prenda.precio}
            )
            
            if not created:
                # Si ya existe, aumentar la cantidad
                nueva_cantidad = item.cantidad + cantidad
                
                # Verificar stock nuevamente
                from apps.products.models import StockPrenda
                stock = StockPrenda.objects.filter(prenda=prenda, talla=talla).first()
                
                if not stock or stock.cantidad < nueva_cantidad:
                    disponible = stock.cantidad if stock else 0
                    return Response({
                        'error': f'Stock insuficiente. Solo hay {disponible} unidades disponibles y ya tienes {item.cantidad} en el carrito'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                item.cantidad = nueva_cantidad
                item.save()
        
        # Devolver el carrito actualizado
        carrito_serializer = CarritoSerializer(carrito)
        return Response({
            'message': 'Producto agregado al carrito',
            'carrito': carrito_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['put'])
    def actualizar_item(self, request):
        """Actualizar cantidad de un item del carrito"""
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {'error': 'item_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        carrito = self.get_or_create_carrito()
        
        try:
            item = ItemCarrito.objects.get(
                id=item_id,
                carrito=carrito,
                deleted_at__isnull=True
            )
        except ItemCarrito.DoesNotExist:
            return Response(
                {'error': 'Item no encontrado en el carrito'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ActualizarCantidadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nueva_cantidad = serializer.validated_data['cantidad']
        
        # Verificar stock
        tiene_stock, mensaje = item.verificar_stock()
        if not tiene_stock:
            return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)
        
        from apps.products.models import StockPrenda
        stock = StockPrenda.objects.filter(
            prenda=item.prenda,
            talla=item.talla
        ).first()
        
        if stock.cantidad < nueva_cantidad:
            return Response({
                'error': f'Stock insuficiente. Solo hay {stock.cantidad} unidades disponibles'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        item.cantidad = nueva_cantidad
        item.save()
        
        # Devolver el carrito actualizado
        carrito_serializer = CarritoSerializer(carrito)
        return Response({
            'message': 'Cantidad actualizada',
            'carrito': carrito_serializer.data
        })
    
    @action(detail=False, methods=['delete'])
    def eliminar_item(self, request):
        """Eliminar item del carrito"""
        item_id = request.query_params.get('item_id')
        
        if not item_id:
            return Response(
                {'error': 'item_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        carrito = self.get_or_create_carrito()
        
        try:
            item = ItemCarrito.objects.get(
                id=item_id,
                carrito=carrito,
                deleted_at__isnull=True
            )
            item.soft_delete()
            
            # Devolver el carrito actualizado
            carrito_serializer = CarritoSerializer(carrito)
            return Response({
                'message': 'Producto eliminado del carrito',
                'carrito': carrito_serializer.data
            })
            
        except ItemCarrito.DoesNotExist:
            return Response(
                {'error': 'Item no encontrado en el carrito'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def limpiar(self, request):
        """Vaciar el carrito"""
        carrito = self.get_or_create_carrito()
        carrito.limpiar()
        
        carrito_serializer = CarritoSerializer(carrito)
        return Response({
            'message': 'Carrito vaciado',
            'carrito': carrito_serializer.data
        })