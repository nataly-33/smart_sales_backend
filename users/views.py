from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.decorators import action
from rest_framework import serializers # Para el serializer de assign_permissions

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .serializers import (
    UserSerializer, RoleSerializer, PermissionSerializer,
    LoginSerializer, RoleListSerializer, TokenResponseSerializer, AssignPermissionsSerializer
)
from .services import AuthService, UserService, RoleService, PermissionService, PermissionRoleService
from config.response import (
    SuccessResponse, CreatedResponse, NoContentResponse,
    ErrorResponse, NotFoundResponse, ServerErrorResponse
)
from config.permissions import HasPermission
from .constants.permissions import Permissions 

@extend_schema(tags=['Auth'])
class LoginView(APIView):
    """
    Maneja el inicio de sesión de usuario a través de correo electrónico y contraseña.
    Llama a AuthService para realizar la autenticación y generación de tokens.
    """
    permission_classes = [AllowAny] 

    @extend_schema(
        summary="Inicio de Sesión de Usuario",
        request=LoginSerializer,
        responses={
            200: TokenResponseSerializer, 
            401: ErrorResponse, 
            403: ErrorResponse  
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 

        service_response = AuthService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        return service_response


@extend_schema_view(
    list=extend_schema(summary="Listar usuarios activos", description="Requiere permiso: Mostrar usuarios"),
    retrieve=extend_schema(summary="Obtener un usuario por ID", description="Requiere permiso: Mostrar usuarios"),
    create=extend_schema(summary="Crear un nuevo usuario", description="Requiere permiso: Crear usuarios"),
    update=extend_schema(summary="Actualizar un usuario completo", description="Requiere permiso: Actualizar usuarios"),
    partial_update=extend_schema(summary="Actualizar parcialmente un usuario", description="Requiere permiso: Actualizar usuarios"),
    destroy=extend_schema(summary="Desactivar un usuario (Soft Delete)", description="Requiere permiso: Eliminar usuarios"),
)
@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ViewSet): 
    """
    ViewSet para gestionar Usuarios. Llama a UserService para la lógica.
    """
    serializer_class = UserSerializer 
    permission_classes = [IsAuthenticated, HasPermission] 

    def get_permissions(self):
        """ Asigna el 'permission_required' a la vista dinámicamente. """
        permission_required = None
        if self.action == 'list':
            permission_required = Permissions.USER_SHOW.value
        elif self.action == 'retrieve':
            permission_required = Permissions.USER_SHOW.value
        elif self.action == 'create':
            permission_required = Permissions.USER_CREATE.value
        elif self.action in ['update', 'partial_update']:
            permission_required = Permissions.USER_UPDATE.value
        elif self.action == 'destroy':
            permission_required = Permissions.USER_DELETE.value
        
        self.permission_required = permission_required
        return super().get_permissions()

    def list(self, request):
        filters = {'attr': request.query_params.get('attr'), 'value': request.query_params.get('value')}
        order = request.query_params.get('order')
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset', 0)

        service_response = UserService.list(filters=filters, order=order, limit=limit, offset=offset)
        return service_response

    def retrieve(self, request, pk=None):
        service_response = UserService.retrieve(user_id=pk)
        return service_response

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        service_response = UserService.create(serializer.validated_data)
        return service_response

    def update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, partial=False) 
        serializer.is_valid(raise_exception=True)
        service_response = UserService.update(user_id=pk, validated_data=serializer.validated_data)
        return service_response

    def partial_update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        service_response = UserService.update(user_id=pk, validated_data=serializer.validated_data)
        return service_response

    def destroy(self, request, pk=None):
        service_response = UserService.delete(user_id=pk)
        return service_response


