from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Permiso para usuarios con rol Admin"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'rol') and 
            request.user.rol and 
            request.user.rol.nombre == 'Admin'
        )

class IsEmpleadoOrAdmin(permissions.BasePermission):
    """Permiso para Empleados o Admin"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'rol') or not request.user.rol:
            return False
        return request.user.rol.nombre in ['Admin', 'Empleado']

class IsOwnerOrAdmin(permissions.BasePermission):
    """Permiso para dueño del recurso o Admin"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if hasattr(request.user, 'rol') and request.user.rol:
                if request.user.rol.nombre == 'Admin':
                    return True
            if hasattr(obj, 'usuario'):
                return obj.usuario == request.user
            return obj == request.user
        return False