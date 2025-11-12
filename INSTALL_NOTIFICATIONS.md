# 🔔 Guía de Instalación - Sistema de Notificaciones Push

Esta guía te ayudará a configurar el sistema de notificaciones push con Firebase Cloud Messaging en tu proyecto SmartSales365.

## ✅ Paso 1: Instalar Dependencias

```bash
# Navegar al directorio del backend
cd ss_backend

# Instalar las dependencias necesarias
pip install firebase-admin==6.2.0 django-model-utils==4.3.1

# O usar el archivo de requirements
pip install -r requirements_notifications.txt
```

## ✅ Paso 2: Configurar Firebase

### 2.1 Crear Proyecto en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Haz clic en "Agregar proyecto" o selecciona un proyecto existente
3. Sigue el asistente de configuración

### 2.2 Obtener Credenciales de Servicio

1. En tu proyecto de Firebase, ve a **Configuración del proyecto** (ícono de engranaje)
2. Selecciona la pestaña **Cuentas de servicio**
3. Haz clic en **Generar nueva clave privada**
4. Se descargará un archivo JSON con las credenciales
5. Guarda este archivo de forma segura (NO lo subas a Git)

### 2.3 Configurar Credenciales en Django

#### Opción A: Usar Archivo de Credenciales (Recomendado para desarrollo)

1. Copia el archivo JSON a tu proyecto (por ejemplo, en `config/firebase-credentials.json`)
2. Agrega la ruta en tu archivo `.env`:

```env
# .env
FIREBASE_CREDENTIALS_PATH=/ruta/completa/a/firebase-credentials.json
```

3. En `settings.py` o `config/settings/production.py`:

```python
from decouple import config

FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', default=None)
```

#### Opción B: Usar Variable de Entorno (Recomendado para producción)

1. Copia todo el contenido del archivo JSON
2. Minifica el JSON (elimina espacios y saltos de línea)
3. Agrega en tu `.env`:

```env
# .env
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"tu-proyecto-id",...}
```

4. En `settings.py`:

```python
import json
from decouple import config

FIREBASE_CREDENTIALS_DICT = json.loads(
    config('FIREBASE_CREDENTIALS_JSON', default='{}')
)
```

## ✅ Paso 3: Agregar la App a Django

### 3.1 Agregar a INSTALLED_APPS

Edita tu archivo `config/settings.py` o `config/settings/base.py`:

```python
INSTALLED_APPS = [
    # Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',

    # Tus apps
    'apps.core',
    'apps.accounts',
    'apps.products',
    'apps.customers',
    'apps.cart',
    'apps.orders',
    'apps.reports',
    'apps.ai',
    'apps.notifications',  # ← AGREGAR ESTA LÍNEA
]
```

### 3.2 Agregar URLs

Edita `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/notifications/', include('apps.notifications.urls')),  # ← AGREGAR ESTA LÍNEA
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]
```

## ✅ Paso 4: Ejecutar Migraciones

```bash
# Crear las migraciones
python manage.py makemigrations notifications

# Aplicar las migraciones
python manage.py migrate
```

## ✅ Paso 5: Actualizar Modelo de Pedidos (Opcional pero Recomendado)

Para que funcionen las notificaciones automáticas cuando cambia el estado de un pedido, necesitas usar `FieldTracker` de django-model-utils.

Edita `apps/orders/models.py`:

```python
from django.db import models
from model_utils import FieldTracker  # ← Importar

class Pedido(TimeStampedModel):
    # ... todos tus campos existentes ...

    # Agregar tracker al final
    tracker = FieldTracker(fields=['estado'])  # ← AGREGAR ESTA LÍNEA

    class Meta:
        # ... tu configuración existente ...
```

## ✅ Paso 6: Verificar Instalación

### 6.1 Crear Superusuario (si no tienes uno)

```bash
python manage.py createsuperuser
```

### 6.2 Iniciar el Servidor

```bash
python manage.py runserver
```

### 6.3 Verificar en el Admin

1. Ve a `http://localhost:8000/admin/`
2. Inicia sesión
3. Deberías ver las siguientes secciones nuevas:
   - **Tokens de dispositivos**
   - **Notificaciones**
   - **Preferencias de notificaciones**

