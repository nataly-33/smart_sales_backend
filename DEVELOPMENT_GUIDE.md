Guía de Desarrollo - Smart Sales 365

Esta guía detalla el flujo completo para desarrollar nuevas funcionalidades en el backend de Django, basándose en el patrón implementado en el módulo de usuarios.

📋 Índice

1. Arquitectura del Proyecto

2. Creación de Nuevos Módulos vs Apps

3. Estructura de Archivos por Módulo

4. Flujo de Desarrollo

5. Modelos y BaseModel

6. Enums Centralizados

7. Serializers

8. Views y ViewSets

9. Sistema de Permisos

10. Utilities (Utils)

11. Sistema de Respuestas

12. Configuración de URLs

13. Documentación Swagger

14. Seeders

15. Checklist de Desarrollo

16. Arquitectura del Proyecto (Patrón Service Layer)

El proyecto sigue una arquitectura modular de Django con patrones estandarizados:

smart_sales/
├── config/ # Configuración central y utilidades globales
│ ├── models.py # BaseModel (con UUID)
│ ├── enums.py # Enums centralizados
│ ├── response.py # Funciones de respuesta estandarizadas
│ ├── permissions.py # Clase HasPermission
│ ├── urls.py # URLs principales
│ └── settings.py # Configuración Django
├── users/ # Módulo de usuarios
│ ├── constants/
│ │ └── permissions.py # Enum de Permisos
│ ├── models.py # Modelos User, Role, Permission
│ ├── serializers.py # Serializers
│ ├── services.py # Capa de Servicios (Lógica de Negocio)
│ └── views.py # Vistas (Capa de Control)
└── [nuevo_modulo]/ # Nuevos módulos

Flujo de la Arquitectura (Patrón de Respuesta Directa desde el Servicio):

Views (views.py): Actúa como Controlador Delgado. Recibe el request, valida la entrada (usando un Serializer), y llama a un método del Service. Retorna directamente la respuesta generada por el servicio.

Services (services.py): Contiene la Lógica de Negocio y el Manejo de Respuestas. Es llamado por la Vista. Interactúa con los Models, maneja errores (try...except) y construye la respuesta HTTP final usando config/response.py (ej. SuccessResponse, NotFoundResponse).

Models (models.py): Define la base de datos.

2. Creación de Nuevos Módulos vs Apps

¿Cuándo crear una nueva App?

Crear una nueva App cuando:

La funcionalidad es completamente independiente

Requiere sus propios modelos de datos

Podría reutilizarse en otros proyectos

Tiene lógica de negocio compleja y específica

Trabajar en módulos existentes cuando:

La funcionalidad extiende algo ya existente

Solo necesitas nuevas vistas o endpoints

Los modelos ya existen y solo necesitas nuevas relaciones

Comando para crear nueva App:

python manage.py startapp nombre_del_modulo

3. Estructura de Archivos por Módulo

Cada módulo debe seguir esta estructura estándar (ej. users):

nuevo_modulo/
├── **init**.py
├── apps.py # Configuración de la app
├── models.py # Modelos de datos (User, Role, Permission)
├── serializers.py # Serializers (UserSerializer, RoleSerializer)
├── services.py # Lógica de negocio (UserService, RoleService)
├── views.py # Vistas (UserViewSet, RoleViewSet, LoginView)
├── constants/
│ └── permissions.py # Enums de permisos (Permissions.USER_SHOW)
├── migrations/
└── **pycache**/

4. Flujo de Desarrollo

Para cada nueva funcionalidad, sigue este orden:

Definir Constantes (constants/permissions.py) si se necesitan nuevos permisos.

Definir el Modelo (models.py)

Crear/Actualizar Enums (config/enums.py)

Crear Serializers (serializers.py)

Implementar Lógica de Negocio y Respuestas (services.py).

Implementar Vistas (views.py) - (Debe llamar al servicio y retornar su respuesta).

Configurar Permisos (en el ViewSet usando permission_classes y get_permissions).

Configurar URLs (config/urls.py)

Documentar con Swagger (decoradores en views)

Hacer migraciones y probar

5. Modelos y BaseModel

BaseModel

Todos los modelos deben heredar de BaseModel:

# En tu models.py

from config.models import BaseModel
from django.db import models

class TuModelo(BaseModel): # BaseModel ya incluye: # - id (UUID) # - created_at (DateTime) # - updated_at (DateTime)

    nombre = models.CharField(max_length=100)
    # ... otros campos

