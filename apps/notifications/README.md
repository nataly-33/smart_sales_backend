# Sistema de Notificaciones Push

Sistema completo de notificaciones push usando Firebase Cloud Messaging (FCM) para SmartSales365.

## 🚀 Características

- ✅ Envío de notificaciones push a dispositivos Android, iOS y Web
- ✅ Gestión de tokens de dispositivos por usuario
- ✅ Historial de notificaciones enviadas
- ✅ Preferencias de notificaciones personalizables
- ✅ Horas silenciosas configurables
- ✅ Notificaciones automáticas para pedidos
- ✅ Panel de administración completo
- ✅ API REST para gestión de notificaciones
- ✅ Estadísticas de notificaciones

## 📦 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements_notifications.txt
```

### 2. Configurar Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Ve a "Configuración del proyecto" > "Cuentas de servicio"
4. Haz clic en "Generar nueva clave privada"
5. Guarda el archivo JSON descargado

### 3. Configurar Django

Agrega en tu archivo `settings.py` o `.env`:

#### Opción 1: Usando archivo de credenciales

```python
# settings.py
FIREBASE_CREDENTIALS_PATH = '/ruta/a/tu/firebase-credentials.json'
```

#### Opción 2: Usando variables de entorno

```python
# settings.py
import json
from decouple import config

FIREBASE_CREDENTIALS_DICT = json.loads(config('FIREBASE_CREDENTIALS_JSON', default='{}'))
```

En tu archivo `.env`:
```env
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"tu-proyecto",...}
```

### 4. Agregar la app a INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    ...
    'apps.notifications',
    ...
]
```

### 5. Incluir las URLs

```python
# config/urls.py
urlpatterns = [
    ...
    path('api/notifications/', include('apps.notifications.urls')),
    ...
]
```

### 6. Ejecutar migraciones

```bash
python manage.py makemigrations notifications
python manage.py migrate
```

## 📚 Uso

### Registrar Token de Dispositivo

```python
POST /api/notifications/device-tokens/
{
    "token": "fcm_token_aqui",
    "device_type": "android",  # android, ios, web
    "device_name": "Samsung Galaxy S21"
}
```

### Enviar Notificación a un Usuario

```python
from apps.notifications.services import notification_service

notification_service.send_to_user(
    user=usuario,
    title="¡Hola!",
    body="Tu pedido está en camino",
    notification_type="order_shipped",
    data={"order_id": "12345"}
)
```

### Enviar Notificación desde el Admin (API)

```python
POST /api/notifications/admin/send/
{
    "user_id": 123,  # opcional
    "title": "Nueva Promoción",
    "body": "50% de descuento en toda la tienda",
    "notification_type": "promotion",
    "send_to_all": false  # true para enviar a todos
}
```

### Obtener Notificaciones del Usuario

```python
GET /api/notifications/notifications/
```

### Marcar como Leída

```python
POST /api/notifications/notifications/{id}/mark_as_read/
```

### Configurar Preferencias

```python
PUT /api/notifications/preferences/
{
    "order_notifications": true,
    "payment_notifications": true,
    "promotion_notifications": false,
    "quiet_hours_enabled": true,
    "quiet_hours_start": "22:00:00",
    "quiet_hours_end": "08:00:00"
}
```

## 🔔 Tipos de Notificaciones

- `order_created`: Pedido creado
- `order_shipped`: Pedido enviado
- `order_delivered`: Pedido entregado
- `order_cancelled`: Pedido cancelado
- `payment_success`: Pago exitoso
- `payment_failed`: Pago fallido
- `stock_alert`: Alerta de stock
- `new_product`: Nuevo producto
- `promotion`: Promoción
- `general`: General

## 🎯 Notificaciones Automáticas

El sistema envía notificaciones automáticas cuando:

- ✅ Se crea un nuevo pedido
- ✅ Cambia el estado de un pedido (enviado, entregado, cancelado)
- ✅ Se procesa un pago

## 📊 Endpoints API

