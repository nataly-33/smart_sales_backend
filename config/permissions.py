from rest_framework.permissions import BasePermission
from users.models import User, Role, Permission

class HasPermission(BasePermission):
    """
    Permisos personalizados para verificar si un usuario tiene el permiso requerido.
    El permiso requerido se pasa a la vista a través del atributo `permission_required`.

    Uso en una viewset:
    permission_classes = [HasPermission]
    permission_required = "PERMISSION_NAME"
    """
    message = 'No tiene permiso para realizar esta acción.'

    def has_permission(self, request, view):
        # Obtener el permiso requerido de la vista, si está especificado
        required_permission = getattr(view, 'permission_required', None)

        # Si no se requiere ningún permiso para la vista, conceder acceso
        if not required_permission:
            return True

        # Asegurarse de que el usuario esté autenticado y tenga un rol
        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, 'role') or not user.role:
            return False

        # Verificar si el rol del usuario tiene el permiso requerido
        return user.role.permissions.filter(name=required_permission).exists()