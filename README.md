# Smart Sales (smart_sales)

Este proyecto implementa **"SmartSales365": Sistema Inteligente de Gestión Comercial y Reportes Dinámicos**. Es una API backend construida con Django y Django REST Framework, diseñada para un sistema POS/E-commerce de Ropa Femenina que integra Inteligencia Artificial y comandos de voz.

## Características Principales

### Módulos de Negocio

- **Gestión Comercial (Ropa)**: Catálogo (Prenda/Detalle-SKU), Stock por Sucursal, Carrito, Venta POS y E-commerce.
- **Inteligencia Artificial (IA)**: Dashboard de predicción de ventas (Random Forest Regressor).
- **Reportes Dinámicos**: Generación de reportes (PDF/Excel) a partir de _prompts de texto o comandos de voz_.

### Roles de Usuario

- **Administrador Super Usuario (ASU)**: Gestión completa del sistema, IA y estructura (Roles, Permisos, Sucursales).
- **Recepcionista (R)**: Operaciones de Venta POS, consulta de Stock, emisión de reportes.
- **Cliente (C)**: Compras E-commerce, Carrito, Historial de Ventas, uso de comandos de voz.
- **Agencia de Delivery (D)**: Gestión del Envío y logística.

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

## 📚 Documentación API

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Admin: http://localhost:8000/admin/

## 👥 Usuarios de Prueba

| Rol      | Email                      | Password      |
| -------- | -------------------------- | ------------- |
| Admin    | admin@smartsales365.com    | Admin2024!    |
| Empleado | empleado@smartsales365.com | Empleado2024! |
| Cliente  | cliente@gmail.com          | Cliente2024!  |
| Delivery | delivery@smartsales365.com | Delivery2024! |
