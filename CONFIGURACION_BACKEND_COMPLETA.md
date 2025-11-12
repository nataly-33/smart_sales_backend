# 🎯 CONFIGURACIÓN COMPLETA DEL BACKEND PARA NOTIFICACIONES

Este archivo contiene TODO lo que necesitas hacer en el backend para que funcionen las notificaciones.

**Tu amigo (Flutter) recibirá un archivo separado con solo las instrucciones de Flutter.**

---

## 📋 CHECKLIST DE BACKEND

```
☐ 1. Tener el archivo firebase-credentials.json
☐ 2. Instalar dependencias Python
☐ 3. Configurar .env
☐ 4. Ejecutar migraciones
☐ 5. Verificar que todo funciona
☐ 6. Generar archivo para Flutter
```

---

## PASO 1: VERIFICAR ARCHIVO FIREBASE

### 1.1 Asegúrate de tener el archivo descargado

Deberías tener en tu carpeta `Downloads`:

```
smart-sales-xxxxx-firebase-adminsdk-xxxxx.json
```

### 1.2 Muévelo a la carpeta correcta

```powershell
# Copiar el archivo
copy "C:\Users\TU_USUARIO\Downloads\smart-sales-*firebase-adminsdk*.json" `
      "d:\1NATALY\Proyectos\smart_sales\ss_backend\config\firebase-credentials.json"

# Verificar que se copió
Test-Path "d:\1NATALY\Proyectos\smart_sales\ss_backend\config\firebase-credentials.json"
```

Debe mostrar: `True`

Si no funciona, copia manualmente el archivo:

- Ve a `Downloads`
- Busca el archivo `smart-sales-*firebase-adminsdk*.json`
- Cópialo
- Pégalo en: `d:\1NATALY\Proyectos\smart_sales\ss_backend\config\`
- Renómbralo a: `firebase-credentials.json`

---

## PASO 2: INSTALAR DEPENDENCIAS PYTHON

### 2.1 Abre PowerShell en el directorio del backend

```powershell
cd d:\1NATALY\Proyectos\smart_sales\ss_backend
```

### 2.2 Instala las dependencias

```powershell
# Opción 1: Usar el archivo requirements
pip install -r requirements_notifications.txt

# Opción 2: Instalar manualmente
pip install firebase-admin==6.2.0
pip install django-model-utils==4.3.1
```

### 2.3 Verifica la instalación

```powershell
pip show firebase-admin
pip show django-model-utils
```

Deberías ver información de ambos paquetes.

---

## PASO 3: CONFIGURAR .env

### 3.1 Abre el archivo .env

En: `d:\1NATALY\Proyectos\smart_sales\ss_backend\.env`

### 3.2 Agrega esta línea

```env
FIREBASE_CREDENTIALS_PATH=d:/1NATALY/Proyectos/smart_sales/ss_backend/config/firebase-credentials.json
```

**IMPORTANTE:**

- Usa `/` (slash) no `\` (backslash)
- Debe estar exactamente como arriba

### 3.3 Verifica que está correcto

El archivo `.env` debe verse algo así:

```env
# Variables existentes
DEBUG=True
SECRET_KEY=tu_secret_key_aqui
DATABASE_URL=...

# AGREGA ESTA LÍNEA
FIREBASE_CREDENTIALS_PATH=d:/1NATALY/Proyectos/smart_sales/ss_backend/config/firebase-credentials.json

# Otras variables...
```

---

## PASO 4: EJECUTAR MIGRACIONES

### 4.1 En PowerShell, asegúrate de estar en el backend

```powershell
cd d:\1NATALY\Proyectos\smart_sales\ss_backend
```

### 4.2 Crea las migraciones

```powershell
python manage.py makemigrations notifications
```

Deberías ver:

```
Migrations for 'notifications':
  apps/notifications/migrations/0001_initial.py
    - Create model DeviceToken
    - Create model Notification
    - Create model NotificationPreference
```

### 4.3 Aplica las migraciones

```powershell
python manage.py migrate
```

Deberías ver:

```
Running migrations:
  Applying notifications.0001_initial... OK
