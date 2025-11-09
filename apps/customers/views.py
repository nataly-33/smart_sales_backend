from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Direccion, Favoritos
from .serializers import (
    DireccionSerializer, CustomerProfileSerializer,
    FavoritosSerializer
)
from apps.core.permissions import IsOwnerOrAdmin


class CustomerProfileViewSet(viewsets.GenericViewSet):
    """Gestión del perfil del cliente"""
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Obtener o actualizar perfil del cliente actual"""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        else:  # PUT o PATCH
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(
                request.user, 
                data=request.data, 
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def wallet(self, request):
        """Ver saldo de billetera"""
        # TODO: Implementar cuando se agregue el modelo de Wallet
        return Response({
            'message': 'Funcionalidad de billetera no disponible'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class DireccionViewSet(viewsets.ModelViewSet):
    """CRUD de direcciones del cliente"""
    serializer_class = DireccionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Cada usuario solo ve sus propias direcciones
        return Direccion.objects.filter(
            usuario=self.request.user,
            deleted_at__isnull=True
        )
    
    @action(detail=True, methods=['post'])
    def set_principal(self, request, pk=None):
        """Marcar una dirección como principal"""
        direccion = self.get_object()
        
        # Desmarcar todas las direcciones principales del usuario
        Direccion.objects.filter(
            usuario=request.user,
            es_principal=True
        ).update(es_principal=False)
        
        # Marcar esta como principal
        direccion.es_principal = True
        direccion.save()
        
        serializer = self.get_serializer(direccion)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        # No permitir eliminar la dirección principal si tiene otras
        if instance.es_principal:
            otras_direcciones = Direccion.objects.filter(
                usuario=instance.usuario,
                deleted_at__isnull=True
            ).exclude(id=instance.id)
            
            if otras_direcciones.exists():
                # Marcar otra como principal
                nueva_principal = otras_direcciones.first()
                nueva_principal.es_principal = True
                nueva_principal.save()
        
        instance.soft_delete()


class FavoritosViewSet(viewsets.ModelViewSet):
    """Gestión de productos favoritos"""
    serializer_class = FavoritosSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']  # Solo GET, POST, DELETE
    
    def get_queryset(self):
        return Favoritos.objects.filter(
            usuario=self.request.user,
            deleted_at__isnull=True
        ).select_related('prenda', 'prenda__marca')
    
    def create(self, request, *args, **kwargs):
        """Agregar a favoritos"""
        prenda_id = request.data.get('prenda')
        
        # Verificar si ya existe
        existe = Favoritos.objects.filter(
            usuario=request.user,
            prenda_id=prenda_id,
            deleted_at__isnull=True
        ).exists()
        
        if existe:
            return Response(
                {'message': 'Este producto ya está en favoritos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Agregar o quitar de favoritos (toggle)"""
        prenda_id = request.data.get('prenda')
        
        if not prenda_id:
            return Response(
                {'error': 'prenda es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        favorito = Favoritos.objects.filter(
            usuario=request.user,
            prenda_id=prenda_id,
            deleted_at__isnull=True
        ).first()
        
        if favorito:
            # Eliminar de favoritos
            favorito.soft_delete()
            return Response({
                'message': 'Producto eliminado de favoritos',
                'en_favoritos': False
            })
        else:
            # Agregar a favoritos
            favorito = Favoritos.objects.create(
                usuario=request.user,
                prenda_id=prenda_id
            )
            serializer = self.get_serializer(favorito)
            return Response({
                'message': 'Producto agregado a favoritos',
                'en_favoritos': True,
                'favorito': serializer.data
            }, status=status.HTTP_201_CREATED)
    
    def perform_destroy(self, instance):
        instance.soft_delete()