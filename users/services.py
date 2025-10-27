from django.contrib.auth import authenticate
from config.response import (
    SuccessResponse, CreatedResponse, NoContentResponse,
    ErrorResponse, UnauthorizedResponse, ForbiddenResponse, NotFoundResponse,
    ServerErrorResponse
)
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Role, Permission
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer
from django.core.exceptions import ObjectDoesNotExist, ValidationError

class AuthService:
    @staticmethod
    def login(email, password):
        """
        Autenticar a un usuario y devolver tokens JWT.
        """
        user = authenticate(username=email, password=password)
        if not user:
            return UnauthorizedResponse('Credenciales inválidas, inténtalo de nuevo.')
        if not user.is_active:
            return ForbiddenResponse('La cuenta de usuario está deshabilitada.')

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        return SuccessResponse(
            message="Login exitoso",
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data
            }
        )

class UserService:
    """
    Servicio para manejar operaciones relacionadas con usuarios.
    """
    @staticmethod
    def create(validated_data):
        """
        Crea un nuevo usuario y asigna un rol.
        """
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)

        email = validated_data.get('email')
        if User.objects.filter(email=email).exists():
            return ErrorResponse(message=f"El correo electrónico '{email}' ya está registrado.")
        
        try:
            user = User(**validated_data)
            if password:
                user.set_password(password)

            if role:
                user.role = role
            user.save()
            user_data = UserSerializer(user).data

            return CreatedResponse(message="Usuario creado exitosamente", data=user_data)
        
        except Exception as e:
            return ServerErrorResponse(f"Error al crear usuario: {str(e)}")

    @staticmethod
    def update(user_id, validated_data):
        """
        Actualiza un usuario existente y maneja las actualizaciones de contraseña.
        """
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return NotFoundResponse("Usuario no encontrado.")

        new_email = validated_data.get('email')
        if new_email and new_email != user.email and User.objects.filter(email=new_email).exclude(id=user_id).exists():
            return ErrorResponse(message=f"El email '{new_email}' ya está en uso por otro usuario.")

        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)

        try:
            for attr, value in validated_data.items():
                setattr(user, attr, value)

            if password:
                user.set_password(password)

            if role:
                user.role = role

            user.save()
            user_data = UserSerializer(user).data
            return SuccessResponse(message="Usuario actualizado exitosamente", data=user_data)
        except Exception as e:
            return ServerErrorResponse(f"Error al actualizar usuario: {str(e)}")
    
    @staticmethod
    def list(filters=None, order=None, limit=None, offset=0):
        """
        Listar todos los usuarios con filtros, ordenamiento y paginación opcionales.
        """
        try:
            queryset = User.objects.filter(is_active=True)

            if filters:
                attr = filters.get('attr')
                value = filters.get('value')
                if attr and value:
                    valid_user_attrs = [f.name for f in User._meta.get_fields()]
                    valid_role_attrs = [f'role__{f.name}' for f in Role._meta.get_fields()]
                    valid_attrs = valid_user_attrs + valid_role_attrs

                    if attr not in valid_attrs:
                        return ErrorResponse(message=f"El campo '{attr}' no es válido para filtrado en Usuario o Rol.")

                    filter_kwargs = {f"{attr}__icontains": value}
                    queryset = queryset.filter(**filter_kwargs)

            if order:
                valid_order_fields = [f.name for f in User._meta.get_fields()] + [f'-{f.name}' for f in User._meta.get_fields()] + \
                                     [f'role__{f.name}' for f in Role._meta.get_fields()] + [f'-role__{f.name}' for f in Role._meta.get_fields()]
                if order not in valid_order_fields:
                    return ErrorResponse(message=f"No se puede ordenar por '{order}'. Campo inválido.")
                queryset = queryset.order_by(order)
            else:
                queryset = queryset.order_by('name') # Orden por defecto

            total_count = queryset.count()

            if limit is not None:
                try:
                    limit = int(limit)
                    offset = int(offset)
                    if limit <= 0 or offset < 0:
                            raise ValueError("Limit debe ser > 0 y offset >= 0")
                    queryset = queryset[offset : offset + limit]
                except ValueError:
                    return ErrorResponse(message="Los valores de limit y offset deben ser enteros")
            
            user_data = UserSerializer(queryset, many=True).data

            return SuccessResponse(message="Usuarios encontrados", data=user_data)
        except Exception as e:
            return ServerErrorResponse(f"Error al listar usuarios: {str(e)}")

    @staticmethod
    def retrieve(user_id):
        """
        Listar un usuario específico por ID.
        """
        try:
            user = User.objects.get(id=user_id, is_active=True)
            user_data = UserSerializer(user).data
            return SuccessResponse(message="Usuario encontrado.", data=user_data)
        except User.DoesNotExist:
            return NotFoundResponse("Usuario no encontrado.")
        except Exception as e:
            return ServerErrorResponse(f"Error al obtener usuario: {str(e)}")

    @staticmethod
    def delete(user_id): 
        """
        Eliminar (soft delete) un usuario marcándolo como inactivo.
        """
        try:
            user = User.objects.get(id=user_id) 
            if not user.is_active:
                return NotFoundResponse("Usuario no encontrado o ya está eliminado.")
            user.is_active = False
            user.save(update_fields=['is_active'])
            return NoContentResponse(message="Usuario eliminado exitosamente (soft delete).")
        except User.DoesNotExist:
            return NotFoundResponse("Usuario no encontrado.")
        except Exception as e:
            return ServerErrorResponse(f"Error al eliminar usuario: {str(e)}")

