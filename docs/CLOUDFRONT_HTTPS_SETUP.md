# 🚀 Configuración CloudFront + EC2 para HTTPS (SmartSales)

## 📌 Objetivo

Habilitar HTTPS usando CloudFront (Free Tier) para que funcione el reconocimiento de voz en SmartSales.

---

## FASE 1: Preparar EC2 y Nginx

### 1.1 Conectarse a EC2

```powershell
ssh -i "tu-clave.pem" ubuntu@52.0.69.138
```

### 1.2 Verificar estado actual de servicios

```bash
# Ver servicios activos
sudo systemctl status clinic-records-backend
sudo systemctl status smartsales-backend 2>/dev/null || echo "SmartSales no existe aún"

# Ver configuración Nginx
sudo nginx -t
cat /etc/nginx/sites-available/multi-apps
```

### 1.3 Asegurar que SmartSales backend esté corriendo

Si no existe el servicio `smartsales-backend.service`, créalo:

```bash
# Ir al directorio del proyecto SmartSales
cd /home/ubuntu/smart_sales/ss_backend

# Crear el archivo de servicio
sudo nano /etc/systemd/system/smartsales-backend.service
```

**Contenido del archivo** (ajusta rutas si es necesario):

```ini
[Unit]
Description=SmartSales Backend (Gunicorn + Django)
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/smart_sales/ss_backend
Environment="PATH=/home/ubuntu/smart_sales/ss_backend/vane/bin"
EnvironmentFile=/home/ubuntu/smart_sales/ss_backend/.env
ExecStart=/home/ubuntu/smart_sales/ss_backend/vane/bin/gunicorn \
    --bind 127.0.0.1:8003 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /var/log/smartsales/access.log \
    --error-logfile /var/log/smartsales/error.log \
    config.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Crear directorios de logs y habilitar servicio:**

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/smartsales
sudo chown ubuntu:ubuntu /var/log/smartsales

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar SmartSales
sudo systemctl enable smartsales-backend
sudo systemctl restart smartsales-backend

# Verificar que esté corriendo
sudo systemctl status smartsales-backend

# Verificar que el puerto 8003 esté escuchando
sudo netstat -tlnp | grep 8003
```

### 1.4 Configurar Nginx para SmartSales

Edita la configuración de Nginx:

```bash
sudo nano /etc/nginx/sites-available/multi-apps
```

**Modifica el bloque `location /api/`** para apuntar a SmartSales (puerto 8003):

```nginx
# API SmartSales (Backend principal)
location /api/ {
    proxy_pass http://127.0.0.1:8003/api/;
    proxy_http_version 1.1;

    # Headers esenciales
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Tenant-Slug $http_x_tenant_slug;

    # Timeouts largos para IA/voz
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    # WebSocket support (por si usas streaming)
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

**Probar y recargar Nginx:**

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 1.5 Verificar que todo funcione localmente

```bash
# Probar backend directo
curl http://127.0.0.1:8003/api/health/ || echo "Backend no responde en 8003"

# Probar a través de Nginx
curl http://127.0.0.1/api/health/

