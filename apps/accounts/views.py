from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash

from .models import User, Role, Permission
from .serializers import (
    UserSerializer, UserCreateSerializer, RoleSerializer, 
    PermissionSerializer, CustomTokenObtainPairSerializer,
    RegisterSerializer, ChangePasswordSerializer
)
from apps.core.permissions import IsAdminUser
from .signals import user_logged_in


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login con JWT personalizado"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Si el login fue exitoso, disparar la señal
        if response.status_code == 200:
            # Obtener el usuario desde el serializador
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            
            # Disparar señal de login exitoso
            user_logged_in.send(
                sender=self.__class__,
                user=user,
                request=request
            )
        
        return response


class RegisterViewSet(viewsets.GenericViewSet):
    """Registro de nuevos usuarios (clientes)"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios"""
    queryset = User.objects.filter(deleted_at__isnull=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in [
            'create', 'update', 'partial_update', 'destroy', 'list', 'retrieve'
        ]:
            return [IsAdminUser()]

        if self.action in ['me', 'change_password']:
            return [IsAuthenticated()]

        # Fallback: require authentication
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Cambiar contraseña del usuario actual"""
        user = request.user
        
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar contraseña antigua
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Contraseña actual incorrecta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Mantener la sesión activa después de cambiar la contraseña
        update_session_auth_hash(request, user)
        
        return Response({'message': 'Contraseña actualizada exitosamente'})
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.soft_delete()


class RoleViewSet(viewsets.ModelViewSet):
    """CRUD de roles"""
    queryset = Role.objects.filter(deleted_at__isnull=True)
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def perform_destroy(self, instance):
        """Soft delete"""
        if instance.es_rol_sistema:
            raise serializers.ValidationError("No se puede eliminar un rol del sistema")
        instance.soft_delete()


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Listado de permisos"""
    queryset = Permission.objects.filter(deleted_at__isnull=True)
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]