class RoleService:
    @staticmethod
    def create(validated_data):
        """
        Crea un nuevo rol. Los permisos se asignan por separado.
        """
        name = validated_data.get('name')
        if Role.objects.filter(name=name).exists():
            return ErrorResponse(message=f"El rol '{name}' ya existe.")

        try:
            role = Role.objects.create(**validated_data)
            role_data = RoleSerializer(role).data
            return CreatedResponse(message="Rol creado exitosamente.", data=role_data)
        except Exception as e:
            return ServerErrorResponse(f"Error al crear rol: {str(e)}")

    @staticmethod
    def list(filters=None, order=None, limit=None, offset=0):
        """
        Lista roles con filtros, ordenamiento y paginación. Incluye permisos asociados.
        """
        try:
            queryset = Role.objects.prefetch_related('permissions') 

            if filters:
                attr = filters.get('attr')
                value = filters.get('value')
                if attr == 'name' and value:
                    queryset = queryset.filter(name__icontains=value)
                elif attr:
                    return ErrorResponse(message=f"Filtrado por '{attr}' no soportado en Roles.")

            if order and order in ['name', '-name']:
                queryset = queryset.order_by(order)
            else:
                queryset = queryset.order_by('name')

            total_count = queryset.count()

            if limit is not None:
                try:
                    limit = int(limit)
                    offset = int(offset)
                    if limit <= 0 or offset < 0:
                            raise ValueError("Limit debe ser > 0 y offset >= 0")
                    queryset = queryset[offset : offset + limit]
                except ValueError:
                    return ErrorResponse("Los valores de limit y offset deben ser enteros")
            
            data = RoleSerializer(queryset, many=True).data    

            return SuccessResponse(message="Roles encontrados", data=data)
        except Exception as e:
            return ServerErrorResponse(f"Error al listar roles: {str(e)}")

    @staticmethod
    def retrieve(role_id):
        """
        Obtiene un rol específico por ID, incluyendo sus permisos.
        """
        try:
            role = Role.objects.prefetch_related('permissions').get(id=role_id)
            role_data = RoleSerializer(role).data
            return SuccessResponse(message="Rol encontrado.", data=role_data)
        except Role.DoesNotExist:
            return NotFoundResponse("Rol no encontrado.")
        except Exception as e:
            return ServerErrorResponse(f"Error al obtener rol: {str(e)}")

    @staticmethod
    def update(role_id, validated_data):
        """
        Actualiza el nombre de un rol. Los permisos se gestionan aparte.
        """
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return NotFoundResponse("Rol no encontrado.")

        new_name = validated_data.get('name')

        if new_name and new_name != role.name and Role.objects.filter(name=new_name).exclude(id=role_id).exists():
            return ErrorResponse(f"El nombre de rol '{new_name}' ya está en uso.")

        try:
            role.name = new_name if new_name else role.name
            role.save()
            role_data = RoleSerializer(role).data
            return SuccessResponse("Rol actualizado exitosamente.", data=role_data)
        except Exception as e:
            return ServerErrorResponse(f"Error al actualizar rol: {str(e)}")

    @staticmethod
    def delete(role_id):
        """
        Elimina un rol si no está asignado a ningún usuario.
        """
        try:
            role = Role.objects.get(id=role_id)
            if User.objects.filter(role=role, is_active=True).exists():
                return ErrorResponse(message="No se puede eliminar el rol, está asignado a usuarios activos.")

            role.delete()
            return NoContentResponse(message="Rol eliminado exitosamente.") 
        except Role.DoesNotExist:
            return NotFoundResponse("Rol no encontrado.")
        except Exception as e:
            return ServerErrorResponse(f"Error al eliminar rol: {str(e)}")