# Probar desde IP pública
curl http://52.0.69.138/api/health/
```

---

## FASE 2: Configurar Security Group en EC2

### 2.1 Ir a AWS Console → EC2 → Security Groups

1. **Busca tu instancia**: EC2 Dashboard → Instances → `52.0.69.138`
2. **Pestaña "Security"** → Click en el Security Group
3. **Edit inbound rules** → Asegúrate de tener:

```
Type        Protocol    Port    Source          Description
HTTP        TCP         80      0.0.0.0/0       Allow HTTP from CloudFront
HTTP        TCP         80      ::/0            Allow HTTP IPv6
SSH         TCP         22      Tu-IP/32        SSH access
```

**⚠️ IMPORTANTE**: NO necesitas abrir 443 en EC2. CloudFront se conecta a EC2 por HTTP (puerto 80).

---

## FASE 3: Crear Distribución CloudFront

### 3.1 Ir a AWS CloudFront Console

```
https://console.aws.amazon.com/cloudfront/v3/home
```

### 3.2 Crear nueva distribución

Click en **"Create distribution"** y configura:

#### **Origin Settings**

- **Origin domain**: `52.0.69.138` (tu IP EC2)
- **Protocol**: `HTTP only` (CloudFront → EC2 sin SSL)
- **HTTP port**: `80`
- **Origin name**: `smartsales-ec2-origin` (auto-generado, déjalo)

#### **Default Cache Behavior**

- **Path pattern**: `Default (*)`
- **Compress objects automatically**: `Yes`
- **Viewer protocol policy**: `Redirect HTTP to HTTPS` ⭐ (esto fuerza HTTPS)
- **Allowed HTTP methods**: `GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE`
- **Cache policy**: `CachingDisabled` (para APIs dinámicas)
- **Origin request policy**: `AllViewer`

#### **Settings**

- **Price class**: `Use only North America and Europe` (Free Tier)
- **Alternate domain name (CNAME)**: Dejar vacío (usarás `*.cloudfront.net`)
- **Custom SSL certificate**: `Default CloudFront Certificate (*.cloudfront.net)` ⭐
- **Security policy**: `TLSv1.2_2021`
- **Supported HTTP versions**: `HTTP/2, HTTP/1.1`
- **Default root object**: `index.html`
- **Standard logging**: `Off` (para Free Tier)

### 3.3 Crear distribución

Click **"Create distribution"** y **espera 5-10 minutos** hasta que Status = `Deployed`.

### 3.4 Anotar URL de CloudFront

Verás algo como:

```
d1234abcd5678.cloudfront.net
```

**Esta es tu URL HTTPS gratuita** 🎉

---

## FASE 4: Configurar Nginx para aceptar CloudFront

### 4.1 Modificar Nginx para aceptar el dominio CloudFront

```bash
sudo nano /etc/nginx/sites-available/multi-apps
```

Cambia la línea `server_name`:

```nginx
server {
    listen 80;

    # Acepta IP directa + dominio CloudFront
    server_name 52.0.69.138 _.cloudfront.net d1234abcd5678.cloudfront.net;

    # ... resto de tu configuración
}
```

**⚠️ Reemplaza** `d1234abcd5678.cloudfront.net` con tu dominio real de CloudFront.

### 4.2 Agregar headers para detectar HTTPS desde CloudFront

En el bloque `location /api/`:

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8003/api/;

    # Headers esenciales
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    # ⭐ IMPORTANTE: CloudFront envía el protocolo original
    proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
    proxy_set_header X-Forwarded-Host $host;

    # Timeouts
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
}
```

### 4.3 Recargar Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## FASE 5: Configurar Django para confiar en CloudFront

### 5.1 Editar settings de producción

```bash
cd /home/ubuntu/smart_sales/ss_backend
nano config/settings/production.py
```

Agrega o modifica:

```python
# HTTPS a través de CloudFront
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False  # CloudFront ya hace el redirect

# Hosts permitidos
ALLOWED_HOSTS = [
    '52.0.69.138',
    'd1234abcd5678.cloudfront.net',  # ⚠️ Reemplaza con tu dominio
    '*.cloudfront.net',
    'localhost',
    '127.0.0.1',
]

# CORS para frontend en CloudFront
CORS_ALLOWED_ORIGINS = [
    'https://d1234abcd5678.cloudfront.net',  # ⚠️ Reemplaza
]

CORS_ALLOW_CREDENTIALS = True

# CSRF (si usas cookies)
CSRF_TRUSTED_ORIGINS = [
    'https://d1234abcd5678.cloudfront.net',  # ⚠️ Reemplaza
]

# Session cookies seguros
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'  # Para cross-origin
CSRF_COOKIE_SAMESITE = 'None'
```

### 5.2 Reiniciar backend

```bash
sudo systemctl restart smartsales-backend
sudo systemctl status smartsales-backend
```

---

## FASE 6: Actualizar Frontend

### 6.1 Modificar variable de entorno del frontend

En tu máquina local (donde buildeas el frontend):

```powershell
cd D:\1NATALY\Proyectos\smart_sales\ss_frontend
```

Edita `.env.production`:

```env
VITE_API_URL=https://d1234abcd5678.cloudfront.net/api
```

**⚠️ Reemplaza** con tu dominio CloudFront.

### 6.2 Rebuild frontend

```powershell
npm run build
```

### 6.3 Subir nuevo dist/ a EC2

```powershell
# Opción 1: SCP
scp -i "tu-clave.pem" -r dist/* ubuntu@52.0.69.138:/home/ubuntu/smart_sales/ss_frontend/dist/

# Opción 2: FileZilla / WinSCP
# Sube la carpeta dist/ a /home/ubuntu/smart_sales/ss_frontend/dist/
```

En EC2:

```bash
# Verificar que los archivos estén actualizados
ls -la /home/ubuntu/smart_sales/ss_frontend/dist/
cat /home/ubuntu/smart_sales/ss_frontend/dist/index.html | grep cloudfront
```

---

## FASE 7: Probar HTTPS

### 7.1 Probar desde navegador

Abre en tu navegador:

```
https://d1234abcd5678.cloudfront.net
```

**Deberías ver**:

- ✅ Candado verde (HTTPS)
- ✅ Frontend cargando
- ✅ Login funcionando

### 7.2 Probar API

```powershell
# Desde PowerShell
Invoke-WebRequest -Uri "https://d1234abcd5678.cloudfront.net/api/health/" -UseBasicParsing
```

### 7.3 Probar reconocimiento de voz

Ve al módulo de voz en tu app y:

