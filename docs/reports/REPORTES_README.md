# Sistema de Reportes Dinámicos - SmartSales365

## Descripción General

El sistema de reportes dinámicos permite a los usuarios generar reportes personalizados a través de **comandos en lenguaje natural** (texto o voz). El sistema interpreta el prompt, construye consultas seguras, y genera reportes en múltiples formatos (PDF, Excel, CSV).

## Arquitectura

### Backend (Django + DRF)

```
apps/reports/
├── views.py                    # Endpoints REST
├── serializers.py              # Validación de datos
├── urls.py                     # Rutas API
├── services/
│   ├── prompt_parser.py        # Interpreta lenguaje natural
│   ├── query_builder.py        # Construye consultas ORM
│   ├── analytics_service.py    # Métricas y estadísticas
│   └── report_generator_service.py  # Coordina generación
└── generators/
    ├── pdf_generator.py        # Genera PDFs
    ├── excel_generator.py      # Genera Excel
    └── csv_generator.py        # Genera CSV
```

### Frontend (React + TypeScript)

```
modules/reports/
├── pages/
│   ├── ReportsPage.tsx         # UI principal de reportes
│   └── AnalyticsPage.tsx       # Dashboard de analytics
├── components/
│   ├── ReportPromptInput.tsx   # Input con voz
│   └── StatCard.tsx            # Tarjetas de estadísticas
├── services/
│   └── reports.service.ts      # Cliente API
└── types/
    └── index.ts                # Tipos TypeScript
```

## Flujo de Generación de Reportes

### 1. **Usuario ingresa prompt**

- Texto: escribiendo en el input
- Voz: mediante Web Speech API (navegador)

### 2. **Frontend envía request**

```typescript
POST /
  api /
  reports /
  generate /
  {
    prompt: "Ventas del año 2025 en Excel",
  };
```

### 3. **Backend procesa**

1.  **PromptParser** interpreta el texto:

    - Tipo de reporte (ventas, productos, clientes, etc.)
    - Período (año 2025, último mes, hoy, etc.)
    - Formato (PDF, Excel, CSV)
    - Agrupación (por producto, cliente, categoría)
    - Filtros adicionales

2.  **QueryBuilder** construye consulta segura:

    - Usa lista blanca de tablas/campos
    - Construye consultas Django ORM
    - Valida permisos y límites

3.  **ReportGenerator** genera archivo:
    - Formato apropiado (PDF/Excel/CSV)
    - Aplica estilos y formato
    - Agrega metadata

### 4. **Frontend descarga archivo**

- Recibe blob del archivo
- Crea link de descarga automático
- Muestra notificación de éxito

## Instalación y Configuración

### Backend

#### Requisitos

- Python 3.10+
- Django 4.2+
- PostgreSQL 14+

#### Dependencias adicionales

```bash
pip install openpyxl xlsxwriter weasyprint reportlab
```

#### Variables de entorno (.env)

```env
# Configuración de reportes
MAX_REPORT_ROWS=10000
REPORT_CACHE_ENABLED=True
REPORT_CACHE_TTL=3600

# Auditoría
ENABLE_LOGIN_AUDIT=True
```

#### Migraciones

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

### Frontend

#### Requisitos

- Node.js 18+
- React 18+
- TypeScript 5+

#### Instalación

```bash
cd ss_frontend
npm install
```

#### Variables de entorno (.env)

```env
VITE_API_URL=http://localhost:8000
```

## Ejecución en Local

### Backend

```bash
cd ss_backend

# Activar entorno virtual
# Windows
.\vane\Scripts\activate
# Linux/Mac
source vane/bin/activate

# Ejecutar servidor
python manage.py runserver
```

### Frontend

```bash
cd ss_frontend
npm run dev
```

Acceder a:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Admin: `http://localhost:3000/admin/reports`

## Ejecución en Producción

### Backend con Gunicorn

1. **Instalar Gunicorn**

```bash
pip install gunicorn
```

2. **Configurar workers** (gunicorn.conf.py)

```python
workers = 4
worker_class = 'sync'
bind = '0.0.0.0:8000'
timeout = 120
```

3. **Ejecutar**

```bash
gunicorn config.wsgi:application -c gunicorn.conf.py
```

### Frontend en Producción

1. **Build**

```bash
npm run build
```

2. **Servir con Nginx**

```nginx
server {
    listen 443 ssl http2;
    server_name smartsales365.com;

    root /var/www/smartsales/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### CORS y Seguridad

En producción, configurar en `settings/production.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'https://smartsales365.com',
    'https://www.smartsales365.com',
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'https://smartsales365.com',
]
```

## Reconocimiento de Voz

### Requisitos del Navegador

El sistema usa **Web Speech API** que requiere:

#### ✅ Navegadores soportados

- **Chrome/Chromium** 33+ (recomendado)
- **Edge** 79+
- **Safari** 14.1+
- **Opera** 27+

#### ❌ No soportados

- Firefox (no tiene Web Speech API completo)
- IE 11

### Requisitos de Conexión

1. **HTTPS obligatorio** (o localhost)

   - La Web Speech API solo funciona en contextos seguros
   - En local: `http://localhost` está permitido
   - En producción: DEBE ser `https://`