```

### 4.4 Verifica que se crearon las tablas

```powershell
python manage.py dbshell
```

Dentro del shell, ejecuta:

```sql
.tables
```

Deberías ver las nuevas tablas (busca: `device_tokens`, `notifications`, etc.)

Salir del shell:

```sql
.exit
```

---

## PASO 5: PROBAR QUE TODO FUNCIONA

### 5.1 Inicia el servidor

```powershell
cd d:\1NATALY\Proyectos\smart_sales\ss_backend
python manage.py runserver
```

Deberías ver:

```
Starting development server at http://127.0.0.1:8000/
```

**Déjalo ejecutándose (no cierres esta terminal)**

### 5.2 Abre otra PowerShell en el mismo directorio

```powershell
cd d:\1NATALY\Proyectos\smart_sales\ss_backend
```

### 5.3 Abre Python Shell

```powershell
python manage.py shell
```

### 5.4 Prueba que Firebase está inicializado

Copia esto en el shell:

```python
from apps.notifications.services import notification_service

print("Verificando Firebase...")
if notification_service.fcm_service.initialized:
    print("✅ Firebase está inicializado correctamente")
else:
    print("❌ Firebase NO está inicializado")
    print("Verifica que:")
    print("1. El archivo config/firebase-credentials.json existe")
    print("2. La variable FIREBASE_CREDENTIALS_PATH está en .env")
    print("3. El archivo JSON es válido")
```

**Resultado esperado:**

```
Verificando Firebase...
✅ Firebase está inicializado correctamente
```

Si ves ❌, verifica que:

- El archivo `config/firebase-credentials.json` existe
- La variable `FIREBASE_CREDENTIALS_PATH` está en `.env`
- El archivo JSON es válido (no está corrupto)

### 5.5 Prueba enviar una notificación de prueba

**OPCIÓN 1: Copia TODO de una vez (recomendado)**

Copia TODO esto junto en una sola línea (sin espacios al principio):

```python
from apps.notifications.services import notification_service; from apps.accounts.models import User; user = User.objects.first(); result = notification_service.send_to_user(user=user, title="🧪 Prueba", body="Backend funciona", notification_type="general", save_to_db=True); print(result)
```

**OPCIÓN 2: Crea un script (MEJOR - sin errores de indentación)**

Salir del shell primero:

```python
exit()
```

Crear archivo de prueba:

```powershell
# En PowerShell, en ss_backend
cat > test_notifications.py << 'EOF'
from apps.notifications.services import notification_service
from apps.accounts.models import User

user = User.objects.first()

if user:
    print(f"\nProbando con usuario: {user.email}")
    result = notification_service.send_to_user(
        user=user,
        title="🧪 Prueba de Backend",
        body="Si ves esto en los logs, ¡el backend funciona!",
        notification_type="general",
        save_to_db=True
    )
    print(f"\nResultado:")
    print(result)
else:
    print("❌ No hay usuarios en la BD")
    print("Crea un usuario primero: python manage.py createsuperuser")
EOF
```

Ejecutar:

```powershell
python manage.py shell < test_notifications.py
```

**Resultado esperado:**

```
Probando con usuario: cliente835@consultoria.com

Resultado:
{'success': False, 'error': 'Usuario no tiene tokens activos'}
```

Esto es NORMAL en esta etapa porque todavía no hay tokens registrados (eso lo hace Flutter).

### 5.6 Salir del shell

```python
exit()
```

---

## PASO 6: VERIFICAR EN ADMIN DE DJANGO

### 6.1 Abre el navegador

Ve a: http://localhost:8000/admin/

### 6.2 Inicia sesión

Usa las credenciales de superusuario que creaste anteriormente.

### 6.3 Verifica que ves NOTIFICATIONS

En el panel de admin, deberías ver una nueva sección:

```
NOTIFICATIONS
├─ Device tokens
├─ Notifications
└─ Notification preferences
```

Si ves esto, ¡el backend está 100% configurado! ✅

---

## PASO 7: CREAR ARCHIVO PARA TU AMIGO (FLUTTER)

El backend está listo. Ahora necesitas generar un archivo con las instrucciones SOLO para Flutter.

**Tu amigo recibirá un archivo llamado:**

```
CONFIGURACION_FLUTTER_NOTIFICACIONES.md
```

Que contiene SOLO lo que necesita hacer en Flutter, sin nada de backend.

---

## 🧪 COMANDOS DE PRUEBA RÁPIDOS

### Ver todos los tokens registrados

```powershell
cd d:\1NATALY\Proyectos\smart_sales\ss_backend
python manage.py shell
```

```python
from apps.notifications.models import DeviceToken