1. Click en botón de micrófono
2. El navegador debería pedir permiso
3. ✅ Si funciona, estás listo

---

## 🎤 FASE 8: Verificar Permisos de Micrófono

### 8.1 Verificar en Chrome DevTools

Abre tu app HTTPS y presiona `F12`:

```javascript
// Console
navigator.permissions.query({ name: "microphone" }).then((result) => {
  console.log("Microphone permission:", result.state);
});

// Probar directamente
navigator.mediaDevices
  .getUserMedia({ audio: true })
  .then((stream) => {
    console.log("✅ Micrófono funcionando!");
    stream.getTracks().forEach((track) => track.stop());
  })
  .catch((err) => console.error("❌ Error:", err));
```

### 8.2 Si no funciona el micrófono

1. **Verifica HTTPS**: La URL debe empezar con `https://`
2. **Permisos del navegador**: Chrome settings → Privacy → Site settings → Microphone
3. **Código en tu app**: Asegúrate de usar Web Speech API correctamente

---

## 📊 FASE 9: Monitoreo y Troubleshooting

### 9.1 Ver logs de Nginx (en EC2)

```bash
sudo tail -f /var/log/nginx/clinic_access.log
sudo tail -f /var/log/nginx/clinic_error.log
```

### 9.2 Ver logs de SmartSales backend

```bash
sudo journalctl -u smartsales-backend -f
tail -f /var/log/smartsales/error.log
tail -f /var/log/smartsales/access.log
```

### 9.3 CloudFront no responde

```bash
# Verificar que EC2 sea accesible por HTTP
curl -I http://52.0.69.138/

# Invalidar caché de CloudFront (AWS Console)
# CloudFront → Tu distribución → Invalidations → Create → Path: /*
```

### 9.4 Headers de debugging

Agrega a Nginx (temporal):

```nginx
location /api/ {
    # ... config existente

    # Debugging headers
    add_header X-Debug-Proto $http_x_forwarded_proto always;
    add_header X-Debug-Host $host always;
}
```

---

## 🎯 Checklist Final

- [ ] SmartSales backend corriendo en puerto 8003
- [ ] Nginx apunta `/api/` a `127.0.0.1:8003`
- [ ] Security Group permite HTTP (80) desde `0.0.0.0/0`
- [ ] CloudFront creado con `Redirect HTTP to HTTPS`
- [ ] Nginx acepta dominio CloudFront en `server_name`
- [ ] Django `ALLOWED_HOSTS` incluye dominio CloudFront
- [ ] Django `SECURE_PROXY_SSL_HEADER` configurado
- [ ] Frontend buildeado con `VITE_API_URL` apuntando a CloudFront
- [ ] Frontend subido a EC2 en `/home/ubuntu/smart_sales/ss_frontend/dist/`
- [ ] Browser muestra candado HTTPS
- [ ] API responde en `https://tu-dominio.cloudfront.net/api/`
- [ ] Micrófono pide permisos y funciona

---

## 🚨 Troubleshooting Común

### Error: "This site can't provide a secure connection"

- CloudFront aún está desplegando (espera 10 min)
- Verifica que usas `https://` en la URL

### Error: CORS

```python
# En Django settings
CORS_ALLOWED_ORIGINS = ['https://tu-dominio.cloudfront.net']
CORS_ALLOW_CREDENTIALS = True
```

### Error: CSRF Token

```python
# En Django settings
CSRF_TRUSTED_ORIGINS = ['https://tu-dominio.cloudfront.net']
```

### Error: 502 Bad Gateway

```bash
# Backend no está corriendo
sudo systemctl status smartsales-backend
sudo systemctl restart smartsales-backend

# Nginx no puede conectar
sudo netstat -tlnp | grep 8003
```

### Error: 504 Gateway Timeout

```nginx
# Aumentar timeouts en Nginx
proxy_read_timeout 300;
proxy_connect_timeout 300;
```

### Micrófono no funciona

1. Verifica HTTPS: `console.log(window.location.protocol)` → debe ser `https:`
2. Permisos del navegador: Settings → Privacy → Microphone
3. Prueba en Chrome incógnito (limpia permisos)

---

## 💰 Costos (Free Tier)

- **CloudFront**: 1 TB salida/mes gratis (primer año)
- **EC2 t2.micro**: 750 horas/mes gratis (primer año)
- **Total**: $0 USD (dentro de Free Tier)

---

## 🎉 ¡Listo!

Ahora tienes:

- ✅ HTTPS gratuito con CloudFront
- ✅ Dominio `*.cloudfront.net` con SSL
- ✅ Micrófono funcionando en el navegador
- ✅ Backend y frontend sin cambios mayores
- ✅ Todo dentro de Free Tier

**Siguiente paso**: Ir a `https://tu-dominio.cloudfront.net` y probar el reconocimiento de voz 🎤