### Tokens de Dispositivo
- `GET /api/notifications/device-tokens/` - Listar tokens
- `POST /api/notifications/device-tokens/` - Registrar token
- `POST /api/notifications/device-tokens/{id}/deactivate/` - Desactivar token
- `POST /api/notifications/device-tokens/deactivate_all/` - Desactivar todos

### Notificaciones
- `GET /api/notifications/notifications/` - Listar notificaciones
- `GET /api/notifications/notifications/recent/` - Últimas 20
- `GET /api/notifications/notifications/unread_count/` - Contador no leídas
- `POST /api/notifications/notifications/{id}/mark_as_read/` - Marcar como leída
- `POST /api/notifications/notifications/mark_all_as_read/` - Marcar todas

### Preferencias
- `GET /api/notifications/preferences/` - Obtener preferencias
- `PUT /api/notifications/preferences/` - Actualizar preferencias

### Admin
- `POST /api/notifications/admin/send/` - Enviar notificación
- `GET /api/notifications/admin/stats/` - Estadísticas

## 🔐 Permisos

- Los usuarios pueden gestionar sus propios tokens y notificaciones
- Solo administradores pueden enviar notificaciones personalizadas
- Solo administradores pueden ver estadísticas globales

## 🎨 Integración con Flutter

### 1. Instalar paquete

```yaml
# pubspec.yaml
dependencies:
  firebase_messaging: ^14.6.9
  flutter_local_notifications: ^16.1.0
```

### 2. Configurar Firebase

Sigue la [guía oficial de Firebase para Flutter](https://firebase.google.com/docs/flutter/setup)

### 3. Registrar token

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

// Obtener token
final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
String? token = await _firebaseMessaging.getToken();

// Enviar al backend
await api.post('/api/notifications/device-tokens/', {
  'token': token,
  'device_type': 'android',
  'device_name': 'Mi Dispositivo'
});

// Escuchar nuevos tokens
_firebaseMessaging.onTokenRefresh.listen((newToken) {
  // Actualizar token en el backend
});
```

### 4. Manejar notificaciones

```dart
// Manejar notificaciones en primer plano
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  print('Notificación recibida: ${message.notification?.title}');
  // Mostrar notificación local
});

// Manejar taps en notificaciones
FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
  print('Notificación abierta: ${message.data}');
  // Navegar a pantalla correspondiente
});
```

## 🐛 Troubleshooting

### Error: Firebase no está inicializado

Asegúrate de que:
1. `firebase-admin` está instalado
2. Las credenciales de Firebase están configuradas correctamente
3. El archivo de credenciales existe y tiene permisos de lectura

### Error: Token no registrado

El token de dispositivo puede expirar o ser inválido. El sistema automáticamente marca estos tokens para eliminación.

### No llegan notificaciones

Verifica:
1. El token está activo en la base de datos
2. El usuario tiene las preferencias habilitadas para ese tipo de notificación
3. No está en horas silenciosas
4. Firebase está correctamente configurado
5. El dispositivo tiene conexión a internet

## 📈 Monitoreo

Puedes ver estadísticas en:
- Django Admin: `/admin/notifications/`
- API: `GET /api/notifications/admin/stats/`

## 🔄 Actualización de Tokens

Los tokens se actualizan automáticamente con cada uso. Los tokens inactivos por más de 30 días deberían ser eliminados periódicamente.

## 📝 Ejemplo Completo

```python
from apps.notifications.services import notification_service
from apps.accounts.models import User

# Enviar a un usuario específico
user = User.objects.get(email='cliente@example.com')
result = notification_service.send_to_user(
    user=user,
    title="🎉 ¡Pedido Confirmado!",
    body="Tu pedido #12345 ha sido confirmado",
    notification_type="order_created",
    data={
        "order_id": "12345",
        "action": "view_order"
    },
    image_url="https://example.com/order-image.jpg"
)

print(result)  # {'success': True, 'message_id': '...'}
```

## 🤝 Contribuir

Si encuentras algún bug o tienes sugerencias, por favor abre un issue.

## 📄 Licencia

Este módulo es parte de SmartSales365 Backend.