2. **Permisos de micrófono**
   - El usuario debe dar permiso explícito
   - El permiso se solicita al hacer clic en el botón "Voz"

### Consideraciones Especiales

#### Brave Browser

Brave tiene protecciones de privacidad adicionales:

- Requiere permiso explícito para cada sitio
- Ir a: `brave://settings/content/microphone`
- Agregar el sitio a la lista de permitidos

#### Mobile (iOS/Android)

- iOS Safari: requiere iOS 14.5+
- Android Chrome: funciona nativamente
- Requiere HTTPS estricto (no self-signed)

### Manejo de Errores

El componente `ReportPromptInput` maneja los siguientes errores:

| Error           | Descripción         | Solución                                   |
| --------------- | ------------------- | ------------------------------------------ |
| `not-allowed`   | Permiso denegado    | Dar permiso en configuración del navegador |
| `no-speech`     | No se detectó audio | Hablar más alto o verificar micrófono      |
| `audio-capture` | No hay micrófono    | Conectar o habilitar micrófono             |
| `network`       | Error de red        | Verificar conexión a internet              |

## Tipos de Reportes Soportados

### 1. Ventas

- Por período (día, mes, año, rango personalizado)
- Agrupado por producto, cliente, o categoría
- Filtrado por estado (pendiente, confirmado, etc.)

### 2. Productos

- Inventario completo
- Top productos más vendidos
- Agrupado por categoría o marca
- Productos con stock bajo

### 3. Clientes

- Lista de clientes
- Clientes nuevos por período
- Top clientes por volumen de compra
- Análisis de comportamiento

### 4. Analytics

- Resumen general del sistema
- Métricas de ventas
- Estadísticas de inventario
- Análisis de clientes

### 5. Logins (Auditoría)

- Registros de inicio de sesión
- Por usuario o período
- Detalle de IP y user agent

### 6. Carritos

- Carritos activos con items
- Análisis de abandono
- Valor promedio de carritos

### 7. Ingresos

- Por día, semana, mes
- Comparativas de períodos
- Tendencias y proyecciones

## Seguridad

### Lista Blanca

El sistema SOLO permite consultas sobre tablas y campos predefinidos:

**Tablas permitidas:**

- `pedido` (ventas)
- `prenda` (productos)
- `usuario` (clientes)
- `login_audit` (auditoría)
- `carrito` (carritos)

**NO se permite:**

- SQL libre o inyecciones
- Acceso a tablas sensibles (contraseñas, tokens)
- Consultas sin autenticación

### Autenticación

- Todos los endpoints requieren JWT válido
- Token en header: `Authorization: Bearer <token>`
- Verificación de rol para endpoints admin

### Rate Limiting (Recomendado)

```python
# Agregar en settings
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/hour',
        'user': '100/hour',
        'reports': '20/hour',
    }
}
```

## Límites y Validaciones

- **Máximo de filas por reporte:** 10,000 (configurable)
- **Timeout:** 120 segundos
- **Preview:** máximo 20 filas
- **Caché:** resultados se cachean por 1 hora (opcional)

## Troubleshooting

### Error 401 Unauthorized

**Problema:** El endpoint devuelve 401 incluso estando logueado.

**Soluciones:**

1. Verificar que el token JWT esté en el header
2. Token puede haber expirado - refrescar
3. Verificar middleware en `settings.py`
4. Revisar `permission_classes` en la vista

### Voz no funciona

**Problema:** El botón de voz no responde o da error.

**Soluciones:**

1. Verificar HTTPS (o localhost)
2. Dar permisos de micrófono en el navegador
3. Usar Chrome/Edge/Safari (no Firefox)
4. Revisar consola del navegador para errores

### Reporte vacío o sin datos

**Problema:** El reporte se genera pero no tiene datos.

**Soluciones:**

1. Verificar que existan datos para el período solicitado
2. Revisar filtros aplicados en el prompt
3. Verificar permisos del usuario sobre esos datos
4. Consultar logs del backend

### PDF/Excel no se descarga

**Problema:** El archivo no se descarga o está corrupto.

**Soluciones:**

1. Verificar Content-Type del response
2. Revisar que `responseType: 'blob'` esté configurado
3. Verificar permisos de descarga del navegador
4. Probar con otro formato (PDF vs Excel vs CSV)

## Testing

### Backend

```bash
python manage.py test apps.reports
```

### Frontend

```bash
npm run test
```

### Test Manual - Ejemplos de Prompts

1. "Ventas del año 2025 en Excel"
2. "Top 10 productos más vendidos en PDF"
3. "Clientes registrados en el último mes en CSV"
4. "Logins de los últimos 7 días en Excel"
5. "Carritos activos con items en PDF"
6. "Pedidos pendientes en Excel"
7. "Ingresos por día del mes actual en Excel"
8. "Reporte de analytics completo en PDF"

## Soporte

Para problemas o preguntas:

- GitHub Issues: (tu repo)
- Email: support@smartsales365.com
- Documentación API: `/docs/REPORTES_API.md`

## Licencia

Proyecto privado - SmartSales365 © 2025