Ejemplo del modelo User:

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from config.models import BaseModel
from config.enums import Gender
from .models import Role # Asumiendo import local
from django.db import models

class User(BaseModel, AbstractBaseUser, PermissionsMixin):
ci = models.CharField(max_length=20, unique=True)
name = models.CharField(max_length=100)
phone = models.CharField(max_length=20)
email = models.EmailField(unique=True)
role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

6. Enums Centralizados

Ubicación: config/enums.py

Los enums se definen centralizadamente para mantener consistencia:

from enum import Enum

class TuEnum(Enum):
"""
Descripción del enum
"""
OPCION_1 = 'opcion1'
OPCION_2 = 'opcion2'

    @classmethod
    def choices(cls):
        """Para usar en Django models"""
        return [(item.value, item.get_label()) for item in cls]

    @classmethod
    def values(cls):
        """Solo los valores"""
        return [item.value for item in cls]

    def get_label(self):
        """Etiquetas en español"""
        labels = {
            self.OPCION_1: 'Opción Uno',
            self.OPCION_2: 'Opción Dos',
        }
        return labels.get(self, self.value)

Ejemplo del Gender enum:

class Gender(Enum):
MALE = 'male'
FEMALE = 'female'
OTHER = 'other'

    @classmethod
    def choices(cls):
        return [(gender.value, gender.get_label()) for gender in cls]

    def get_label(self):
        labels = {
            self.MALE: 'Masculino',
            self.FEMALE: 'Femenino',
            self.OTHER: 'Otro',
        }
        return labels.get(self, self.value)

7. Serializers

Ubicación: [modulo]/serializers.py

Los serializers manejan la serialización/deserialización de datos:

from rest_framework import serializers
from .models import TuModelo

class TuModeloSerializer(serializers.ModelSerializer):
class Meta:
model = TuModelo
fields = ['id', 'campo1', 'campo2', 'created_at', 'updated_at']
extra_kwargs = {
'campo_sensible': {'write_only': True},
}
read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_campo1(self, value):
        """Validación específica"""
        if not value.strip():
            raise serializers.ValidationError("El campo no puede estar vacío.")
        return value

    def create(self, validated_data):
        """Lógica personalizada de creación"""
        return TuModelo.objects.create(**validated_data)

Ejemplo del UserSerializer:

