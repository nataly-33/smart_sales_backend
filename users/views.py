from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import (
    UserSerializer, RoleSerializer, PermissionSerializer,
    LoginSerializer, RoleListSerializer, RoleListSerializer
)
from .services import AuthService, UserService, RoleService, PermissionService, PermissionRoleService
from ..config.response import response, StandardResponseSerializerSuccess, StandardResponseSerializerError
from ..config.permissions import HasPermission
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
            200: StandardResponseSerializerSuccess, 
            401: StandardResponseSerializerError, 
            403: StandardResponseSerializerError  
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 

        service_response = AuthService.login_user(
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
        serializer = self.serializer_class(data=request.data) 
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
    destroy=extend_schema(summary="Eliminar un rol", description="Requiere permiso: Eliminar roles"),
    assign_permissions=extend_schema(
        summary="Asignar permisos a un rol",
        description="Reemplaza todos los permisos del rol. Requiere permiso: Actualizar roles",
        request=serializers.ListSerializer(child=serializers.UUIDField()), # Expecting a list of permission UUIDs
        responses={200: None, 400: None, 404: None}
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
        # Use RoleSerializer without permission_ids for creation of the role itself
        # Or modify RoleSerializer to make permission_ids optional for create
        serializer = RoleListSerializer(data=request.data) # Use simpler serializer for just name
        serializer.is_valid(raise_exception=True)
        service_response = RoleService.create(serializer.validated_data)
        # Note: Permissions are assigned via assign_permissions action after creation
        return service_response

    def update(self, request, pk=None):
        # Update only the role's name
        serializer = RoleListSerializer(data=request.data) # Use simpler serializer for just name
        serializer.is_valid(raise_exception=True)
        service_response = RoleService.update(role_id=pk, validated_data=serializer.validated_data)
        return service_response

    # You might not need partial_update if only 'name' is updatable here
    # def partial_update(self, request, pk=None):
    #     # ... similar to update ...

    def destroy(self, request, pk=None):
        service_response = RoleService.delete(role_id=pk)
        return service_response

    # --- Custom Action for Assigning Permissions ---
    from rest_framework.decorators import action
    from rest_framework import serializers # For request validation

    # Define a simple serializer for the list of UUIDs
    class AssignPermissionsSerializer(serializers.Serializer):
        permission_ids = serializers.ListField(child=serializers.UUIDField())

    @action(detail=True, methods=['post'], url_path='assign-permissions')
    def assign_permissions(self, request, pk=None):
        """
        Custom action to assign/replace permissions for a specific role.
        Expects a JSON body like: {"permission_ids": ["uuid1", "uuid2", ...]}
        """
        serializer = self.AssignPermissionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission_ids = serializer.validated_data['permission_ids']

        # Call the specific service for assigning permissions
        service_response = PermissionRoleService.assign_permissions_to_role(
            role_id=pk,
            permission_ids=permission_ids
        )
        return service_response


@extend_schema_view(
    list=extend_schema(summary="Listar todos los permisos disponibles", description="Requiere permiso: Mostrar permisos"),
    retrieve=extend_schema(summary="Obtener un permiso por ID", description="Requiere permiso: Mostrar permisos"),
    # CRUD for Permissions might be admin-only or internal, hence ReadOnly
    # create=extend_schema(summary="Crear un nuevo permiso"),
    # update=extend_schema(summary="Actualizar un permiso"),
    # destroy=extend_schema(summary="Eliminar un permiso"),
)
@extend_schema(tags=['Permissions'])
class PermissionViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnly: List and Retrieve only
    """
    ViewSet para listar y ver Permisos. Llama a PermissionService.
    La creación/modificación de permisos suele ser una tarea administrativa interna.
    """
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = Permissions.PERMISSION_SHOW.value # Static permission for all read actions

    # Override list and retrieve to use the service layer

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

    # If you need CRUD for permissions, change to ModelViewSet and add permission checks:
    # def create(self, request):
    #     self.permission_required = Permissions.PERMISSION_CREATE.value
    #     self.check_permissions(request) # Manually check permission for non-standard actions
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     service_response = PermissionService.create(serializer.validated_data)
    #     return service_response
    #
    # def update(self, request, pk=None):
    #     # ... similar logic ...
    #
    # def destroy(self, request, pk=None):
    #     # ... similar logic ...