from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

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
    
    def mi_carrito(self, request):
        """Obtener carrito del usuario actual"""
        carrito = self.get_or_create_carrito()
                
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)
    
    def agregar(self, request):
        """Agregar item al carrito"""
        logger.info(f"POST agregar - User: {request.user.id}, Data: {request.data}")
        serializer = AgregarItemCarritoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        carrito = self.get_or_create_carrito()
        prenda = serializer.validated_data['prenda_obj']
        talla = serializer.validated_data['talla_obj']
        cantidad = serializer.validated_data['cantidad']
        
        with transaction.atomic():
            # Buscar item existente (incluyendo los eliminados lógicamente)
            item_existente = ItemCarrito.objects.filter(
                carrito=carrito,
                prenda=prenda,
                talla=talla
            ).first()
            
            if item_existente and item_existente.deleted_at is None:
                # Si ya existe y no está eliminado, aumentar la cantidad
                nueva_cantidad = item_existente.cantidad + cantidad
                
                # Verificar stock
                from apps.products.models import StockPrenda
                stock = StockPrenda.objects.filter(prenda=prenda, talla=talla).first()
                
                if not stock or stock.cantidad < nueva_cantidad:
                    disponible = stock.cantidad if stock else 0
                    return Response({
                        'error': f'Stock insuficiente. Solo hay {disponible} unidades disponibles y ya tienes {item_existente.cantidad} en el carrito'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                item_existente.cantidad = nueva_cantidad
                item_existente.save()
                item = item_existente
                
            elif item_existente and item_existente.deleted_at is not None:
                # Si existe pero está eliminado, reactivarlo
                item_existente.deleted_at = None
                item_existente.cantidad = cantidad
                item_existente.precio_unitario = prenda.precio
                item_existente.save()
                item = item_existente
            else:
                # Crear nuevo item
                item = ItemCarrito.objects.create(
                    carrito=carrito,
                    prenda=prenda,
                    talla=talla,
                    cantidad=cantidad,
                    precio_unitario=prenda.precio
                )
        
        # Actualizar el total del carrito
        carrito.actualizar_total()
        
        # Devolver el carrito actualizado
        carrito_serializer = CarritoSerializer(carrito)
        logger.info(f"Item agregado - Carrito total: {carrito.total}")
        return Response({
            'message': 'Producto agregado al carrito',
            'carrito': carrito_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def actualizar_item(self, request, item_id=None):
        """Actualizar cantidad de un item del carrito"""
        logger.info(f"PUT actualizar_item - User: {request.user.id}, Item: {item_id}, Data: {request.data}")
        
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
            logger.info(f"Item encontrado: {item.id} - {item.prenda.nombre}")
        except ItemCarrito.DoesNotExist:
            logger.error(f"Item no encontrado: {item_id} para usuario {request.user.id}")
            return Response(
                {'error': 'Item no encontrado en el carrito'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ActualizarCantidadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nueva_cantidad = serializer.validated_data['cantidad']
        
        # Verificar stock
        from apps.products.models import StockPrenda
        stock = StockPrenda.objects.filter(
            prenda=item.prenda,
            talla=item.talla
        ).first()
        
        if not stock:
            return Response({
                'error': 'Producto no disponible'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if stock.cantidad < nueva_cantidad:
            return Response({
                'error': f'Stock insuficiente. Solo hay {stock.cantidad} unidades disponibles'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if nueva_cantidad == 0:
            # Si la cantidad es 0, eliminar el item
            item.soft_delete()
            message = 'Item eliminado del carrito'
        else:
            item.cantidad = nueva_cantidad
            item.save()
            message = 'Cantidad actualizada'
        
        # Devolver el carrito actualizado
        carrito_serializer = CarritoSerializer(carrito)
        return Response({
            'message': message,
            'carrito': carrito_serializer.data
        })
    
    def eliminar_item(self, request, item_id=None):
        """Eliminar item del carrito"""        
        if not item_id:
            return Response(
                {'error': 'item_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        carrito = self.get_or_create_carrito()
        logger.info(f"Buscando item {item_id} en carrito {carrito.id}")
        
        try:
            item = ItemCarrito.objects.get(
                id=item_id,
                carrito=carrito,
                deleted_at__isnull=True
            )
            logger.info(f"✅ Item encontrado para eliminar: {item.id} - {item.prenda.nombre}")
            
            item.soft_delete()
            
            carrito_serializer = CarritoSerializer(carrito)
            logger.info(f"✅ Item eliminado - Carrito total: {carrito.total}")
            return Response({
                'message': 'Producto eliminado del carrito',
                'carrito': carrito_serializer.data
            })
            
        except ItemCarrito.DoesNotExist as e:
            logger.error(f"❌ Error completo: {str(e)}")
            items_en_carrito = ItemCarrito.objects.filter(carrito=carrito, deleted_at__isnull=True)
            
            return Response(
                {'error': 'Item no encontrado en el carrito'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def limpiar(self, request):
        """Vaciar el carrito"""
        carrito = self.get_or_create_carrito()
        carrito.limpiar()
        
        carrito_serializer = CarritoSerializer(carrito)
        return Response({
            'message': 'Carrito vaciado',
            'carrito': carrito_serializer.data
        })