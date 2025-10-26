from django.db import models
from enum import Enum

class Permissions(Enum):
    # User
    USER_SHOW = 'Mostrar usuarios'
    USER_CREATE = 'Crear usuarios'
    USER_UPDATE = 'Actualizar usuarios'
    USER_DELETE = 'Eliminar usuarios'

    # Role
    ROLE_SHOW = 'Mostrar roles'
    ROLE_CREATE = 'Crear roles'
    ROLE_UPDATE = 'Actualizar roles'
    ROLE_DELETE = 'Eliminar roles'

    # Permission
    PERMISSION_SHOW = 'Mostrar permisos'
    PERMISSION_CREATE = 'Crear permisos'
    PERMISSION_UPDATE = 'Actualizar permisos'
    PERMISSION_DELETE = 'Eliminar permisos'

    @classmethod
    def choices(cls):
        """Devuelve las opciones para usar en Django models"""
        return [(status.value, status.get_label()) for status in cls]
    
    @classmethod
    def values(cls):
        """Devuelve solo los valores de los estados"""
        return [status.value for status in cls]