class UserSerializer(serializers.ModelSerializer):
role = RoleListSerializer(read_only=True)
role_id = serializers.PrimaryKeyRelatedField(
write_only=True, queryset=Role.objects.all(), source='role', allow_null=True
)

    class Meta:
        model = User
        fields = [
            'id', 'ci', 'name', 'lastname', 'email', 'phone', 'gender',
            'is_active', 'role', 'role_id', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def validate_ci(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("El CI debe contener solo números.")
        return value

8. Views y ViewSets

Ubicación: [modulo]/views.py

Usa ViewSets para operaciones CRUD estándar y APIView para lógica específica:

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from config.response import SuccessResponse, ErrorResponse # Importar respuestas
from .services import TuModeloService # Importar servicio
from .serializers import TuModeloSerializer

class TuModeloViewSet(viewsets.ViewSet):
serializer_class = TuModeloSerializer
permission_classes = [IsAuthenticated] # Añadir permisos personalizados

    def create(self, request):
        serializer = TuModeloSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Llamar al servicio y retornar su respuesta
        service_response = TuModeloService.create(serializer.validated_data)
        return service_response

    def list(self, request):
        # Implementar filtros, paginación, búsqueda
        filters = {} # ...
        order = request.query_params.get('order')
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset', 0)

        # Llamar al servicio y retornar su respuesta
        service_response = TuModeloService.list(
            filters=filters, order=order, limit=limit, offset=offset
        )
        return service_response

Ejemplo específico - LoginView:

@extend_schema(
tags=['Auth'],
request=LoginSerializer,
responses={
200: TokenResponseSerializer,
401: ErrorResponse,
}
)
class LoginView(APIView):
permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service_response = AuthService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        return service_response

9. Sistema de Permisos

El sistema de permisos es personalizado y se basa en tres archivos principales:

users/constants/permissions.py: Define los nombres de los permisos como un Enum (ej. Permissions.USER_SHOW).

users/models.py:

Permission: Almacena los permisos en la BD (ej. un registro con name="Mostrar usuarios").

Role: Tiene una relación ManyToManyField con Permission.

User: Tiene una ForeignKey a Role (un usuario tiene un solo rol).

config/permissions.py: Contiene la clase HasPermission.

Uso en Vistas (views.py)

Para proteger un ViewSet, debes:

Incluir HasPermission en permission_classes.

Implementar el método get_permissions(self) para asignar dinámicamente el permiso requerido desde el Enum de constantes.

# En tu views.py

from rest_framework.permissions import IsAuthenticated
from config.permissions import HasPermission
from .constants.permissions import Permissions

@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, HasPermission]

    def get_permissions(self):
        """ Asigna el 'permission_required' a la vista dinámicamente. """
        permission_required = None

        if self.action == 'list' or self.action == 'retrieve':
            permission_required = Permissions.USER_SHOW.value
        elif self.action == 'create':
            permission_required = Permissions.USER_CREATE.value
        elif self.action in ['update', 'partial_update']:
            permission_required = Permissions.USER_UPDATE.value
        elif self.action == 'destroy':
            permission_required = Permissions.USER_DELETE.value

        # Esto asigna la variable que 'HasPermission' leerá
        self.permission_required = permission_required
        return super().get_permissions()

    # ... tus métodos list, create, retrieve ...

10. Utilities (Utils)

... (Sección sin cambios) ...

11. Sistema de Respuestas

Ubicación: config/response.py

Este archivo provee funciones estandarizadas para las respuestas HTTP (ej. SuccessResponse, ErrorResponse, NotFoundResponse).

Importante: Patrón de Arquitectura (Respuesta Directa del Servicio)

CAPA DE SERVICIO (services.py): DEBE importar y usar config/response.py. Es responsable de manejar su propia lógica (incluyendo try...except si es necesario) y construir la respuesta HTTP final (ej. SuccessResponse, NotFoundResponse).

CAPA DE VISTA (views.py): DEBE llamar al servicio y retornar directamente la respuesta que este genera. Esta capa solo valida los datos de entrada (serializers) y pasa el control al servicio.

Ejemplo de Implementación (Patrón Actual):

# En services.py

from config.response import SuccessResponse, NotFoundResponse
from .models import User
from .serializers import UserSerializer

class UserService:
@staticmethod
def retrieve(user_id):
try:
user = User.objects.get(id=user_id, is_active=True)
user_data = UserSerializer(user).data # 1. El servicio crea la respuesta de éxito
return SuccessResponse(message="Usuario encontrado.", data=user_data)
except User.DoesNotExist: # 2. El servicio crea la respuesta de error
return NotFoundResponse("Usuario no encontrado.")

# En views.py

class UserViewSet(viewsets.ViewSet): # ...
def retrieve(self, request, pk=None): # 3. La vista solo llama y retorna
service_response = UserService.retrieve(user_id=pk)
return service_response

12. Configuración de URLs

Ubicación Principal: config/urls.py

Todas las URLs de la API se registran aquí.

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.views import UserViewSet, RoleViewSet, PermissionViewSet, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

# Router para ViewSets

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
path('admin/', admin.site.urls),

    # URLs de la API (registradas en el router)
    path('api/', include(router.urls)),

    # Endpoints de Autenticación
    path('api/auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Documentación Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularAPIView.as_view(url_name='schema'), name='swagger-ui'),

]

13. Documentación Swagger

Decorador @extend_schema

Documenta cada endpoint usando drf-spectacular:

from drf_spectacular.utils import extend_schema, OpenApiParameter
from config.response import SuccessResponse, ErrorResponse # (O tus Serializers de respuesta)

@extend_schema(
tags=['Nombre del Tag'],
request=TuSerializer,
parameters=[
OpenApiParameter(name='param', description='Descripción', required=False, type=str),
],
responses={
200: SuccessResponse, # Usar las clases de respuesta
400: ErrorResponse,
404: ErrorResponse,
}
)
class TuView(APIView):
def post(self, request): # Tu lógica aquí
pass

Serializers para Swagger:

Puedes usar directamente las funciones de config/response.py en el decorador responses si no has definido serializers de respuesta específicos (como StandardResponseSerializerSuccess que tenías comentado).

responses={
200: SuccessResponse,
400: ErrorResponse,
500: ErrorResponse,
}

14. Seeders

Estructura de Seeders

Para cada nueva entidad, crea su seeder correspondiente:

1. Crear el Seeder: seeders/tu_entidad_seeder.py

import pandas as pd
import random
from tu_modulo.models import TuModelo
from config.enums import TuEnum

class TuEntidadSeeder:
def **init**(self):
self.cantidad = 10
self.messages = []

    def add_message(self, message):
        self.messages.append(message)

    def create_sample_data(self):
        """Crear datos de prueba usando pandas"""
        # Generar DataFrame con datos
        df = pd.DataFrame({
            'campo1': [f'valor_{i}' for i in range(self.cantidad)],
            'campo2': [random.choice(['A', 'B', 'C']) for _ in range(self.cantidad)]
        })

        created_items = []
        for _, row in df.iterrows():
            item, created = TuModelo.objects.get_or_create(
                campo_unico=row['campo1'],
                defaults={
                    'campo2': row['campo2']
                }
            )
            if created:
                created_items.append(item)

        self.add_message(f"✅ {len(created_items)} items creados")
        return created_items

    def run(self):
        """Ejecutar seeder"""
        self.add_message("🚀 Iniciando seeder...")
        items = self.create_sample_data()

        return {
            'messages': self.messages,
            'items_created': len(items),
            'total_items': TuModelo.objects.count()
        }

2. Agregar a Views: seeders/views.py (Si tienes este archivo)

# from .tu_entidad_seeder import TuEntidadSeeder

# (Esta sección parece estar incompleta en la guía original,

# la lógica para ejecutar seeders debe ser implementada)

# @api_view(['GET'])

# @permission_classes([AllowAny])

# def seed_database(request):

# ...

3. Endpoint de Status (Si tienes este archivo)

# @api_view(['GET'])

# @permission_classes([AllowAny])

# def seeder_status(request):

# ...

15. Checklist de Desarrollo

✅ Al crear una nueva funcionalidad:

Planificación

[ ] ¿Necesito una nueva App o puedo usar una existente?

[ ] ¿Qué modelos necesito?

[ ] ¿Qué endpoints necesito?

[ ] ¿Qué roles pueden acceder?

Modelos (models.py)

[ ] Hereda de BaseModel

[ ] Usa enums para choices

[ ] Implementa **str**()

[ ] Define campos requeridos correctamente

Enums (config/enums.py o constants/)

[ ] Agrega nuevos enums si es necesario

[ ] Implementa choices() y get_label()

[ ] Documenta cada opción

Serializers (serializers.py)

[ ] Implementa validaciones personalizadas

[ ] Define read_only_fields apropiadamente

[ ] Usa extra_kwargs para campos sensibles

Servicios (services.py)

[ ] Implementa lógica de negocio

[ ] Maneja errores con try...except

[ ] Usa config/response.py para devolver respuestas

Vistas (views.py)

[ ] Implementa autenticación (IsAuthenticated)

[ ] Define permisos (HasPermission, get_permissions)

[ ] Llama al servicio y retorna su respuesta

[ ] Valida entrada con serializer.is_valid(raise_exception=True)

Permisos (constants/permissions.py)

[ ] Define nuevos permisos en el Enum si es necesario

[ ] Asigna los permisos en views.py

URLs (config/urls.py)

[ ] Registra ViewSets en el router

[ ] Define paths para APIViews específicas

[ ] Usa nombres descriptivos

Documentación Swagger

[ ] Usa @extend_schema en todas las views

[ ] Define tags apropiados

[ ] Documenta parámetros y responses

Seeders (Opcional)

[ ] Crea seeder para tu entidad

[ ] Usa pandas para generar datos

Testing

[ ] Ejecuta migraciones: python manage.py makemigrations && python manage.py migrate

[ ] Prueba seeders (si aplica)

[ ] Verifica Swagger: http://localhost:8000/api/docs/

[ ] Prueba todos los endpoints (Postman, etc.)

[ ] Verifica permisos por rol

Documentación

[ ] Actualiza esta guía si introduces nuevos patrones

[ ] Documenta APIs específicas

[ ] Actualiza README del proyecto

🎯 Buenas Prácticas

Consistencia: Sigue siempre los patrones establecidos

Reutilización: Usa componentes centralizados (BaseModel, enums, response system)

Seguridad: Siempre implementa autenticación y permisos apropiados

Documentación: Documenta todo en Swagger y código

Testing: Prueba con seeders antes de producción

Performance: Implementa filtros y paginación en listados

Mantenibilidad: Código limpio, nombres descriptivos, separación de responsabilidades

🔧 Comandos Útiles

# Crear migraciones

python manage.py makemigrations users

# Aplicar migraciones

python manage.py migrate

# Ejecutar servidor

python manage.py runserver

# Crear superusuario

python manage.py createsuperuser