for token in DeviceToken.objects.all():
    print(f"{token.user.email}: {token.token[:30]}... ({token.device_type})")
```

### Ver todas las notificaciones enviadas

```python
from apps.notifications.models import Notification

for notif in Notification.objects.all():
    print(f"[{notif.notification_type}] {notif.title} → {notif.user.email if notif.user else 'Todos'}")
```

### Ver preferencias de un usuario

```python
from apps.accounts.models import User

user = User.objects.first()
prefs = user.notification_preferences

print(f"Usuario: {user.email}")
print(f"Notif. pedidos: {prefs.order_notifications}")
print(f"Notif. pagos: {prefs.payment_notifications}")
print(f"Notif. promociones: {prefs.promotion_notifications}")
print(f"Horas silenciosas: {prefs.quiet_hours_enabled}")
```

---

## ✅ LISTA DE VERIFICACIÓN FINAL

```
☑ 1. ¿Archivo firebase-credentials.json en config/ ? → Sí
☑ 2. ¿firebase-admin instalado? → pip show firebase-admin
☑ 3. ¿django-model-utils instalado? → pip show django-model-utils
☑ 4. ¿FIREBASE_CREDENTIALS_PATH en .env? → Abre y verifica
☑ 5. ¿Migraciones ejecutadas? → python manage.py migrate
☑ 6. ¿Servidor inicia sin errores? → python manage.py runserver
☑ 7. ¿Firebase inicializado? → Prueba en Python Shell
☑ 8. ¿NOTIFICATIONS visible en admin? → Abre http://localhost:8000/admin/
```

---

## 🎯 RESUMEN: BACKEND COMPLETADO

```
✅ Código del backend: 100% LISTO
✅ Base de datos: CONFIGURADA
✅ Firebase: INTEGRADO
✅ APIs: FUNCIONANDO
✅ Admin: VISIBLE

EL BACKEND ESTÁ 100% LISTO PARA FLUTTER
```

---

## 🚀 PRÓXIMO PASO

Ahora tu amigo necesita:

1. El archivo `google-services.json` (desde Firebase Console)
2. Las instrucciones de Flutter (en archivo separado)
3. Conocer la URL de tu backend

**Puedes darle:**

- URL del backend: `http://TU_IP:8000` (o `http://localhost:8000` si es local)
- Archivo: `CONFIGURACION_FLUTTER_NOTIFICACIONES.md`

---

## 🆘 PROBLEMAS COMUNES

### Error: "Firebase no está inicializado"

**Causa:** Archivo JSON no está en el lugar correcto o variable de entorno no está en .env

**Solución:**

```powershell
# Verificar que el archivo existe
Test-Path "d:\1NATALY\Proyectos\smart_sales\ss_backend\config\firebase-credentials.json"

# Abrir .env y verificar que tiene la línea correcta
code d:\1NATALY\Proyectos\smart_sales\ss_backend\.env
```

### Error: "ModuleNotFoundError: No module named 'firebase_admin'"

**Solución:**

```powershell
pip install firebase-admin==6.2.0
```

### Error: "No such table: notifications_devicetoken"

**Solución:** Las migraciones no se ejecutaron

```powershell
python manage.py makemigrations notifications
python manage.py migrate
```

---

## 📞 ARCHIVO PARA TU AMIGO

El siguiente archivo contiene SOLO las instrucciones para Flutter:

**Nombre del archivo:** `CONFIGURACION_FLUTTER_NOTIFICACIONES.md`

Tu amigo solo necesita ese archivo, nada más.
