# 🛍️ SmartSales365 - Backend API

**Sistema Inteligente de Gestión Comercial y Reportes Dinámicos**

API REST construida con Django y Django REST Framework para un sistema POS/E-commerce de Ropa Femenina que integra Inteligencia Artificial y comandos de voz.

## ✨ Características Principales

### Módulos de Negocio

- **Gestión Comercial**: Catálogo de productos, Stock por talla, Carrito de compras, Ventas online
- **Inteligencia Artificial**: Dashboard de predicción de ventas con Random Forest Regressor
- **Reportes Dinámicos**: Generación de reportes (PDF/Excel) mediante prompts de texto o comandos de voz
- **Sistema de Pagos**: Integración con PayPal (Stripe configurado)
- **Multi-rol**: Control de acceso basado en roles (RBAC)

### Roles de Usuario

- **Admin**: Gestión completa del sistema, productos, usuarios, roles, reportes e IA
- **Empleado**: Operaciones de ventas, gestión de productos, consulta de stock
- **Cliente**: Compras E-commerce, carrito, historial de pedidos, comandos de voz

### Funcionalidades Técnicas

- Sistema de autenticación JWT.
- Permisos granulares basados en Roles.
- API REST documentada con Swagger (DRF-Spectacular).
- Configuración CORS para los frontends (React y Flutter).
- Base de Datos **PostgreSQL**.

## Requisitos previos

- **Python 3.10 o superior**
- **pip**
- **PostgreSQL** (servidor local o remoto)
- (Opcional) [virtualenv](https://virtualenv.pypa.io/en/latest/) para crear un entorno virtual

## Pasos para correr el proyecto

1. **Clona el repositorio**

```bash
git clone <URL_DEL_REPOSITORIO>
cd smart_sales
```

2. **Crea y activa un entorno virtual (opcional pero recomendado)**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Instala las dependencias**

```bash
pip install -r requirements.txt
```

4. **Configura las variables de entorno**

Copia el archivo de ejemplo y configura tus variables:

```bash
cp .env.example .env
```

Edita el archivo .env con tu configuración.
Ver [ENV_SETUP.md](./ENV_SETUP.md) para más detalles.

**Variables requeridas mínimas:**

- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: Modo debug (True para desarrollo)
- Configuración de base de datos (`DB_*`)

5. **Aplica migraciones**

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

6. **Corre el servidor de desarrollo**

```bash
python manage.py runserver
```

O para producción, usa el script de entrada:

```bash
bash entrypoint.sh
```

7. **Cargar datos de prueba (seeder)**

```bash
python manage.py shell < scripts/seed_data.py
```

Esto creará:
- Roles y permisos
- Usuarios de prueba
- Categorías, marcas y tallas
- Productos con stock
- Métodos de pago

## 📚 Documentación

### Documentación API
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin Django**: http://localhost:8000/admin/

### Documentación Técnica
- **Guía Completa**: [docs/documentation_guide.md](./docs/documentation_guide.md)
- **Lista de Endpoints**: [docs/endpoints.md](./docs/endpoints.md)
- **Estado del Proyecto**: [docs/status.md](./docs/status.md)

## 👥 Usuarios de Prueba

| Rol      | Email                      | Password      | Descripción                    |
| -------- | -------------------------- | ------------- | ------------------------------ |
| Admin    | admin@smartsales365.com    | Admin2024!    | Acceso completo al sistema     |
| Empleado | empleado@smartsales365.com | Empleado2024! | Gestión de productos y ventas  |
| Cliente  | cliente@gmail.com          | Cliente2024!  | Compras online                 |

## 📊 Endpoints Principales

**Base URL**: http://localhost:8000/api/

### Autenticación
- `POST /auth/login/` - Login con JWT
- `POST /auth/register/register/` - Registro de usuario
- `GET /auth/users/me/` - Usuario actual

### Productos
- `GET /products/prendas/` - Listar productos (público)
- `GET /products/prendas/{slug}/` - Detalle de producto
- `POST /products/prendas/` - Crear producto (Admin)

### Carrito
- `GET /cart/` - Obtener carrito
- `POST /cart/add/` - Agregar al carrito

### Pedidos
- `GET /orders/pedidos/` - Mis pedidos
- `POST /orders/pedidos/` - Crear pedido (checkout)

Ver lista completa en [docs/endpoints.md](./docs/endpoints.md)

## 🚀 Tecnologías

**Core**:
- Python 3.10+
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL

**Autenticación**:
- djangorestframework-simplejwt 5.3.0

**Almacenamiento**:
- AWS S3 (boto3 + django-storages)

**Pagos**:
- PayPal REST SDK
- Stripe 7.0.0

**IA y Reportes**:
- scikit-learn 1.3.2 (Random Forest)
- pandas 2.1.4
- numpy 1.26.2
- reportlab 4.0.7 (PDF)
- openpyxl 3.1.2 (Excel)

## 📁 Estructura del Proyecto

```
ss_backend/
├── apps/
│   ├── core/          # Modelos base, permisos, constantes
│   ├── accounts/      # Autenticación, usuarios, roles
│   ├── products/      # Catálogo, stock, categorías
│   ├── customers/     # Clientes, direcciones, favoritos
│   ├── cart/          # Carrito de compras
│   └── orders/        # Pedidos, pagos, envíos
├── config/
│   └── settings/      # Configuración (base, dev, prod)
├── docs/              # Documentación técnica
├── scripts/           # Seeders y utilidades
└── requirements.txt
```

## 🔧 Configuración Adicional

### AWS S3 (Producción)

En producción, cambiar `USE_S3=True` en `.env`:

```bash
USE_S3=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

### PayPal

Configurar en `.env`:

```bash
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-secret
PAYPAL_MODE=sandbox  # o 'live' en producción
```

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Con cobertura
coverage run --source='.' manage.py test
coverage report
```

## 🛠️ Comandos Útiles

```bash
# Crear superusuario
python manage.py createsuperuser

# Hacer migraciones
python manage.py makemigrations
python manage.py migrate

# Colectar archivos estáticos
python manage.py collectstatic

# Shell de Django
python manage.py shell

# Limpiar cache
python manage.py clear_cache
```

## 📦 Deploy

Ver guía completa de deploy en [docs/deployment.md](./docs/deployment.md)

**Plataformas recomendadas**:
- AWS EC2 + RDS
- Railway
- Render
- Heroku

## 🤝 Contribución

Ver [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📝 Licencia

Este proyecto es privado y está bajo licencia propietaria.

---

**Versión**: 1.0.0
**Última actualización**: 6 de Noviembre 2025