@extend_schema_view(
    list=extend_schema(summary="Listar roles", description="Requiere permiso: Mostrar roles"),
    retrieve=extend_schema(summary="Obtener un rol por ID", description="Requiere permiso: Mostrar roles"),
    create=extend_schema(summary="Crear un nuevo rol", description="Requiere permiso: Crear roles"),
    update=extend_schema(summary="Actualizar nombre de un rol", description="Requiere permiso: Actualizar roles"),
    partial_update=extend_schema(summary="Actualizar nombre de un rol (Parcial)", description="Requiere permiso: Actualizar roles"),
    destroy=extend_schema(summary="Eliminar un rol", description="Requiere permiso: Eliminar roles"),
    assign_permissions=extend_schema(
        summary="Asignar permisos a un rol",
        description="Reemplaza todos los permisos del rol. Requiere permiso: Actualizar roles",
        request=serializers.ListSerializer(child=serializers.UUIDField()), # Expecting a list of permission UUIDs
        responses={200: SuccessResponse, 400: ErrorResponse, 404: NotFoundResponse}
    )
)
@extend_schema(tags=['Roles'])
class RoleViewSet(viewsets.ViewSet):
    """
    ViewSet para gestionar Roles y sus Permisos. Llama a RoleService y PermissionRoleService.
    """
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]

    def get_permissions(self):
        permission_required = None
        if self.action in ['list', 'retrieve']:
            permission_required = Permissions.ROLE_SHOW.value
        elif self.action == 'create':
            permission_required = Permissions.ROLE_CREATE.value
        elif self.action in ['update', 'partial_update', 'assign_permissions']: # Assign needs update permission
            permission_required = Permissions.ROLE_UPDATE.value
        elif self.action == 'destroy':
            permission_required = Permissions.ROLE_DELETE.value

        self.permission_required = permission_required
        return super().get_permissions()

    def list(self, request):
        filters = {'attr': request.query_params.get('attr'), 'value': request.query_params.get('value')}
        order = request.query_params.get('order')
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset', 0)
        service_response = RoleService.list(filters=filters, order=order, limit=limit, offset=offset)
        return service_response

    def retrieve(self, request, pk=None):
        service_response = RoleService.retrieve(role_id=pk)
        return service_response

    def create(self, request):
        serializer = RoleListSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        service_response = RoleService.create(serializer.validated_data)
        return service_response

    def update(self, request, pk=None):
        serializer = RoleListSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        service_response = RoleService.update(role_id=pk, validated_data=serializer.validated_data)
        return service_response

    def destroy(self, request, pk=None):
        service_response = RoleService.delete(role_id=pk)
        return service_response

    

    @action(detail=True, methods=['post'], url_path='assign-permissions')
    def assign_permissions(self, request, pk=None):
        """
        Acción personalizada para asignar/reemplazar permisos de un rol.
        Body esperado: {"permission_ids": ["uuid1", "uuid2", ...]}
        """
        serializer = AssignPermissionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission_ids = serializer.validated_data['permission_ids']

        service_response = PermissionRoleService.assign_permissions_to_role(
            role_id=pk,
            permission_ids=permission_ids
        )
        return service_response

@extend_schema_view(
    list=extend_schema(summary="Listar todos los permisos", description="Requiere permiso: Mostrar permisos"),
    retrieve=extend_schema(summary="Obtener un permiso por ID", description="Requiere permiso: Mostrar permisos"),
    create=extend_schema(summary="Crear un nuevo permiso", description="Requiere permiso: Crear permisos"),
    update=extend_schema(summary="Actualizar un permiso (Completo)", description="Requiere permiso: Actualizar permisos"),
    partial_update=extend_schema(summary="Actualizar un permiso (Parcial)", description="Requiere permiso: Actualizar permisos"),
    destroy=extend_schema(summary="Eliminar un permiso", description="Requiere permiso: Eliminar permisos"),
)
@extend_schema(tags=['Permissions'])
class PermissionViewSet(viewsets.ViewSet): 
    """
    ViewSet para gestionar Permisos con CRUD completo.
    Llama a PermissionService y devuelve la respuesta del servicio directamente.
    """
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission]

    def get_permissions(self):
        """ Asigna permisos dinámicamente. """
        permission_required = None
        if self.action in ['list', 'retrieve']:
            permission_required = Permissions.PERMISSION_SHOW.value
        elif self.action == 'create':
            permission_required = Permissions.PERMISSION_CREATE.value
        elif self.action in ['update', 'partial_update']:
            permission_required = Permissions.PERMISSION_UPDATE.value
        elif self.action == 'destroy':
            permission_required = Permissions.PERMISSION_DELETE.value

        self.permission_required = permission_required
        return super().get_permissions()

    def list(self, request):
        filters = {'attr': request.query_params.get('attr'), 'value': request.query_params.get('value')}
        order = request.query_params.get('order')
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset', 0)
        
        service_response = PermissionService.list(filters=filters, order=order, limit=limit, offset=offset)
        return service_response

    def retrieve(self, request, pk=None):
        service_response = PermissionService.retrieve(permission_id=pk)
        return service_response

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        service_response = PermissionService.create(serializer.validated_data)
        return service_response

    def update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        service_response = PermissionService.update(permission_id=pk, validated_data=serializer.validated_data)
        return service_response

    def partial_update(self, request, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        service_response = PermissionService.update(permission_id=pk, validated_data=serializer.validated_data)
        return service_response

    def destroy(self, request, pk=None):
        service_response = PermissionService.delete(permission_id=pk)
        return service_response