class PermissionService:
    @staticmethod
    def create(validated_data):
        """
        Crea un nuevo permiso.
        """
        name = validated_data.get('name')
        if Permission.objects.filter(name=name).exists():
            return ErrorResponse(message=f"El permiso '{name}' ya existe.")
        
        try:
            permission = Permission.objects.create(**validated_data)
            perm_data = PermissionSerializer(permission).data
            return CreatedResponse(message="Permiso creado exitosamente.", data=perm_data)
        except Exception as e:
            return ServerErrorResponse(f"Error al crear permiso: {str(e)}")


    @staticmethod
    def list(filters=None, order=None, limit=None, offset=0):
        """
        Lista permisos con filtros, ordenamiento y paginación.
        """
        try:
            queryset = Permission.objects.all()

            if filters:
                attr = filters.get('attr')
                value = filters.get('value')
                if attr in ['name', 'description'] and value:
                    filter_kwargs = {f"{attr}__icontains": value}
                    queryset = queryset.filter(**filter_kwargs)
                elif attr:
                    return ErrorResponse(message=f"Filtrado por '{attr}' no soportado en Permisos.")

            if order and order in ['name', '-name', 'description', '-description']:
                queryset = queryset.order_by(order)
            else:
                queryset = queryset.order_by('name')

            total_count = queryset.count()

            if limit is not None:
                try:
                    limit = int(limit); offset = int(offset)
                    if limit <= 0 or offset < 0: raise ValueError()
                    queryset = queryset[offset : offset + limit]
                except (ValueError, TypeError):
                    return ErrorResponse(message="Limit/Offset inválidos.")

            data = PermissionSerializer(queryset, many=True).data
            return SuccessResponse(message="Permisos encontrados", data=data)
        except Exception as e:
            return ServerErrorResponse(f"Error al listar permisos: {str(e)}")

    @staticmethod
    def retrieve(permission_id):
        """
        Obtiene un permiso específico por ID.
        """
        try:
            permission = Permission.objects.get(id=permission_id)
            perm_data = PermissionSerializer(permission).data
            return SuccessResponse(message="Permiso encontrado.", data=perm_data)
        except Permission.DoesNotExist:
            return NotFoundResponse(message="Permiso no encontrado.")
        except Exception as e:
            return ServerErrorResponse(f"Error al obtener permiso: {str(e)}")

    @staticmethod
    def update(permission_id, validated_data):
        """
        Actualiza un permiso existente.
        """
        try:
            permission = Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return NotFoundResponse(message="Permiso no encontrado.")

        new_name = validated_data.get('name')
        if new_name and new_name != permission.name and Permission.objects.filter(name=new_name).exclude(id=permission_id).exists():
            return ErrorResponse(message=f"El nombre de permiso '{new_name}' ya está en uso.")

        try:
            permission.name = new_name if new_name else permission.name
            permission.description = validated_data.get('description', permission.description)
            permission.save()
            perm_data = PermissionSerializer(permission).data
            return SuccessResponse(message="Permiso actualizado exitosamente.", data=perm_data)
        except Exception as e:
            return ServerErrorResponse(f"Error al actualizar permiso: {str(e)}")

    @staticmethod
    def delete(permission_id):
        """
        Elimina un permiso si no está asignado a ningún rol.
        """
        try:
            permission = Permission.objects.get(id=permission_id)
            if permission.roles.exists():
                return ErrorResponse(message="No se puede eliminar el permiso, está asignado a uno o más roles.")

            permission.delete()
            return NoContentResponse(message="Permiso eliminado exitosamente.")
        except Permission.DoesNotExist:
            return NotFoundResponse(message="Permiso no encontrado.")
        except Exception as e:
            return ServerErrorResponse(f"Error al eliminar permiso: {str(e)}")

class PermissionRoleService:
    """
    Servicio dedicado a gestionar la asignación de permisos a roles.
    """
    @staticmethod
    def assign_permissions_to_role(role_id, permission_ids):
        """
        Asigna una lista de permisos (por ID) a un rol (por ID).
        Reemplaza los permisos existentes del rol con los nuevos.
        """
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return NotFoundResponse(f"Rol con id '{role_id}' no encontrado.")

        valid_permissions = Permission.objects.filter(id__in=permission_ids)
        if valid_permissions.count() != len(permission_ids):
            invalid_ids = set(permission_ids) - set(valid_permissions.values_list('id', flat=True))
            return ErrorResponse(message=f"Los siguientes IDs de permiso no existen: {list(invalid_ids)}")

        try:
            role.permissions.set(valid_permissions)
            return SuccessResponse(message=f"Permisos asignados correctamente al rol '{role.name}'.")
        except Exception as e:
            return ServerErrorResponse(f"Error al asignar permisos: {str(e)}")

    @staticmethod
    def remove_permission_from_role(role_id, permission_id):
        """
        Quita un permiso específico de un rol.
        """
        try:
            role = Role.objects.get(id=role_id)
            permission = Permission.objects.get(id=permission_id)

            role.permissions.remove(permission)

            return SuccessResponse(message=f"Permiso '{permission.name}' quitado del rol '{role.name}'.")
        except Role.DoesNotExist:
            return NotFoundResponse("Rol no encontrado.")
        except Permission.DoesNotExist:
            return NotFoundResponse("Permiso no encontrado.")
        except Exception as e:
            return ServerErrorResponse(f"Error al quitar permiso: {str(e)}")