### 6.4 Probar la API

```bash
# Registrar un token de dispositivo
curl -X POST http://localhost:8000/api/notifications/device-tokens/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "test_fcm_token_123",
    "device_type": "android",
    "device_name": "Mi Dispositivo"
  }'

# Obtener notificaciones
curl -X GET http://localhost:8000/api/notifications/notifications/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📱 Paso 7: Configurar App Móvil (Flutter)

### 7.1 Agregar Firebase a tu App

1. En Firebase Console, agrega tu app Android/iOS
2. Descarga `google-services.json` (Android) o `GoogleService-Info.plist` (iOS)
3. Colócalos en los directorios correspondientes

### 7.2 Instalar Paquetes

```yaml
# pubspec.yaml
dependencies:
  firebase_core: ^2.24.0
  firebase_messaging: ^14.7.0
  flutter_local_notifications: ^16.2.0
```

### 7.3 Código de Ejemplo (Flutter)

Ver el archivo `apps/notifications/README.md` para código completo.

## 🧪 Paso 8: Probar Notificaciones

### Método 1: Desde el Admin de Django

1. Ve a `/admin/notifications/notification/`
2. Crea una nueva notificación
3. Selecciona un usuario y tipo
4. Haz clic en "Guardar y enviar"

### Método 2: Desde Python Shell

```bash
python manage.py shell
```

```python
from apps.notifications.services import notification_service
from apps.accounts.models import User

# Obtener un usuario
user = User.objects.first()

# Enviar notificación de prueba
result = notification_service.send_to_user(
    user=user,
    title="¡Hola!",
    body="Esta es una notificación de prueba",
    notification_type="general",
    data={"test": "data"}
)

print(result)
```

### Método 3: Crear un Pedido

Las notificaciones de pedidos se envían automáticamente:

```python
from apps.orders.models import Pedido

# Crear o actualizar un pedido
# Se enviará automáticamente una notificación al usuario
```

## 🐛 Solución de Problemas

### Problema: "Firebase no está inicializado"

**Solución:**
1. Verifica que `firebase-admin` esté instalado: `pip show firebase-admin`
2. Verifica que las credenciales estén configuradas correctamente en `.env`
3. Verifica que el archivo de credenciales exista y tenga permisos de lectura

### Problema: "Token no registrado"

**Solución:**
- El token FCM puede haber expirado
- Registra un nuevo token desde la app móvil
- Verifica que el token esté marcado como activo en la BD

### Problema: No llegan notificaciones

**Verifica:**
1. El usuario tiene un token activo registrado
2. Las preferencias de notificaciones están habilitadas
3. No está en horas silenciosas
4. Firebase está correctamente configurado en el proyecto y la app
5. El dispositivo tiene conexión a internet
6. Los logs de Django no muestran errores

### Ver Logs

```bash
# Agregar logging en settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.notifications': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📊 Monitoreo

### Ver Estadísticas

```bash
# API
curl -X GET http://localhost:8000/api/notifications/admin/stats/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Admin de Django

Ve a `/admin/notifications/` para ver:
- Tokens registrados
- Historial de notificaciones
- Estadísticas de lectura
- Errores de envío

## 🔐 Seguridad

### ⚠️ IMPORTANTE:

1. **NUNCA** subas el archivo de credenciales de Firebase a Git
2. Agrega `*firebase-credentials.json` a tu `.gitignore`
3. Usa variables de entorno en producción
4. Limita los permisos de la cuenta de servicio de Firebase
5. Rota las credenciales periódicamente

### Configurar .gitignore

```gitignore
# Firebase
*firebase-credentials.json
firebase-adminsdk*.json

# Env files
.env
.env.local
.env.production
```

## ✅ ¡Listo!

Tu sistema de notificaciones push está configurado y listo para usar.

Para más detalles sobre el uso, consulta:
- `apps/notifications/README.md` - Documentación completa
- `apps/notifications/tests.py` - Ejemplos de uso

## 🆘 ¿Necesitas Ayuda?

Si tienes problemas:
1. Revisa los logs de Django
2. Revisa los logs de Firebase Console
3. Consulta la documentación oficial de [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
