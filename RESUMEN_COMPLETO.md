# 🛍️ SMARTSALES365 - SISTEMA INTELIGENTE DE GESTIÓN COMERCIAL

## RESUMEN COMPLETO - GUÍA MAESTRA DEL PROYECTO

**Versión:** 1.0 Final  
**Última actualización:** Octubre 2025  
**Duración total:** 12 días (3 ciclos)  
**Equipo:** 2 personas  
**Stack:** Django + React + Flutter + PostgreSQL + AWS/Azure/GCP

---

## 📋 TABLA DE CONTENIDOS

1. [Visión General del Proyecto](#1-visión-general-del-proyecto)
2. [Stack Tecnológico](#2-stack-tecnológico)
3. [Arquitectura del Sistema](#3-arquitectura-del-sistema)
4. [Estructura Completa del Proyecto](#4-estructura-completa-del-proyecto)
5. [Base de Datos](#5-base-de-datos)
6. [Planificación de Ciclos (12 días)](#6-planificación-de-ciclos-12-días)
7. [Integraciones de IA](#7-integraciones-de-ia)
8. [Sistema de Reportes Dinámicos](#8-sistema-de-reportes-dinámicos)
9. [Seguridad y Auditoría](#9-seguridad-y-auditoría)
10. [APIs y Swagger](#10-apis-y-swagger)
11. [Deployment](#11-deployment)
12. [Roles del Equipo](#12-roles-del-equipo)

---

## 1. VISIÓN GENERAL DEL PROYECTO

### 🎯 Objetivo

Desarrollar **SmartSales365**, un Sistema Inteligente de Gestión Comercial híbrido (POS + E-Commerce) que combine funcionalidades tradicionales de gestión de ventas con componentes de Inteligencia Artificial aplicada, permitiendo:

- Gestión completa de catálogo de productos
- Ventas presenciales (POS) y en línea (E-Commerce)
- Generación de reportes dinámicos mediante prompts de texto o voz
- Predicciones de ventas usando Machine Learning (Random Forest Regressor)
- Aplicación móvil Flutter con funcionalidades estratégicas

### 🎓 Contexto Académico

Este proyecto se desarrolla como **Segundo Examen Parcial** de la materia Sistemas de Información II, con una duración de **12 días naturales** divididos en **3 ciclos de desarrollo**.

### ✅ FUNCIONALIDADES MÍNIMAS OBLIGATORIAS

#### **a) Gestión Comercial Básica**

1. **Gestión de Productos:**
   - CRUD de productos (categorías, precios, stock, imágenes)
   - Atributos: tallas, colores, marcas
   - Inventario centralizado con alertas de stock mínimo
   - Galería de imágenes por producto

2. **Gestión de Clientes:**
   - Registro y perfil de clientes
   - Direcciones múltiples de envío
   - Historial de compras
   - Billetera virtual

3. **Carrito de Compra:**
   - Agregar/quitar productos
   - Selección de talla y color
   - Aplicación de descuentos
   - Comandos por **texto y voz**

4. **Gestión de Ventas:**
   - Ventas presenciales (POS)
   - Ventas online (E-Commerce)
   - Múltiples métodos de pago:
     - Efectivo
     - Tarjeta (Stripe/PayPal)
     - Billetera Virtual
   - Emisión de comprobantes (notas de venta)
   - Seguimiento de estados del pedido

5. **Gestión de Envíos:**
   - Asignación a agencias externas o delivery propio
   - Tracking de pedidos
   - Gestión de estados de entrega

#### **b) Generación Dinámica de Reportes (Texto o Voz)**

Los usuarios deben poder generar reportes mediante:

- **Prompt de texto** en interfaz web/móvil
- **Comando de voz** (Web Speech API / Flutter speech_to_text)

**Ejemplos de prompts válidos:**

```
"Quiero un reporte de ventas del mes de septiembre, agrupado por producto, en PDF"

"Genera un reporte en Excel de ventas del 01/10/2024 al 01/01/2025 con nombre del cliente, cantidad de compras, monto total y fechas"

"Dame las ventas de hoy en pantalla"

"Muéstrame los productos con bajo stock"

"Reporte de los 10 clientes que más han comprado este mes"
```

**Proceso del sistema:**

1. **Capturar** el prompt (texto o voz convertida a texto)
2. **Interpretar** el comando (parser con regex o reglas)
3. **Extraer parámetros:**
   - Tipo de reporte (ventas, productos, clientes)
   - Periodo (fechas, mes, año)
   - Formato (PDF, Excel, pantalla)
   - Agrupaciones (por producto, categoría, cliente)
   - Filtros adicionales
4. **Construir query dinámico** (SQL o Django ORM)
5. **Generar reporte** en formato solicitado
6. **Retornar resultado** (visualización o descarga)

**Tecnologías:**
- Parser propio (regex + reglas)
- `reportlab` para PDF
- `openpyxl` para Excel
- `pandas` para procesamiento de datos

#### **c) Dashboard de Predicción de Ventas (IA)**

Dashboard interactivo que muestre:

- **Ventas históricas:**
  - Por periodo (día, semana, mes)
  - Por producto/categoría
  - Por cliente
- **Predicciones futuras:**
  - Ventas proyectadas del próximo mes
  - Por categoría
  - Tendencias
- **Gráficas dinámicas:**
  - Líneas (tendencias)
  - Barras (comparativas)
  - Tortas (distribución)

**Modelo de IA: Random Forest Regressor**

- Framework: `scikit-learn`
- Entrenamiento con datos históricos
- Features: fecha, categoría, precio, promociones, día de la semana
- Target: monto de ventas
- Métricas: MSE, MAE, R²
- Serialización con `joblib`
- Reentrenamiento periódico automático

**Justificación del modelo:**
- Fácil implementación
- No requiere dataset extenso
- Buena capacidad de generalización
- Maneja relaciones no lineales
- Robusto ante outliers

#### **d) Aplicación Móvil (Flutter)**

La app móvil debe incluir funcionalidades estratégicas que aprovechen el entorno móvil:

**Funcionalidades prioritarias:**

1. **Compra rápida con cámara:**
   - Escanear código QR del producto
   - Búsqueda por foto (opcional)

2. **Carrito y checkout móvil:**
   - Agregar productos por texto/voz
   - Pago con billetera virtual
   - One-click purchase

3. **Notificaciones Push:**
   - Estado del pedido actualizado
   - Ofertas personalizadas
   - Recordatorios de carrito abandonado
   - Alertas de stock (productos favoritos)

4. **Dashboard resumido:**
   - Estadísticas de ventas (para admin/empleados)
   - Predicciones de IA
   - Gráficos simplificados

5. **Tracking de envíos:**
   - Estado en tiempo real
   - Mapa con ubicación del delivery
   - Contacto directo con repartidor

6. **Gestión rápida (empleados/admin):**
   - Confirmar pedidos
   - Actualizar inventario
   - Escanear productos para modificar stock

### 🚀 Características Principales del Sistema

- ✅ **Híbrido POS/E-Commerce:** Venta presencial y online
- ✅ **Sistema de Roles:** Admin, Empleado, Cliente, Delivery
- ✅ **Multi-Pago:** Efectivo, Tarjeta, Billetera Virtual
- ✅ **Reportes Inteligentes:** Generación por texto/voz
- ✅ **IA Predictiva:** Random Forest para ventas
- ✅ **App Móvil:** Flutter con funcionalidades estratégicas
- ✅ **Responsive:** PWA optimizada
- ✅ **Auditoría Completa:** Logs de todas las operaciones
- ✅ **API Documentada:** Swagger/OpenAPI

---

## 2. STACK TECNOLÓGICO

### 🔧 Backend

- **Framework:** Django 4.2 + Django REST Framework 3.14
- **Base de Datos:** PostgreSQL 14+
- **ORM:** Django ORM
- **Autenticación:** JWT con `djangorestframework-simplejwt`
- **Validaciones:** Serializers + Custom Validators
- **Tareas Asíncronas:** Celery 5.3 + Redis
- **Storage:** AWS S3 / Azure Blob / GCP Storage
- **Email:** SendGrid / AWS SES
- **Pagos:** Stripe + PayPal

### 🎨 Frontend Web

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **UI Library:** Tailwind CSS + shadcn/ui
- **Estado Global:** Zustand o React Context
- **Peticiones HTTP:** Axios
- **Routing:** React Router v6
- **Formularios:** React Hook Form + Zod
- **Gráficos:** Recharts o Chart.js
- **Notificaciones:** React Toastify
- **Reconocimiento de Voz:** Web Speech API

### 📱 Frontend Móvil

- **Framework:** Flutter 3.x
- **UI:** Material Design + Custom Widgets
- **Navegación:** GoRouter
- **Estado:** Provider / Riverpod
- **HTTP:** Dio
- **Almacenamiento Local:** Hive / Shared Preferences
- **Notificaciones Push:** Firebase Cloud Messaging
- **Reconocimiento de Voz:** speech_to_text
- **QR/Barcode:** mobile_scanner
- **Mapas:** Google Maps Flutter

### 🤖 Inteligencia Artificial

| Tecnología | Uso | Librería |
|------------|-----|----------|
| **Random Forest Regressor** | Predicción de ventas | scikit-learn |
| **Pandas** | Procesamiento de datos | pandas |
| **NumPy** | Operaciones numéricas | numpy |
| **Joblib** | Serialización de modelos | joblib |
| **Matplotlib/Seaborn** | Visualización (backend) | matplotlib |

### 📊 Generación de Reportes

| Formato | Librería | Uso |
|---------|----------|-----|
| **PDF** | reportlab / WeasyPrint | Reportes con gráficos |
| **Excel** | openpyxl / xlsxwriter | Tablas dinámicas |
| **CSV** | pandas | Exportación de datos |

### 🔧 DevOps & Herramientas

- **Control de Versiones:** Git + GitHub
- **CI/CD:** GitHub Actions
- **Deploy:** AWS / Azure / Google Cloud
- **Contenedores:** Docker + Docker Compose
- **Documentación API:** Swagger (drf-spectacular)
- **Testing:** pytest + pytest-django
- **Linting:** Black + Flake8 + isort
- **Gestión de Tareas:** Trello / Notion

---

## 3. ARQUITECTURA DEL SISTEMA

### 🏗️ Arquitectura General

```
┌────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                         │
├──────────────────────┬─────────────────────┬───────────────────┤
│   React Web App      │   Flutter Mobile    │   Admin Panel     │
│   (PWA Responsive)   │   (iOS + Android)   │   (Django Admin)  │
└──────────────────────┴─────────────────────┴───────────────────┘
                              ▼ HTTPS/REST
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY / NGINX                        │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO REST FRAMEWORK                        │
├─────────────────────────────────────────────────────────────────┤
│  Authentication (JWT) → Seguridad                               │
│  Permissions (RBAC) → Control de acceso por rol                 │
│  Report Generator → Parser de prompts + Query Builder           │
│  ML Service → Predicciones con Random Forest                    │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────┬───────────────────┬─────────────────────────┐
│   PostgreSQL     │   Redis           │   AWS S3 / Azure        │
│   (Base Datos)   │   (Caché/Celery)  │   (Imágenes)            │
└──────────────────┴───────────────────┴─────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICIOS EXTERNOS                           │
├─────────────────────────────────────────────────────────────────┤
│  Stripe/PayPal → Pagos  │  FCM → Push  │ SendGrid → Email      │
└─────────────────────────────────────────────────────────────────┘
```

### 📦 Arquitectura de Apps Django

```
smartsales365/
├── apps/
│   ├── core/              → Configuración base, utilidades
│   ├── accounts/          → Usuarios, roles, permisos, autenticación
│   ├── products/          → Catálogo (productos, categorías, stock)
│   ├── customers/         → Clientes, direcciones, favoritos
│   ├── cart/              → Carrito de compras
│   ├── orders/            → Pedidos, pagos, estados
│   ├── shipping/          → Envíos, tracking, agencias
│   ├── promotions/        → Descuentos, cupones
│   ├── reviews/           → Reseñas de productos
│   ├── reports/           → Sistema de reportes dinámicos
│   ├── analytics/         → Dashboard, estadísticas
│   ├── ai/                → Predicciones ML, entrenamiento
│   ├── notifications/     → Notificaciones push/email
│   └── audit/             → Logs de auditoría
└── config/                → Configuración Django
```

---

## 4. ESTRUCTURA COMPLETA DEL PROYECTO

### 📁 Estructura de Directorios (Final)

```
smartsales365-project/
│
├── backend/                          # Django Backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── pytest.ini
│   ├── docker-compose.yml
│   ├── Dockerfile
│   │
│   ├── config/                       # Configuración del proyecto
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py
│   │   │   └── testing.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── apps/                         # Todas las apps
│   │   │
│   │   ├── core/                     # Base del sistema
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # BaseModel
│   │   │   ├── admin.py
│   │   │   ├── permissions.py
│   │   │   ├── utils.py
│   │   │   ├── constants.py
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── accounts/                 # Usuarios y autenticación
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # User, Role, Permission
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── permissions.py
│   │   │   ├── signals.py
│   │   │   ├── services.py
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── products/                 # Catálogo de productos
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Prenda, Categoria, Marca, Talla, Stock
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── filters.py
│   │   │   ├── services.py
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── customers/                # Clientes
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Direccion, Favoritos
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── cart/                     # Carrito de compras
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Carrito, ItemCarrito
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py          # Lógica de carrito
│   │   │   ├── voice_processor.py   # Procesamiento de voz
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── orders/                   # Pedidos y pagos
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Pedido, DetallePedido, Pago
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── payment_processor.py # Stripe/PayPal
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── shipping/                 # Envíos
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Envio, AgenciaDelivery
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── promotions/               # Descuentos
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Descuento, DescuentoPrenda
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── reviews/                  # Reseñas
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Resena
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── reports/                  # Reportes dinámicos (NÚCLEO)
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # ReporteGenerado
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── prompt_parser.py     # Interpreta prompts
│   │   │   ├── query_builder.py     # Construye queries
│   │   │   ├── generators/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pdf_generator.py
│   │   │   │   ├── excel_generator.py
│   │   │   │   └── csv_generator.py
│   │   │   ├── templates/
│   │   │   │   ├── report_base.html
│   │   │   │   └── sales_report.html
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── analytics/                # Estadísticas y dashboard
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── ai/                       # Inteligencia Artificial (NÚCLEO)
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # PrediccionVentas, EntrenamientoModelo
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data_preparation.py
│   │   │   │   ├── model_trainer.py
│   │   │   │   ├── predictor.py
│   │   │   │   └── evaluator.py
│   │   │   ├── models_ml/           # Modelos serializados (.pkl)
│   │   │   │   └── .gitkeep
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   ├── notifications/            # Notificaciones
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Notificacion
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── push_service.py      # FCM
│   │   │   ├── tests/
│   │   │   └── migrations/
│   │   │
│   │   └── audit/                    # Auditoría
│   │       ├── __init__.py
│   │       ├── apps.py
│   │       ├── models.py            # Auditoria
│   │       ├── serializers.py
│   │       ├── views.py
│   │       ├── urls.py
│   │       ├── middleware.py
│   │       ├── signals.py
│   │       ├── tests/
│   │       └── migrations/
│   │
│   ├── static/                       # Archivos estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── media/                        # Archivos subidos (dev)
│   │   ├── products/
│   │   ├── avatars/
│   │   └── reports/
│   │
│   ├── templates/                    # Templates HTML
│   │   ├── base.html
│   │   ├── emails/
│   │   └── reports/
│   │
│   ├── scripts/                      # Scripts útiles
│   │   ├── setup_dev.sh
│   │   ├── seed_data.py
│   │   ├── train_ml_model.py
│   │   └── generate_fake_sales.py
│   │
│   └── docs/                         # Documentación
│       ├── api.md
│       ├── architecture.md
│       └── deployment.md
│
├── frontend/                         # React Frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── index.html
│   ├── .env
│   ├── .env.example
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── assets/
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── vite-env.d.ts
│       │
│       ├── components/               # Componentes reutilizables
│       │   ├── ui/                  # shadcn/ui components
│       │   ├── layout/
│       │   ├── forms/
│       │   ├── products/
│       │   ├── cart/
│       │   └── common/
│       │
│       ├── pages/                    # Páginas
│       │   ├── auth/
│       │   ├── dashboard/
│       │   ├── products/
│       │   ├── cart/
│       │   ├── checkout/
│       │   ├── orders/
│       │   ├── reports/
│       │   └── analytics/
│       │
│       ├── services/                 # API calls
│       │   ├── api.ts
│       │   ├── auth.service.ts
│       │   ├── products.service.ts
│       │   ├── cart.service.ts
│       │   ├── orders.service.ts
│       │   ├── reports.service.ts
│       │   └── voice.service.ts
│       │
│       ├── hooks/                    # Custom hooks
│       │   ├── useAuth.ts
│       │   ├── useCart.ts
│       │   ├── useVoice.ts
│       │   └── useDebounce.ts
│       │
│       ├── store/                    # Estado global
│       │   ├── authStore.ts
│       │   ├── cartStore.ts
│       │   └── index.ts
│       │
│       ├── utils/                    # Utilidades
│       │   ├── constants.ts
│       │   ├── helpers.ts
│       │   └── formatters.ts
│       │
│       ├── types/                    # TypeScript types
│       │   └── index.ts
│       │
│       └── styles/                   # Estilos globales
│           └── globals.css
│
├── mobile/                           # Flutter App
│   ├── pubspec.yaml
│   ├── analysis_options.yaml
│   ├── android/
│   ├── ios/
│   ├── web/
│   │
│   └── lib/
│       ├── main.dart
│       │
│       ├── config/
│       │   ├── theme.dart
│       │   ├── routes.dart
│       │   └── constants.dart
│       │
│       ├── models/
│       │   ├── user.dart
│       │   ├── product.dart
│       │   ├── order.dart
│       │   └── cart.dart
│       │
│       ├── providers/
│       │   ├── auth_provider.dart
│       │   ├── cart_provider.dart
│       │   └── products_provider.dart
│       │
│       ├── services/
│       │   ├── api_service.dart
│       │   ├── auth_service.dart
│       │   ├── voice_service.dart
│       │   ├── notification_service.dart
│       │   └── storage_service.dart
│       │
│       ├── screens/
│       │   ├── auth/
│       │   ├── home/
│       │   ├── products/
│       │   ├── cart/
│       │   ├── orders/
│       │   ├── profile/
│       │   └── dashboard/
│       │
│       ├── widgets/
│       │   ├── common/
│       │   ├── products/
│       │   └── cart/
│       │
│       └── utils/
│           ├── helpers.dart
│           └── validators.dart
│
├── database/                         # Scripts de DB
│   ├── schema.sql
│   └── seeders/
│       ├── roles.sql
│       ├── users.sql
│       ├── products.sql
│       └── fake_sales.sql
│
└── docs/                             # Documentación del proyecto
    ├── RESUMEN_COMPLETO.md          # Esta guía
    ├── PLAN_ACCION_DIA_*.md         # Guías diarias
    ├── UML/                         # Diagramas UML
    ├── API_DOCUMENTATION.md
    └── DEPLOYMENT_GUIDE.md
```

---

## 5. BASE DE DATOS

### 📊 Diseño de Base de Datos

La base de datos PostgreSQL está diseñada con **30 tablas** organizadas en **11 módulos funcionales**.

#### **MÓDULOS Y TABLAS:**

| # | Módulo | Tablas | Total |
|---|--------|--------|-------|
| 1 | Autenticación | rol, permiso, permiso_rol, usuario, direccion | 5 |
| 2 | Catálogo | categoria, marca, talla, prenda, prenda_categoria, stock_prenda, imagen_prenda | 7 |
| 3 | Promociones | descuento, descuento_prenda | 2 |
| 4 | Ventas | pedido, detalle_pedido, historial_estado_pedido, pago, metodo_pago | 5 |
| 5 | Envíos | envio, agencia_delivery | 2 |
| 6 | Carrito | carrito, item_carrito | 2 |
| 7 | Social | resena, favoritos | 2 |
| 8 | Notificaciones | notificacion | 1 |
| 9 | Reportes | reporte_generado | 1 |
| 10 | IA | prediccion_ventas, entrenamiento_modelo | 2 |
| 11 | Auditoría | auditoria | 1 |

**TOTAL: 30 TABLAS**

### 🔑 Características Clave de la BD:

- ✅ **UUIDs:** Todas las PKs son UUID v4 para seguridad
- ✅ **Soft Deletes:** Campo `deleted_at` en tablas críticas
- ✅ **Timestamps:** `created_at` y `updated_at` automáticos
- ✅ **JSONB:** Campos flexibles para metadata
- ✅ **Índices:** Optimizados para queries frecuentes
- ✅ **Constraints:** Validaciones a nivel de BD
- ✅ **Extensiones:** uuid-ossp, pgcrypto

### 📝 Script SQL Completo

El script SQL completo con las 30 tablas, índices y constraints está disponible en:

```bash
database/schema.sql
```

**Ejecutar con:**

```bash
psql -U postgres -d smartsales365_db -f database/schema.sql
```

---

## 6. PLANIFICACIÓN DE CICLOS (12 DÍAS)

### 📅 Calendario General

| Ciclo | Días | Duración | Objetivo |
|-------|------|----------|----------|
| **CICLO 1** | 1-5 | 5 días | Backend completo + Frontend básico + Base de datos |
| **CICLO 2** | 6-9 | 4 días | IA + Reportes Dinámicos + Frontend avanzado |
| **CICLO 3** | 10-12 | 3 días | App Móvil + Testing + Deploy + Documentación |

---

## 🎯 CICLO 1: FUNDACIÓN DEL SISTEMA (Días 1-5)

**Objetivo:** Sistema funcional con todas las operaciones CRUD, autenticación, catálogo y ventas básicas.

### **DÍA 1 - Setup y Autenticación** (8 horas)

**Entregables:**

- ✅ Proyecto Django configurado
- ✅ Base de datos PostgreSQL creada y poblada
- ✅ Modelos: User, Role, Permission
- ✅ Autenticación JWT funcionando
- ✅ Roles: Admin, Empleado, Cliente, Delivery
- ✅ API de login/logout/register
- ✅ 4 usuarios de prueba (uno por rol)

**Tecnologías:**
- Django 4.2
- PostgreSQL
- djangorestframework-simplejwt

**Funcionalidades:**
- Sistema de autenticación completo
- RBAC (Role-Based Access Control)
- Permisos granulares
- JWT con refresh token

---

### **DÍA 2 - Catálogo de Productos** (8 horas)

**Entregables:**

- ✅ Modelos: Categoria, Marca, Talla, Prenda, StockPrenda, ImagenPrenda
- ✅ APIs CRUD completas de productos
- ✅ Sistema de inventario (stock por talla/color)
- ✅ Upload de imágenes (S3 o local)
- ✅ Filtros y búsqueda de productos
- ✅ 50+ productos de prueba (seeders)

**APIs principales:**

```
GET/POST    /api/products/categories/
GET/POST    /api/products/brands/
GET/POST    /api/products/sizes/
GET/POST    /api/products/
GET         /api/products/{id}/
PUT/DELETE  /api/products/{id}/
GET         /api/products/search/?q=&category=&brand=
POST        /api/products/{id}/images/
GET         /api/products/{id}/stock/
PUT         /api/products/{id}/stock/
```

**Funcionalidades:**
- CRUD completo de productos
- Gestión de stock por variante (talla/color)
- Galería de imágenes
- Búsqueda y filtros avanzados
- Alertas de stock bajo

---

### **DÍA 3 - Carrito y Clientes** (8 horas)

**Entregables:**

- ✅ Modelos: Direccion, Favoritos, Carrito, ItemCarrito
- ✅ APIs de gestión de clientes
- ✅ Sistema de carrito de compras
- ✅ Direcciones múltiples de envío
- ✅ Lista de favoritos/wishlist
- ✅ Billetera virtual (saldo)

**APIs principales:**

```
GET/PUT     /api/customers/profile/
GET/POST    /api/customers/addresses/
PUT/DELETE  /api/customers/addresses/{id}/
GET         /api/customers/wallet/
POST        /api/customers/wallet/recharge/

GET         /api/cart/
POST        /api/cart/add/
PUT         /api/cart/items/{id}/
DELETE      /api/cart/items/{id}/
DELETE      /api/cart/clear/

GET/POST    /api/favorites/
DELETE      /api/favorites/{id}/
```

**Funcionalidades:**
- Perfil de cliente completo
- Múltiples direcciones de envío
- Carrito persistente
- Agregar/quitar productos
- Actualizar cantidades
- Favoritos

---

### **DÍA 4 - Sistema de Ventas y Pedidos** (8 horas)

**Entregables:**

- ✅ Modelos: Pedido, DetallePedido, Pago, MetodoPago, HistorialEstadoPedido
- ✅ APIs de gestión de pedidos
- ✅ Múltiples métodos de pago (Efectivo, Tarjeta, Billetera)
- ✅ Estados de pedido (workflow)
- ✅ Integración básica con Stripe
- ✅ Generación de número de pedido único

**APIs principales:**

```
POST        /api/orders/checkout/
GET         /api/orders/
GET         /api/orders/{id}/
PUT         /api/orders/{id}/status/
GET         /api/orders/{id}/history/
POST        /api/orders/{id}/cancel/

GET         /api/orders/payment-methods/
POST        /api/payments/process/
POST        /api/payments/stripe/webhook/
```

**Funcionalidades:**
- Checkout completo
- Proceso de pedido (estados)
- Pagos múltiples:
  - Efectivo (POS)
  - Tarjeta (Stripe)
  - Billetera Virtual
- Historial de estados
- Cálculo de totales
- Aplicación de descuentos

---

### **DÍA 5 - Envíos y Frontend Básico** (8 horas)

**Entregables Backend:**

- ✅ Modelos: Envio, AgenciaDelivery
- ✅ APIs de gestión de envíos
- ✅ Asignación de delivery
- ✅ Tracking básico

**APIs principales:**

```
GET/POST    /api/shipping/agencies/
GET         /api/shipping/orders/{order_id}/
PUT         /api/shipping/orders/{order_id}/status/
GET         /api/shipping/track/{tracking_code}/
```

**Entregables Frontend:**

- ✅ Setup React + Vite
- ✅ Autenticación (login/register)
- ✅ Catálogo de productos (grid)
- ✅ Carrito de compras
- ✅ Página de producto (detalle)
- ✅ Checkout básico

**Páginas:**
- `/login` - Login
- `/register` - Registro
- `/` - Home con productos
- `/products/:id` - Detalle producto
- `/cart` - Carrito
- `/checkout` - Finalizar compra

---

## 🤖 CICLO 2: INTELIGENCIA ARTIFICIAL Y REPORTES (Días 6-9)

**Objetivo:** Implementar las funcionalidades de IA (predicciones) y el sistema de reportes dinámicos por texto/voz.

### **DÍA 6 - Reportes Dinámicos (Parte 1)** (8 horas)

**Entregables:**

- ✅ Modelo: ReporteGenerado
- ✅ PromptParser (interpreta comandos de texto)
- ✅ QueryBuilder (construye queries SQL dinámicos)
- ✅ Generador de reportes en pantalla (JSON)

**Componentes:**

1. **PromptParser** (`apps/reports/prompt_parser.py`)
   - Extrae tipo de reporte
   - Extrae fechas (rangos)
   - Extrae formato (PDF, Excel, pantalla)
   - Extrae agrupaciones
   - Extrae filtros

2. **QueryBuilder** (`apps/reports/query_builder.py`)
   - Construye query Django ORM
   - Aplica filtros
   - Aplica agrupaciones
   - Aplica ordenamiento

3. **ReportGenerator** (`apps/reports/generators/`)
   - Procesa query
   - Formatea datos
   - Retorna resultado

**Ejemplos de prompts soportados:**

```
"Ventas del mes de octubre"
"Reporte de ventas del 01/10/2024 al 31/10/2024"
"Ventas de hoy"
"Productos con stock menor a 10"
"Top 10 clientes que más compraron"
"Ventas por categoría en pantalla"
```

**APIs:**

```
POST        /api/reports/generate/
GET         /api/reports/history/
GET         /api/reports/{id}/download/
```

---

### **DÍA 7 - Reportes Dinámicos (Parte 2) + Voz** (8 horas)

**Entregables:**

- ✅ Generadores de PDF (reportlab)
- ✅ Generadores de Excel (openpyxl)
- ✅ Templates HTML para reportes
- ✅ Integración de voz en frontend (Web Speech API)
- ✅ Endpoint para recibir comandos de voz

**Generadores:**

1. **PDFGenerator** (`pdf_generator.py`)
   - Reportes con tablas
   - Gráficos embebidos (matplotlib)
   - Header/footer personalizado
   - Logo de la empresa

2. **ExcelGenerator** (`excel_generator.py`)
   - Múltiples hojas
   - Formato de celdas
   - Fórmulas
   - Gráficos

**Frontend:**

- Componente `<VoiceReport />` con micrófono
- Captura de audio
- Conversión speech-to-text
- Envío a backend
- Visualización de resultado

**Ejemplos:**

```typescript
// Usuario habla: "Quiero un reporte de ventas de octubre en PDF"
// Sistema procesa:
{
  "tipo": "ventas",
  "fecha_inicio": "2024-10-01",
  "fecha_fin": "2024-10-31",
  "formato": "pdf"
}
// Genera PDF y retorna URL de descarga
```

---

### **DÍA 8 - Inteligencia Artificial (Preparación de Datos)** (8 horas)

**Entregables:**

- ✅ Modelos: PrediccionVentas, EntrenamientoModelo
- ✅ Script de preparación de datos
- ✅ Generador de datos sintéticos de ventas (mínimo 1 año)
- ✅ Feature engineering
- ✅ División train/test

**Servicios:**

1. **DataPreparation** (`apps/ai/services/data_preparation.py`)
   - Extrae ventas históricas
   - Crea features:
     - Fecha (día, mes, año, día de semana)
     - Categoría producto
     - Precio promedio
     - Descuentos aplicados
     - Cantidad vendida
   - Maneja valores nulos
   - Normalización

2. **FakeSalesGenerator** (`scripts/generate_fake_sales.py`)
   - Genera 365 días de ventas
   - Variación por día de semana
   - Tendencias (Black Friday, Navidad)
   - Datos realistas

**Estructura de datos:**

```python
# Features (X)
fecha_dia, fecha_mes, fecha_año, dia_semana, categoria_id, 
precio_promedio, descuento, es_fin_semana, es_feriado

# Target (y)
monto_total_ventas
```

---

### **DÍA 9 - Inteligencia Artificial (Entrenamiento y Predicción)** (8 horas)

**Entregables:**

- ✅ ModelTrainer (entrena Random Forest)
- ✅ Predictor (genera predicciones)
- ✅ Evaluator (métricas del modelo)
- ✅ Modelo entrenado y guardado (.pkl)
- ✅ APIs de predicción
- ✅ Dashboard de IA en frontend

**Servicios:**

1. **ModelTrainer** (`model_trainer.py`)
   ```python
   from sklearn.ensemble import RandomForestRegressor
   
   model = RandomForestRegressor(
       n_estimators=100,
       max_depth=10,
       min_samples_split=5,
       random_state=42
   )
   model.fit(X_train, y_train)
   ```

2. **Predictor** (`predictor.py`)
   - Carga modelo entrenado
   - Recibe parámetros (fecha, categoría)
   - Genera predicción
   - Calcula intervalo de confianza

3. **Evaluator** (`evaluator.py`)
   - Calcula métricas:
     - MSE (Mean Squared Error)
     - MAE (Mean Absolute Error)
     - R² Score
     - RMSE
   - Genera gráficos de evaluación

**APIs:**

```
POST        /api/ai/train/
POST        /api/ai/predict/
GET         /api/ai/models/
GET         /api/ai/models/{id}/metrics/
```

**Frontend:**

- Dashboard con predicciones
- Gráfico de ventas históricas vs predichas
- Filtros por categoría
- Exportar predicciones

---

## 📱 CICLO 3: APP MÓVIL Y FINALIZACIÓN (Días 10-12)

**Objetivo:** Aplicación móvil funcional, testing completo, deploy y documentación final.

### **DÍA 10 - App Móvil Flutter (Parte 1)** (8 horas)

**Entregables:**

- ✅ Proyecto Flutter configurado
- ✅ Autenticación (login/register)
- ✅ Navegación (tabs/drawer)
- ✅ Catálogo de productos (grid)
- ✅ Detalle de producto
- ✅ Carrito de compras
- ✅ Integración con API REST

**Pantallas:**

1. **Auth Screens:**
   - `LoginScreen`
   - `RegisterScreen`

2. **Main Screens:**
   - `HomeScreen` (productos destacados)
   - `ProductsScreen` (catálogo)
   - `ProductDetailScreen`
   - `CartScreen`
   - `ProfileScreen`

**Providers:**
- `AuthProvider` (estado de autenticación)
- `CartProvider` (carrito)
- `ProductsProvider` (productos)

---

### **DÍA 11 - App Móvil Flutter (Parte 2)** (8 horas)

**Entregables:**

- ✅ Checkout móvil
- ✅ Historial de pedidos
- ✅ Tracking de envíos
- ✅ Notificaciones Push (Firebase Cloud Messaging)
- ✅ Reconocimiento de voz para carrito
- ✅ Escaneo QR de productos
- ✅ Dashboard resumido (admin/empleados)

**Funcionalidades clave:**

1. **Notificaciones Push:**
   - Estado de pedido actualizado
   - Ofertas personalizadas
   - Recordatorio de carrito

2. **Voz en Carrito:**
   ```dart
   // Usuario dice: "Agregar camisa roja talla M"
   // Sistema procesa y agrega al carrito
   ```

3. **QR Scanner:**
   - Escanear código QR del producto
   - Agregar directamente al carrito

4. **Dashboard Móvil (Admin):**
   - Ventas del día
   - Pedidos pendientes
   - Gráfico de predicciones

**Pantallas:**
- `CheckoutScreen`
- `OrdersScreen`
- `OrderDetailScreen`
- `TrackingScreen`
- `DashboardScreen` (admin)
- `QRScannerScreen`

---

### **DÍA 12 - Testing, Deploy y Documentación Final** (8 horas)

**Entregables:**

- ✅ Testing completo (backend)
- ✅ Testing E2E (frontend)
- ✅ Deploy en nube (AWS/Azure/GCP)
- ✅ Documentación técnica completa
- ✅ Manual de usuario
- ✅ Video demo del sistema
- ✅ Presentación final

**Testing Backend:**
```bash
pytest --cov=apps --cov-report=html
```
- Tests unitarios (modelos, serializers)
- Tests de integración (APIs)
- Cobertura > 70%

**Testing Frontend:**
- Tests de componentes críticos
- Tests de flujos principales

**Deploy:**
1. Backend Django → AWS EC2 / Railway / Render
2. Frontend React → Vercel / Netlify
3. Base de datos → PostgreSQL managed (AWS RDS / ElephantSQL)
4. Storage → AWS S3
5. App móvil → Expo EAS Build

**Documentación:**
1. **Documentación Técnica:**
   - Arquitectura del sistema
   - Diagramas UML completos
   - Descripción de módulos
   - Guía de instalación

2. **Manual de Usuario:**
   - Guía paso a paso
   - Screenshots
   - Casos de uso

3. **Video Demo:**
   - 5-10 minutos
   - Mostrar todas las funcionalidades
   - Énfasis en IA y reportes

---

## 7. INTEGRACIONES DE IA

### 🧠 Random Forest Regressor - Predicción de Ventas

#### **Arquitectura del Modelo:**

```python
# apps/ai/services/model_trainer.py

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

class SalesModelTrainer:
    def __init__(self):
        self.model = None
        self.best_params = None
        
    def prepare_features(self, df):
        """
        Crea features a partir de datos de ventas
        """
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Features temporales
        df['dia'] = df['fecha'].dt.day
        df['mes'] = df['fecha'].dt.month
        df['año'] = df['fecha'].dt.year
        df['dia_semana'] = df['fecha'].dt.dayofweek  # 0=Lunes, 6=Domingo
        df['es_fin_semana'] = df['dia_semana'].isin([5, 6]).astype(int)
        
        # Features de producto
        # categoria_id ya existe en el df
        
        # Features de precio
        df['precio_promedio'] = df['total'] / df['cantidad']
        df['tiene_descuento'] = (df['descuento_aplicado'] > 0).astype(int)
        
        # Lags (ventas de días anteriores)
        df = df.sort_values('fecha')
        df['venta_dia_anterior'] = df['total'].shift(1).fillna(0)
        df['venta_semana_anterior'] = df['total'].shift(7).fillna(0)
        
        return df
    
    def train(self, sales_data):
        """
        Entrena el modelo Random Forest
        """
        df = self.prepare_features(sales_data)
        
        # Features (X)
        feature_cols = [
            'dia', 'mes', 'año', 'dia_semana', 'es_fin_semana',
            'categoria_id', 'precio_promedio', 'tiene_descuento',
            'venta_dia_anterior', 'venta_semana_anterior'
        ]
        
        X = df[feature_cols]
        y = df['total']  # Target: monto de ventas
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Hyperparameter tuning (opcional, consume tiempo)
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 15, 20],
            'min_samples_split': [5, 10]
        }
        
        rf = RandomForestRegressor(random_state=42)
        grid_search = GridSearchCV(
            rf, param_grid, cv=3, scoring='neg_mean_squared_error'
        )
        grid_search.fit(X_train, y_train)
        
        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_
        
        # Predicciones
        y_pred = self.model.predict(X_test)
        
        # Métricas
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        metrics = {
            'mse': mse,
            'mae': mae,
            'r2_score': r2,
            'rmse': rmse
        }
        
        # Guardar modelo
        model_path = f'apps/ai/models_ml/sales_model_{datetime.now().strftime("%Y%m%d")}.pkl'
        joblib.dump(self.model, model_path)
        
        return {
            'model_path': model_path,
            'metrics': metrics,
            'best_params': self.best_params
        }
```

#### **Servicio de Predicción:**

```python
# apps/ai/services/predictor.py

import joblib
import pandas as pd
from datetime import datetime, timedelta

class SalesPredictor:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
    
    def predict_next_month(self, categoria_id=None):
        """
        Predice ventas del próximo mes
        """
        today = datetime.now()
        next_month = today + timedelta(days=30)
        
        # Crear datos para predicción
        dates = pd.date_range(start=today, end=next_month, freq='D')
        
        predictions = []
        for date in dates:
            features = {
                'dia': date.day,
                'mes': date.month,
                'año': date.year,
                'dia_semana': date.dayofweek,
                'es_fin_semana': 1 if date.dayofweek >= 5 else 0,
                'categoria_id': categoria_id or 1,
                'precio_promedio': 50.0,  # Valor promedio histórico
                'tiene_descuento': 0,
                'venta_dia_anterior': 1000.0,  # Promedio
                'venta_semana_anterior': 7000.0  # Promedio
            }
            
            X = pd.DataFrame([features])
            pred = self.model.predict(X)[0]
            
            predictions.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'venta_predicha': round(pred, 2)
            })
        
        return predictions
```

#### **Endpoints de IA:**

```python
# apps/ai/views.py

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .services.model_trainer import SalesModelTrainer
from .services.predictor import SalesPredictor
from apps.orders.models import Pedido
import pandas as pd

class AIViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['post'])
    def train_model(self, request):
        """
        Entrena el modelo con datos históricos
        """
        # Obtener datos de ventas
        pedidos = Pedido.objects.filter(
            estado='entregado'
        ).values(
            'created_at', 'total', 'descuento_total'
        )
        
        # Convertir a DataFrame
        df = pd.DataFrame(list(pedidos))
        df.rename(columns={
            'created_at': 'fecha',
            'descuento_total': 'descuento_aplicado'
        }, inplace=True)
        
        # Entrenar
        trainer = SalesModelTrainer()
        result = trainer.train(df)
        
        # Guardar registro en BD
        EntrenamientoModelo.objects.create(
            tipo_modelo='random_forest_regressor',
            registros_entrenamiento=len(df),
            mse=result['metrics']['mse'],
            mae=result['metrics']['mae'],
            r2_score=result['metrics']['r2_score'],
            parametros=result['best_params'],
            archivo_modelo=result['model_path']
        )
        
        return Response({
            'status': 'success',
            'message': 'Modelo entrenado exitosamente',
            'metrics': result['metrics']
        })
    
    @action(detail=False, methods=['post'])
    def predict(self, request):
        """
        Genera predicción de ventas
        """
        categoria_id = request.data.get('categoria_id')
        periodo = request.data.get('periodo', 'mes')  # dia, semana, mes
        
        # Obtener último modelo entrenado
        ultimo_modelo = EntrenamientoModelo.objects.latest('created_at')
        
        # Predecir
        predictor = SalesPredictor(ultimo_modelo.archivo_modelo)
        predicciones = predictor.predict_next_month(categoria_id)
        
        # Guardar predicciones en BD
        for pred in predicciones:
            PrediccionVentas.objects.create(
                fecha_inicio_periodo=pred['fecha'],
                fecha_fin_periodo=pred['fecha'],
                periodo='dia',
                categoria_id=categoria_id,
                ventas_predichas=pred['venta_predicha'],
                confianza=0.85,
                modelo_version=str(ultimo_modelo.id)
            )
        
        return Response({
            'status': 'success',
            'predicciones': predicciones
        })
```

---

## 8. SISTEMA DE REPORTES DINÁMICOS

### 📊 Arquitectura del Sistema de Reportes

El sistema debe interpretar comandos en lenguaje natural (texto o voz) y generar reportes dinámicos.

#### **Componente 1: PromptParser**

```python
# apps/reports/prompt_parser.py

import re
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date

class PromptParser:
    """
    Interpreta prompts de texto y extrae parámetros
    """
    
    REPORT_TYPES = {
        'ventas': ['venta', 'ventas', 'pedido', 'pedidos', 'orden', 'ordenes'],
        'productos': ['producto', 'productos', 'articulo', 'articulos', 'inventario'],
        'clientes': ['cliente', 'clientes', 'comprador', 'compradores'],
        'stock': ['stock', 'inventario', 'existencia']
    }
    
    FORMATS = {
        'pdf': ['pdf'],
        'excel': ['excel', 'xls', 'xlsx'],
        'csv': ['csv'],
        'pantalla': ['pantalla', 'mostrar', 'ver']
    }
    
    def parse(self, prompt):
        """
        Parsea el prompt y retorna diccionario con parámetros
        """
        prompt_lower = prompt.lower()
        
        params = {
            'tipo_reporte': self._extract_report_type(prompt_lower),
            'fecha_inicio': None,
            'fecha_fin': None,
            'formato': self._extract_format(prompt_lower),
            'agrupacion': self._extract_grouping(prompt_lower),
            'filtros': {}
        }
        
        # Extraer fechas
        fecha_inicio, fecha_fin = self._extract_dates(prompt_lower)
        params['fecha_inicio'] = fecha_inicio
        params['fecha_fin'] = fecha_fin
        
        # Extraer filtros adicionales
        params['filtros'] = self._extract_filters(prompt_lower)
        
        return params
    
    def _extract_report_type(self, prompt):
        """Identifica el tipo de reporte"""
        for tipo, keywords in self.REPORT_TYPES.items():
            if any(kw in prompt for kw in keywords):
                return tipo
        return 'ventas'  # Default
    
    def _extract_format(self, prompt):
        """Identifica el formato solicitado"""
        for formato, keywords in self.FORMATS.items():
            if any(kw in prompt for kw in keywords):
                return formato
        return 'pantalla'  # Default
    
    def _extract_dates(self, prompt):
        """Extrae fechas del prompt"""
        today = datetime.now().date()
        
        # Casos especiales
        if 'hoy' in prompt or 'dia de hoy' in prompt:
            return today, today
        
        if 'ayer' in prompt:
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        
        if 'semana' in prompt:
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return start, end
        
        if 'mes' in prompt:
            # Buscar nombre del mes
            meses = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            
            for mes_nombre, mes_num in meses.items():
                if mes_nombre in prompt:
                    # Año actual
                    year = today.year
                    if mes_num > today.month:
                        year -= 1
                    
                    start = datetime(year, mes_num, 1).date()
                    # Último día del mes
                    if mes_num == 12:
                        end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                    else:
                        end = datetime(year, mes_num + 1, 1).date() - timedelta(days=1)
                    
                    return start, end
            
            # Si dice "del mes" sin especificar, usar mes actual
            start = datetime(today.year, today.month, 1).date()
            if today.month == 12:
                end = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
            return start, end
        
        # Buscar fechas explícitas (formato DD/MM/YYYY)
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        matches = re.findall(date_pattern, prompt)
        
        if len(matches) >= 2:
            try:
                start = parse_date(matches[0], dayfirst=True).date()
                end = parse_date(matches[1], dayfirst=True).date()
                return start, end
            except:
                pass
        
        # Default: último mes
        start = today - timedelta(days=30)
        return start, today
    
    def _extract_grouping(self, prompt):
        """Identifica agrupación solicitada"""
        if 'producto' in prompt or 'articulo' in prompt:
            return 'producto'
        if 'categoria' in prompt:
            return 'categoria'
        if 'cliente' in prompt:
            return 'cliente'
        if 'dia' in prompt or 'diario' in prompt:
            return 'dia'
        return None
    
    def _extract_filters(self, prompt):
        """Extrae filtros adicionales"""
        filtros = {}
        
        # Stock bajo
        if 'bajo stock' in prompt or 'stock bajo' in prompt:
            filtros['stock_bajo'] = True
        
        # Top N
        top_match = re.search(r'top\s+(\d+)', prompt)
        if top_match:
            filtros['limit'] = int(top_match.group(1))
        
        return filtros
```

#### **Componente 2: QueryBuilder**

```python
# apps/reports/query_builder.py

from django.db.models import Sum, Count, Avg, Q
from apps.orders.models import Pedido, DetallePedido
from apps.products.models import Prenda, StockPrenda
from apps.accounts.models import User

class QueryBuilder:
    """
    Construye queries Django ORM dinámicamente
    """
    
    def build_query(self, params):
        """
        Construye y ejecuta query basado en parámetros
        """
        tipo = params['tipo_reporte']
        
        if tipo == 'ventas':
            return self._query_ventas(params)
        elif tipo == 'productos':
            return self._query_productos(params)
        elif tipo == 'clientes':
            return self._query_clientes(params)
        elif tipo == 'stock':
            return self._query_stock(params)
        
        return []
    
    def _query_ventas(self, params):
        """Query de ventas"""
        queryset = Pedido.objects.filter(
            estado='entregado'
        )
        
        # Filtrar por fechas
        if params['fecha_inicio']:
            queryset = queryset.filter(
                created_at__date__gte=params['fecha_inicio']
            )
        if params['fecha_fin']:
            queryset = queryset.filter(
                created_at__date__lte=params['fecha_fin']
            )
        
        # Agrupar
        agrupacion = params.get('agrupacion')
        
        if agrupacion == 'producto':
            # Ventas por producto
            data = DetallePedido.objects.filter(
                pedido__in=queryset
            ).values(
                'prenda__nombre'
            ).annotate(
                total_ventas=Sum('subtotal'),
                cantidad_vendida=Sum('cantidad')
            ).order_by('-total_ventas')
            
        elif agrupacion == 'categoria':
            # Ventas por categoría
            data = DetallePedido.objects.filter(
                pedido__in=queryset
            ).values(
                'prenda__prenda_categoria__categoria__nombre'
            ).annotate(
                total_ventas=Sum('subtotal')
            ).order_by('-total_ventas')
            
        elif agrupacion == 'cliente':
            # Ventas por cliente
            data = queryset.values(
                'usuario__nombre',
                'usuario__apellido'
            ).annotate(
                total_ventas=Sum('total'),
                cantidad_compras=Count('id')
            ).order_by('-total_ventas')
            
        elif agrupacion == 'dia':
            # Ventas por día
            data = queryset.extra(
                select={'dia': 'DATE(created_at)'}
            ).values('dia').annotate(
                total_ventas=Sum('total'),
                cantidad_pedidos=Count('id')
            ).order_by('dia')
            
        else:
            # Sin agrupación, solo totales
            data = queryset.aggregate(
                total_ventas=Sum('total'),
                cantidad_pedidos=Count('id'),
                ticket_promedio=Avg('total')
            )
            data = [data]  # Convertir a lista
        
        # Aplicar límite si existe (Top N)
        if 'limit' in params['filtros']:
            data = list(data)[:params['filtros']['limit']]
        
        return list(data)
    
    def _query_productos(self, params):
        """Query de productos"""
        queryset = Prenda.objects.filter(activo=True)
        
        # Si hay filtro de stock bajo
        if params['filtros'].get('stock_bajo'):
            queryset = queryset.filter(stock_total__lt=10)
        
        data = queryset.values(
            'nombre', 'sku', 'stock_total', 'precio_venta'
        ).order_by('stock_total')
        
        if 'limit' in params['filtros']:
            data = data[:params['filtros']['limit']]
        
        return list(data)
    
    def _query_clientes(self, params):
        """Query de clientes"""
        # Top clientes
        data = User.objects.filter(
            rol__nombre='Cliente'
        ).annotate(
            total_compras=Count('pedido_set'),
            total_gastado=Sum('pedido_set__total')
        ).values(
            'nombre', 'apellido', 'email',
            'total_compras', 'total_gastado'
        ).order_by('-total_gastado')
        
        if 'limit' in params['filtros']:
            data = data[:params['filtros']['limit']]
        
        return list(data)
    
    def _query_stock(self, params):
        """Query de stock"""
        data = StockPrenda.objects.select_related(
            'prenda', 'talla'
        ).filter(
            stock__lt=10
        ).values(
            'prenda__nombre',
            'talla__nombre',
            'color',
            'stock'
        ).order_by('stock')
        
        return list(data)
```

#### **Componente 3: ReportGenerator**

```python
# apps/reports/generators/pdf_generator.py

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

class PDFReportGenerator:
    """
    Genera reportes en PDF con tablas y gráficos
    """
    
    def generate(self, data, titulo, filename):
        """
        Genera PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30
        )
        
        # Título
        title = Paragraph(titulo, title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Tabla de datos
        if isinstance(data, list) and len(data) > 0:
            # Crear tabla
            table_data = []
            
            # Headers
            headers = list(data[0].keys())
            table_data.append(headers)
            
            # Rows
            for row in data:
                table_data.append(list(row.values()))
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        # Construir PDF
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        # Guardar archivo
        with open(filename, 'wb') as f:
            f.write(pdf)
        
        return filename
```

```python
# apps/reports/generators/excel_generator.py

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference

class ExcelReportGenerator:
    """
    Genera reportes en Excel con formato y gráficos
    """
    
    def generate(self, data, titulo, filename):
        """
        Genera Excel
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        
        # Título
        ws['A1'] = titulo
        ws['A1'].font = Font(size=16, bold=True)
        ws.merge_cells('A1:E1')
        
        # Headers
        if isinstance(data, list) and len(data) > 0:
            headers = list(data[0].keys())
            
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=3, column=col)
                cell.value = header
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    start_color="366092",
                    end_color="366092",
                    fill_type="solid"
                )
                cell.alignment = Alignment(horizontal='center')
            
            # Datos
            for row_idx, row_data in enumerate(data, start=4):
                for col_idx, value in enumerate(row_data.values(), start=1):
                    ws.cell(row=row_idx, column=col_idx, value=value)
            
            # Ajustar anchos de columna
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column].width = adjusted_width
        
        # Guardar
        wb.save(filename)
        return filename
```

#### **API de Reportes:**

```python
# apps/reports/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .prompt_parser import PromptParser
from .query_builder import QueryBuilder
from .generators.pdf_generator import PDFReportGenerator
from .generators.excel_generator import ExcelReportGenerator
import os

class ReportsViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Genera reporte desde prompt de texto/voz
        """
        prompt = request.data.get('prompt', '')
        
        if not prompt:
            return Response({
                'error': 'Se requiere un prompt'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Parsear prompt
        parser = PromptParser()
        params = parser.parse(prompt)
        
        # 2. Construir query
        builder = QueryBuilder()
        data = builder.build_query(params)
        
        # 3. Generar reporte según formato
        formato = params['formato']
        
        if formato == 'pantalla':
            # Retornar JSON
            return Response({
                'status': 'success',
                'params': params,
                'data': data
            })
        
        elif formato == 'pdf':
            # Generar PDF
            generator = PDFReportGenerator()
            filename = f'media/reports/reporte_{request.user.id}_{int(time.time())}.pdf'
            os.makedirs('media/reports', exist_ok=True)
            
            generator.generate(
                data,
                titulo=f"Reporte de {params['tipo_reporte']}",
                filename=filename
            )
            
            # Guardar en BD
            ReporteGenerado.objects.create(
                usuario=request.user,
                tipo_reporte=params['tipo_reporte'],
                prompt_original=prompt,
                parametros_interpretados=params,
                formato='pdf',
                archivo_url=filename
            )
            
            # Retornar URL de descarga
            return Response({
                'status': 'success',
                'download_url': f'/api/reports/download/?file={filename}'
            })
        
        elif formato == 'excel':
            # Generar Excel
            generator = ExcelReportGenerator()
            filename = f'media/reports/reporte_{request.user.id}_{int(time.time())}.xlsx'
            os.makedirs('media/reports', exist_ok=True)
            
            generator.generate(
                data,
                titulo=f"Reporte de {params['tipo_reporte']}",
                filename=filename
            )
            
            # Guardar en BD
            ReporteGenerado.objects.create(
                usuario=request.user,
                tipo_reporte=params['tipo_reporte'],
                prompt_original=prompt,
                parametros_interpretados=params,
                formato='excel',
                archivo_url=filename
            )
            
            return Response({
                'status': 'success',
                'download_url': f'/api/reports/download/?file={filename}'
            })
    
    @action(detail=False, methods=['get'])
    def download(self, request):
        """
        Descarga archivo de reporte
        """
        filename = request.query_params.get('file')
        
        if not filename or not os.path.exists(filename):
            return Response({
                'error': 'Archivo no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(
            open(filename, 'rb'),
            as_attachment=True,
            filename=os.path.basename(filename)
        )
```

---

## 9. SEGURIDAD Y AUDITORÍA

### 🔒 Medidas de Seguridad

1. **Autenticación:**
   - JWT con refresh tokens
   - Expiración de tokens
   - Rate limiting en login (5 intentos/minuto)
   - Bloqueo temporal después de 5 intentos fallidos

2. **Autorización:**
   - RBAC (Role-Based Access Control)
   - Permisos granulares por recurso
   - Verificación de permisos en cada endpoint

3. **Datos:**
   - Passwords hasheados con bcrypt (Django default)
   - Validación de datos con serializers
   - Sanitización de inputs
   - Protección CSRF

4. **API:**
   - HTTPS obligatorio en producción
   - CORS configurado (origins permitidos)
   - Rate limiting (100 req/min por IP)

5. **Auditoría:**
   - Logs de TODAS las acciones críticas
   - IP, User-Agent, timestamps
   - Cambios before/after en JSONB
   - Logs inmutables (solo INSERT)

### 🕵️ Sistema de Auditoría

```python
# apps/audit/middleware.py

from .models import Auditoria
import json

class AuditMiddleware:
    """
    Middleware que registra todas las acciones
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Solo auditar métodos que modifican datos
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self._log_action(request, response)
        
        return response
    
    def _log_action(self, request, response):
        """Registra la acción en la tabla de auditoría"""
        
        # Extraer información
        usuario = request.user if request.user.is_authenticated else None
        path = request.path
        metodo = request.method
        
        # Datos del request
        try:
            datos_request = json.loads(request.body) if request.body else {}
        except:
            datos_request = {}
        
        # IP y User-Agent
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Guardar en BD
        Auditoria.objects.create(
            usuario=usuario,
            accion=f"{metodo} {path}",
            entidad=self._extract_entity(path),
            entidad_id=self._extract_entity_id(path),
            cambios={
                'request': datos_request,
                'status_code': response.status_code
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _extract_entity(self, path):
        """Extrae el nombre de la entidad del path"""
        parts = path.strip('/').split('/')
        if len(parts) >= 3:
            return parts[2]  # /api/products/ -> products
        return 'unknown'
    
    def _extract_entity_id(self, path):
        """Extrae el ID de la entidad si existe"""
        parts = path.strip('/').split('/')
        if len(parts) >= 4:
            try:
                return parts[3]
            except:
                pass
        return None
```

---

## 10. APIS Y SWAGGER

### 📚 Documentación Swagger

**Configuración:**

```python
# config/settings/base.py

INSTALLED_APPS = [
    ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'SmartSales365 API',
    'DESCRIPTION': 'Sistema Inteligente de Gestión Comercial con IA',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

**URLs:**

```python
# config/urls.py

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Schema & Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Routes
    path('api/auth/', include('apps.accounts.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/ai/', include('apps.ai.urls')),
    # ... más rutas
]
```

**Acceso a documentación:**
- `/api/docs/` - Swagger UI (interactiva)
- `/api/redoc/` - ReDoc (documentación estática)
- `/api/schema/` - Schema OpenAPI (JSON)

---

## 11. DEPLOYMENT

### 🚀 Stack de Producción

#### **Opción 1: AWS**

```
┌─────────────────────────────────────────┐
│  Route 53 (DNS)                         │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  CloudFront (CDN)                       │
└───────────────┬─────────────────────────┘
                │
        ┌───────┴──────┐
        │              │
┌───────▼──────┐  ┌───▼────────────┐
│ S3 (React)   │  │ ALB            │
└──────────────┘  └───┬────────────┘
                      │
                 ┌────▼─────┐
                 │ EC2/ECS  │
                 │ (Django) │
                 └────┬─────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
     ┌────▼───┐  ┌───▼──┐   ┌───▼────┐
     │RDS     │  │ S3   │   │ElastiC │
     │(Postgr)│  │(Media│   │ache    │
     └────────┘  └──────┘   │(Redis) │
                             └────────┘
```

**Servicios:**
- **Frontend:** S3 + CloudFront
- **Backend:** EC2 (t3.medium) o ECS (Fargate)
- **Base de datos:** RDS PostgreSQL
- **Cache:** ElastiCache Redis
- **Storage:** S3
- **CDN:** CloudFront

#### **Opción 2: Railway / Render (Más rápido)**

- Backend: Railway/Render
- Frontend: Vercel/Netlify
- BD: PostgreSQL managed
- Storage: AWS S3

### 🔧 Variables de Entorno

```bash
# Backend .env (Producción)
DEBUG=False
SECRET_KEY=<random-key-256-chars>
ALLOWED_HOSTS=api.smartsales365.com

DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0

# AWS
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=smartsales365-media
AWS_S3_REGION_NAME=us-east-1

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# PayPal
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...
PAYPAL_MODE=live

# Email
SENDGRID_API_KEY=SG...
DEFAULT_FROM_EMAIL=noreply@smartsales365.com

# FCM (Firebase)
FCM_SERVER_KEY=AAAA...
```

### 📦 Dockerfile

```dockerfile
# backend/Dockerfile

FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Colectar archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 🐳 Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: smartsales365_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/smartsales365_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  celery:
    build: ./backend
    command: celery -A config worker -l info
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/smartsales365_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

## 12. ROLES DEL EQUIPO

### 👥 División de Trabajo (2 personas)

#### **PERSONA 1: Backend + IA**

**Responsabilidades:**

**Ciclo 1 (Días 1-5):**
- Setup completo del proyecto Django
- Base de datos y migraciones
- Sistema de autenticación (JWT)
- Modelos de productos y stock
- APIs de carrito
- APIs de pedidos y pagos
- Integración con Stripe

**Ciclo 2 (Días 6-9):**
- Sistema de reportes dinámicos:
  - PromptParser
  - QueryBuilder
  - Generadores (PDF/Excel)
- Inteligencia Artificial:
  - Preparación de datos
  - Entrenamiento del modelo
  - Servicio de predicción
  - APIs de IA

**Ciclo 3 (Días 10-12):**
- Testing backend (pytest)
- Deploy del backend
- Documentación técnica (UML)
- Soporte a frontend/móvil

#### **PERSONA 2: Frontend + Móvil**

**Responsabilidades:**

**Ciclo 1 (Días 1-5):**
- Setup React + Vite
- Autenticación UI
- Catálogo de productos (grid/lista)
- Detalle de producto
- Carrito de compras
- Checkout

**Ciclo 2 (Días 6-9):**
- Dashboard analítico (gráficos)
- Interfaz de reportes:
  - Input de texto
  - Reconocimiento de voz (Web Speech API)
  - Visualización de resultados
- Integración con IA (predicciones)
- Páginas de gestión (admin/empleado)

**Ciclo 3 (Días 10-12):**
- App móvil Flutter (todas las pantallas)
- Notificaciones push (FCM)
- Reconocimiento de voz móvil
- Testing E2E
- Deploy frontend/móvil
- Video demo

---

## ✅ CHECKLIST FINAL

### **Presentación 1 (Martes 28/10 - 23:59):**

- [ ] Backend: Autenticación, productos, carrito funcionando
- [ ] Frontend: Login, catálogo, carrito
- [ ] Base de datos completa
- [ ] Seeders con datos de prueba
- [ ] APIs documentadas (Swagger)
- [ ] Demo funcional

### **Presentación 2 (Martes 04/11 - 23:59):**

- [ ] Sistema de reportes dinámicos completo (texto y voz)
- [ ] IA: Modelo entrenado y predicciones funcionando
- [ ] Dashboard analítico
- [ ] Todas las APIs completas
- [ ] Frontend avanzado
- [ ] Demo de reportes y predicciones

### **Presentación 3 (Martes 11/11 - 23:59):**

- [ ] App móvil funcional (Android/iOS)
- [ ] Notificaciones push
- [ ] Deploy completo
- [ ] Testing > 70%
- [ ] Documentación completa (UML, manual)
- [ ] Video demo

### **Defensa Final (Jueves 13/11):**

- [ ] Proyecto 100% funcional
- [ ] Documentación técnica impresa
- [ ] Manual de usuario
- [ ] Video demo de 5-10 min
- [ ] Presentación PowerPoint
- [ ] Código limpio y comentado
- [ ] QR a repositorio GitHub

---

## 📚 RECURSOS TÉCNICOS

### **Python / Backend:**

```bash
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.0
pip install psycopg2-binary==2.9.9
pip install python-decouple==3.8
pip install drf-spectacular==0.26.5
pip install celery==5.3.4
pip install redis==5.0.1
pip install boto3==1.29.7  # AWS S3
pip install stripe==7.0.0
pip install reportlab==4.0.7
pip install openpyxl==3.1.2
pip install pandas==2.1.3
pip install scikit-learn==1.3.2
pip install joblib==1.3.2
pip install matplotlib==3.8.2
```

### **React / Frontend:**

```bash
npm create vite@latest frontend -- --template react-ts
npm install axios
npm install react-router-dom
npm install zustand
npm install react-hook-form
npm install zod
npm install @hookform/resolvers
npm install recharts
npm install react-toastify
npm install lucide-react
npm install clsx tailwind-merge
```

### **Flutter / Móvil:**

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # HTTP
  dio: ^5.3.3
  
  # Estado
  provider: ^6.0.5
  
  # Almacenamiento
  shared_preferences: ^2.2.2
  hive: ^2.2.3
  
  # Navegación
  go_router: ^12.0.1
  
  # UI
  google_fonts: ^6.1.0
  
  # Notificaciones
  firebase_core: ^2.24.0
  firebase_messaging: ^14.7.4
  
  # Voz
  speech_to_text: ^6.5.1
  
  # QR
  mobile_scanner: ^3.5.5
  
  # Mapas
  google_maps_flutter: ^2.5.0
```

---

## 🎓 PROCESO UNIFICADO (PUDS)

El proyecto debe seguir el **Proceso Unificado de Desarrollo de Software** con **UML 2.5+**.

### **Documentación requerida:**

1. **Captura de Requisitos:**
   - Casos de uso
   - Diagrama de casos de uso
   - Especificación de casos de uso

2. **Análisis:**
   - Diagrama de clases (conceptual)
   - Diagrama de secuencia
   - Diagrama de actividades

3. **Diseño:**
   - Diagrama de clases (diseño)
   - Diagrama de componentes
   - Diagrama de despliegue
   - Modelo ER de base de datos

4. **Implementación:**
   - Código fuente
   - Documentación de APIs

5. **Pruebas:**
   - Plan de pruebas
   - Casos de prueba
   - Resultados

---

## 🚨 ADVERTENCIAS FINALES

1. **NO COPIAR CÓDIGO:** Se penalizará la copia literal entre grupos
2. **COMMITS CONSTANTES:** GitHub debe mostrar trabajo progresivo
3. **TRABAJO EN PAREJA:** Ambos deben dominar todo el sistema
4. **IA DEBE SER REAL:** El modelo debe estar entrenado y funcionar
5. **REPORTES POR VOZ:** Debe funcionar de verdad (no fake)
6. **DATOS REALISTAS:** Usar seeders con datos coherentes

---

## 📞 SOPORTE

Si necesitas ayuda durante el desarrollo:

1. Revisa esta guía completa
2. Consulta los archivos `PLAN_ACCION_DIA_*.md`
3. Revisa la documentación de las tecnologías
4. Consulta con tu compañero de equipo

---

**¡ÉXITO EN TU PROYECTO! 🚀**

*SmartSales365 - Sistema Inteligente de Gestión Comercial con IA*
