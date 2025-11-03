# 🛍️ SMARTSALES365 - SISTEMA INTELIGENTE DE GESTIÓN COMERCIAL

## RESUMEN COMPLETO - GUÍA MAESTRA DEL PROYECTO

**Versión:** 2.0 Final (Sin Docker)  
**Última actualización:** Noviembre 2025  
**Duración total:** 12 días (3 ciclos)  
**Equipo:** 2 personas  
**Stack:** Django + React + Flutter + PostgreSQL + AWS

---

## 📋 TABLA DE CONTENIDOS

1. [Visión General del Proyecto](#1-visión-general-del-proyecto)
2. [Estructura de Repositorios](#2-estructura-de-repositorios)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Arquitectura del Sistema](#4-arquitectura-del-sistema)
5. [Base de Datos](#5-base-de-datos)
6. [Planificación de Ciclos (12 días)](#6-planificación-de-ciclos-12-días)
7. [Integraciones de IA](#7-integraciones-de-ia)
8. [Sistema de Reportes Dinámicos](#8-sistema-de-reportes-dinámicos)
9. [Seguridad y Auditoría](#9-seguridad-y-auditoría)
10. [Deployment (AWS)](#10-deployment-aws)
11. [Roles del Equipo](#11-roles-del-equipo)

---

## 1. VISIÓN GENERAL DEL PROYECTO

### 🎯 Objetivo

Desarrollar **SmartSales365**, un Sistema Inteligente de Gestión Comercial híbrido (POS + E-Commerce) que combine funcionalidades tradicionales de gestión de ventas con componentes de Inteligencia Artificial aplicada.

### 🎓 Contexto Académico

**Segundo Examen Parcial** - Sistemas de Información II  
**Duración:** 12 días naturales (3 ciclos de desarrollo)  
**Modalidad:** Trabajo en pareja (2 personas)

### ✅ FUNCIONALIDADES MÍNIMAS OBLIGATORIAS

#### **a) Gestión Comercial Básica**

1. **Gestión de Productos (Ropa Femenina):**

   - CRUD completo de productos
   - Atributos: categorías, tallas, colores, marcas
   - Inventario centralizado con alertas de stock mínimo
   - Galería de imágenes por producto

2. **Gestión de Clientes:**

   - Registro y perfil
   - Direcciones múltiples de envío
   - Historial de compras
   - Billetera virtual

3. **Carrito de Compra:**

   - Agregar/quitar productos
   - Selección de talla y color
   - Aplicación de descuentos
   - **Comandos por texto y voz** ✨

4. **Gestión de Ventas:**

   - Ventas presenciales (POS)
   - Ventas online (E-Commerce)
   - Métodos de pago: Efectivo, Tarjeta (Stripe/PayPal), Billetera Virtual
   - Emisión de comprobantes
   - Seguimiento de estados del pedido

5. **Gestión de Envíos:**
   - Asignación a agencias externas o delivery propio
   - Tracking de pedidos
   - Gestión de estados de entrega

#### **b) Generación Dinámica de Reportes (Texto o Voz)** ⭐

**Ejemplos de prompts válidos:**

```
"Quiero un reporte de ventas del mes de septiembre, agrupado por producto, en PDF"
"Dame las ventas de hoy en pantalla"
"Muéstrame los productos con bajo stock"
"Reporte de los 10 clientes que más han comprado este mes"
```

**Proceso del sistema:**

1. Capturar prompt (texto o voz → texto)
2. Interpretar comando (PromptParser)
3. Construir query dinámico (QueryBuilder)
4. Generar reporte (PDF/Excel/Pantalla)

#### **c) Dashboard de Predicción de Ventas (IA)** 🤖

- **Modelo:** Random Forest Regressor (scikit-learn)
- **Features:** fecha, categoría, precio, promociones, día de semana
- **Target:** monto de ventas
- **Métricas:** MSE, MAE, R²

#### **d) Aplicación Móvil (Flutter)** 📱

**Funcionalidades prioritarias:**

- Compra rápida con escaneo QR
- Carrito y checkout móvil
- Notificaciones Push (Firebase)
- Dashboard resumido (admin/empleados)
- Tracking de envíos en tiempo real

---

## 2. ESTRUCTURA DE REPOSITORIOS

### 📦 3 REPOSITORIOS SEPARADOS

Este proyecto está dividido en **3 repositorios independientes** para mejor organización:

```
📁 smartsales365-backend/      (Repositorio 1)
📁 smartsales365-frontend/     (Repositorio 2)
📁 smartsales365-mobile/       (Repositorio 3)
```

#### **Repositorio 1: Backend (Django)**

```
smartsales365-backend/
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
├── .env.example
├── .gitignore
├── manage.py
│
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── __init__.py
│   ├── core/              # Modelos base, utilidades
│   ├── accounts/          # Usuarios, roles, permisos
│   ├── products/          # Catálogo de productos
│   ├── customers/         # Clientes y direcciones
│   ├── cart/              # Carrito de compras
│   ├── orders/            # Pedidos y pagos
│   ├── shipping/          # Envíos y delivery
│   ├── promotions/        # Descuentos y cupones
│   ├── reviews/           # Reseñas de productos
│   ├── reports/           # Reportes dinámicos ⭐
│   ├── analytics/         # Dashboard y estadísticas
│   ├── ai/                # Predicciones ML ⭐
│   ├── notifications/     # Notificaciones push/email
│   └── audit/             # Logs de auditoría
│
├── scripts/
│   ├── seed_data.py       # Seeders centralizados
│   └── train_ml_model.py  # Entrenamiento del modelo IA
│
├── static/
├── media/
└── docs/
    ├── API_DOCS.md
    └── DEPLOYMENT.md
```

#### **Repositorio 2: Frontend (React + TypeScript)**

```
smartsales365-frontend/
├── README.md
├── CONTRIBUTING.md
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── .env.example
├── .gitignore
│
├── public/
│   ├── favicon.ico
│   └── assets/
│
└── src/
    ├── main.tsx
    ├── App.tsx
    │
    ├── assets/            # Imágenes, iconos, fonts
    │   ├── images/
    │   ├── icons/
    │   └── fonts/
    │
    ├── components/        # Componentes reutilizables
    │   ├── common/       # Button, Input, Modal, etc.
    │   ├── layout/       # Navbar, Sidebar, Footer
    │   ├── products/     # ProductCard, ProductGrid
    │   ├── cart/         # CartItem, CartSummary
    │   └── forms/        # FormField, FormGroup
    │
    ├── pages/            # Páginas principales
    │   ├── auth/
    │   │   ├── LoginPage.tsx
    │   │   └── RegisterPage.tsx
    │   ├── dashboard/
    │   │   ├── AdminDashboard.tsx
    │   │   └── ClientDashboard.tsx
    │   ├── products/
    │   │   ├── ProductsListPage.tsx
    │   │   └── ProductDetailPage.tsx
    │   ├── cart/
    │   │   └── CartPage.tsx
    │   ├── checkout/
    │   │   └── CheckoutPage.tsx
    │   ├── orders/
    │   │   ├── OrdersListPage.tsx
    │   │   └── OrderDetailPage.tsx
    │   ├── reports/
    │   │   └── ReportsPage.tsx
    │   └── analytics/
    │       └── AnalyticsPage.tsx
    │
    ├── services/         # API calls
    │   ├── api.ts
    │   ├── auth.service.ts
    │   ├── products.service.ts
    │   ├── cart.service.ts
    │   ├── orders.service.ts
    │   ├── reports.service.ts
    │   └── voice.service.ts
    │
    ├── hooks/            # Custom hooks
    │   ├── useAuth.ts
    │   ├── useCart.ts
    │   ├── useVoice.ts
    │   └── useDebounce.ts
    │
    ├── store/            # Estado global (Zustand)
    │   ├── authStore.ts
    │   ├── cartStore.ts
    │   └── index.ts
    │
    ├── utils/            # Utilidades
    │   ├── constants.ts
    │   ├── helpers.ts
    │   ├── formatters.ts
    │   └── validators.ts
    │
    ├── types/            # TypeScript types
    │   ├── index.ts
    │   ├── auth.types.ts
    │   ├── product.types.ts
    │   └── order.types.ts
    │
    ├── styles/           # Estilos globales
    │   └── globals.css
    │
    └── router/           # Configuración de rutas
        └── index.tsx
```

#### **Repositorio 3: Mobile (Flutter)**

```
smartsales365-mobile/
├── README.md
├── CONTRIBUTING.md
├── pubspec.yaml
├── analysis_options.yaml
├── .gitignore
│
├── android/
├── ios/
├── web/
│
└── lib/
    ├── main.dart
    │
    ├── config/
    │   ├── theme.dart
    │   ├── routes.dart
    │   └── constants.dart
    │
    ├── models/
    │   ├── user.dart
    │   ├── product.dart
    │   ├── order.dart
    │   └── cart.dart
    │
    ├── providers/
    │   ├── auth_provider.dart
    │   ├── cart_provider.dart
    │   └── products_provider.dart
    │
    ├── services/
    │   ├── api_service.dart
    │   ├── auth_service.dart
    │   ├── voice_service.dart
    │   ├── notification_service.dart
    │   └── storage_service.dart
    │
    ├── screens/
    │   ├── auth/
    │   ├── home/
    │   ├── products/
    │   ├── cart/
    │   ├── orders/
    │   ├── profile/
    │   └── dashboard/
    │
    ├── widgets/
    │   ├── common/
    │   ├── products/
    │   └── cart/
    │
    └── utils/
        ├── helpers.dart
        └── validators.dart
```

---

## 3. STACK TECNOLÓGICO

### 🔧 Backend

- **Framework:** Django 4.2 + Django REST Framework 3.14
- **Base de Datos:** PostgreSQL 14+
- **Autenticación:** JWT (`djangorestframework-simplejwt`)
- **Tareas Asíncronas:** Celery 5.3 + Redis
- **Storage:** AWS S3
- **Email:** SendGrid / AWS SES
- **Pagos:** Stripe + PayPal
- **IA:** scikit-learn, pandas, numpy
- **Reportes:** reportlab, openpyxl

### 🎨 Frontend Web

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **UI:** Tailwind CSS + shadcn/ui
- **Estado:** Zustand
- **HTTP:** Axios
- **Routing:** React Router v6
- **Forms:** React Hook Form + Zod
- **Gráficos:** Recharts
- **Voz:** Web Speech API

### 📱 Frontend Móvil

- **Framework:** Flutter 3.x
- **Estado:** Provider / Riverpod
- **HTTP:** Dio
- **Storage:** Hive / Shared Preferences
- **Push:** Firebase Cloud Messaging
- **Voz:** speech_to_text
- **QR:** mobile_scanner

### 🛠️ DevOps

- **Control de Versiones:** Git + GitHub (3 repos)
- **CI/CD:** GitHub Actions
- **Deploy:** AWS (EC2, RDS, S3, CloudFront)
- **Documentación:** Swagger (drf-spectacular)
- **Testing:** pytest, pytest-django
- **Linting:** Black, Flake8, isort

---

## 4. ARQUITECTURA DEL SISTEMA

### 🏗️ Arquitectura General (Sin Docker)

```
┌────────────────────────────────────────────────────────────────┐
│                         CLIENTES                               │
├──────────────────────┬─────────────────────┬───────────────────┤
│   React Web App      │   Flutter Mobile    │   Admin Panel     │
│   (Vercel/Netlify)   │   (iOS + Android)   │   (Django Admin)  │
└──────────────────────┴─────────────────────┴───────────────────┘
                              ▼ HTTPS/REST
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO REST FRAMEWORK                        │
│                    (AWS EC2 / Railway)                          │
├─────────────────────────────────────────────────────────────────┤
│  • Authentication (JWT)                                         │
│  • Permissions (RBAC)                                           │
│  • Report Generator (PromptParser + QueryBuilder)              │
│  • ML Service (Random Forest)                                  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────┬───────────────────┬─────────────────────────┐
│   PostgreSQL     │   Redis           │   AWS S3                │
│   (AWS RDS)      │   (ElastiCache)   │   (Imágenes/Reports)    │
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
apps/
├── core/              → Modelos base, utilidades, constantes
├── accounts/          → Usuarios, roles, permisos (JWT)
├── products/          → Catálogo (Prenda, Categoría, Marca, Talla, Stock)
├── customers/         → Clientes, direcciones, favoritos
├── cart/              → Carrito de compras (con voz)
├── orders/            → Pedidos, pagos (Stripe/PayPal), estados
├── shipping/          → Envíos, tracking, agencias delivery
├── promotions/        → Descuentos, cupones
├── reviews/           → Reseñas de productos
├── reports/           → 🌟 Reportes dinámicos (PromptParser, QueryBuilder)
├── analytics/         → Dashboard, estadísticas
├── ai/                → 🤖 Predicciones ML (Random Forest)
├── notifications/     → Push notifications (FCM)
└── audit/             → Logs de auditoría
```

---

## 5. BASE DE DATOS

### 📊 Diseño de Base de Datos

**30 tablas** organizadas en **11 módulos funcionales**:

| #   | Módulo         | Tablas                                                                         | Total |
| --- | -------------- | ------------------------------------------------------------------------------ | ----- |
| 1   | Autenticación  | rol, permiso, permiso_rol, usuario, direccion                                  | 5     |
| 2   | Catálogo       | categoria, marca, talla, prenda, prenda_categoria, stock_prenda, imagen_prenda | 7     |
| 3   | Promociones    | descuento, descuento_prenda                                                    | 2     |
| 4   | Ventas         | pedido, detalle_pedido, historial_estado_pedido, pago, metodo_pago             | 5     |
| 5   | Envíos         | envio, agencia_delivery                                                        | 2     |
| 6   | Carrito        | carrito, item_carrito                                                          | 2     |
| 7   | Social         | resena, favoritos                                                              | 2     |
| 8   | Notificaciones | notificacion                                                                   | 1     |
| 9   | Reportes       | reporte_generado                                                               | 1     |
| 10  | IA             | prediccion_ventas, entrenamiento_modelo                                        | 2     |
| 11  | Auditoría      | auditoria                                                                      | 1     |

### 🔑 Características:

- ✅ **UUIDs** como primary keys
- ✅ **Soft Deletes** (deleted_at)
- ✅ **Timestamps** (created_at, updated_at)
- ✅ **JSONB** para metadata flexible
- ✅ **Índices** optimizados
- ✅ **Extensiones:** uuid-ossp, pgcrypto

---

## 6. PLANIFICACIÓN DE CICLOS (12 DÍAS)

### 📅 Calendario General

| Ciclo       | Días  | Duración | Objetivo                            |
| ----------- | ----- | -------- | ----------------------------------- |
| **CICLO 1** | 1-5   | 5 días   | Backend completo + Frontend básico  |
| **CICLO 2** | 6-9   | 4 días   | IA + Reportes Dinámicos + Dashboard |
| **CICLO 3** | 10-12 | 3 días   | App Móvil + Deploy + Documentación  |

---

### 🎯 CICLO 1: FUNDACIÓN (Días 1-5)

#### **DÍA 1 - Setup y Autenticación** ⚡

**Entregables:**

- ✅ Proyecto Django configurado (sin Docker)
- ✅ PostgreSQL funcionando
- ✅ Modelos: User, Role, Permission
- ✅ JWT funcionando
- ✅ 4 roles: Admin, Empleado, Cliente, Delivery
- ✅ Seeders centralizados en `/scripts/seed_data.py`
- ✅ Swagger documentado

**APIs:**

```
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/register/
GET  /api/auth/users/
GET  /api/auth/users/me/
POST /api/auth/users/{id}/change-password/
```

---

#### **DÍA 2 - Catálogo de Productos** 🛍️

**Entregables:**

- ✅ Modelos: Categoria, Marca, Talla, Prenda, StockPrenda, ImagenPrenda
- ✅ Upload de imágenes a AWS S3
- ✅ Filtros y búsqueda avanzada
- ✅ 50+ productos en seeders
- ✅ APIs CRUD completas

**APIs:**

```
GET/POST    /api/products/categories/
GET/POST    /api/products/brands/
GET/POST    /api/products/sizes/
GET/POST    /api/products/
GET         /api/products/{id}/
GET         /api/products/search/
POST        /api/products/{id}/images/
GET/PUT     /api/products/{id}/stock/
```

---

#### **DÍA 3 - Carrito y Clientes** 🛒

**Entregables:**

- ✅ Modelos: Direccion, Favoritos, Carrito, ItemCarrito
- ✅ Sistema de carrito persistente
- ✅ Billetera virtual
- ✅ Direcciones múltiples

**APIs:**

```
GET/PUT     /api/customers/profile/
GET/POST    /api/customers/addresses/
GET         /api/customers/wallet/
POST        /api/customers/wallet/recharge/

GET         /api/cart/
POST        /api/cart/add/
PUT         /api/cart/items/{id}/
DELETE      /api/cart/items/{id}/

GET/POST    /api/favorites/
```

---

#### **DÍA 4 - Pedidos y Pagos** 💳

**Entregables:**

- ✅ Modelos: Pedido, DetallePedido, Pago, MetodoPago
- ✅ Integración Stripe + PayPal
- ✅ Estados de pedido (workflow)
- ✅ Billetera Virtual

**APIs:**

```
POST        /api/orders/checkout/
GET         /api/orders/
GET         /api/orders/{id}/
PUT         /api/orders/{id}/status/
POST        /api/payments/process/
POST        /api/payments/stripe/webhook/
```

---

#### **DÍA 5 - Envíos y Frontend Básico** 🚚🎨

**Backend:**

- ✅ Modelos: Envio, AgenciaDelivery
- ✅ Tracking de pedidos

**Frontend (React):**

- ✅ Setup React + Vite + TypeScript
- ✅ Login/Register
- ✅ Catálogo de productos
- ✅ Carrito de compras
- ✅ Checkout
- ✅ Dashboard básico (Admin/Cliente)

**Páginas:**

```
/login
/register
/ (home - productos)
/products/:id
/cart
/checkout
/dashboard (admin)
/dashboard/client (cliente)
```

---

### 🤖 CICLO 2: IA Y REPORTES (Días 6-9)

#### **DÍA 6 - Reportes Dinámicos (Parser)** 📊

**Entregables:**

- ✅ PromptParser (interpreta texto/voz)
- ✅ QueryBuilder (construye queries)
- ✅ Reporte en pantalla (JSON)

**Ejemplos de prompts:**

```
"Ventas del mes de octubre"
"Productos con stock menor a 10"
"Top 10 clientes que más compraron"
```

---

#### **DÍA 7 - Reportes (PDF/Excel) + Voz** 🎤📄

**Entregables:**

- ✅ Generadores PDF (reportlab)
- ✅ Generadores Excel (openpyxl)
- ✅ Web Speech API en frontend
- ✅ Componente de reconocimiento de voz

---

#### **DÍA 8 - IA (Preparación de Datos)** 🧠

**Entregables:**

- ✅ Script de preparación de datos
- ✅ Generador de ventas sintéticas (365 días)
- ✅ Feature engineering
- ✅ Modelos: PrediccionVentas, EntrenamientoModelo

---

#### **DÍA 9 - IA (Entrenamiento)** 🚀

**Entregables:**

- ✅ Random Forest Regressor entrenado
- ✅ Predictor de ventas funcionando
- ✅ Dashboard de IA en frontend
- ✅ Gráficos de predicciones

---

### 📱 CICLO 3: MÓVIL Y DEPLOY (Días 10-12)

#### **DÍA 10 - App Móvil (Parte 1)** 📱

**Entregables:**

- ✅ Setup Flutter
- ✅ Login/Register
- ✅ Catálogo de productos
- ✅ Carrito de compras

---

#### **DÍA 11 - App Móvil (Parte 2)** 🔔

**Entregables:**

- ✅ Checkout móvil
- ✅ Notificaciones Push (FCM)
- ✅ Reconocimiento de voz
- ✅ Escaneo QR
- ✅ Dashboard móvil (admin)

---

#### **DÍA 12 - Deploy y Documentación** 🚀📝

**Entregables:**

- ✅ Testing completo (>70% cobertura)
- ✅ Deploy en AWS:
  - Backend → EC2 / Railway
  - Frontend → Vercel / Netlify
  - BD → AWS RDS
  - Storage → AWS S3
- ✅ Documentación técnica (UML)
- ✅ Manual de usuario
- ✅ Video demo (5-10 min)

---

## 7. INTEGRACIONES DE IA

### 🧠 Random Forest Regressor

**Código ejemplo:**

```python
# apps/ai/services/model_trainer.py

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib

class SalesModelTrainer:
    def prepare_features(self, df):
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['dia'] = df['fecha'].dt.day
        df['mes'] = df['fecha'].dt.month
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['es_fin_semana'] = df['dia_semana'].isin([5, 6]).astype(int)
        return df

    def train(self, sales_data):
        df = self.prepare_features(sales_data)

        X = df[['dia', 'mes', 'dia_semana', 'es_fin_semana', 'categoria_id']]
        y = df['total']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        joblib.dump(model, 'apps/ai/models_ml/sales_model.pkl')
        return model
```

---

## 8. SISTEMA DE REPORTES DINÁMICOS

### 📊 PromptParser

**Código ejemplo:**

```python
# apps/reports/prompt_parser.py

import re
from datetime import datetime, timedelta

class PromptParser:
    def parse(self, prompt):
        params = {
            'tipo_reporte': self._extract_report_type(prompt),
            'fecha_inicio': None,
            'fecha_fin': None,
            'formato': self._extract_format(prompt),
            'filtros': {}
        }

        # Extraer fechas
        if 'hoy' in prompt:
            params['fecha_inicio'] = datetime.now().date()
            params['fecha_fin'] = datetime.now().date()
        elif 'mes' in prompt:
            # Lógica para extraer mes específico
            pass

        return params
```

---

## 9. SEGURIDAD Y AUDITORÍA

### 🔒 Medidas de Seguridad

1. **JWT** con refresh tokens
2. **RBAC** granular
3. **Rate limiting** (5 intentos/min en login)
4. **HTTPS** obligatorio en producción
5. **Logs de auditoría** inmutables

### 🕵️ Sistema de Auditoría

```python
# apps/audit/middleware.py

class AuditMiddleware:
    def __call__(self, request):
        response = self.get_response(request)

        if request.method in ['POST', 'PUT', 'DELETE']:
            Auditoria.objects.create(
                usuario=request.user,
                accion=f"{request.method} {request.path}",
                ip_address=self._get_client_ip(request),
                cambios={'status': response.status_code}
            )

        return response
```

---

## 10. DEPLOYMENT (AWS)

### 🚀 Arquitectura AWS

```
┌─────────────────────────────────────────┐
│  Route 53 (DNS)                         │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  CloudFront (CDN) → S3 (React Static)   │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  EC2 (Django) + Gunicorn + Nginx        │
└───────────────┬─────────────────────────┘
                │
        ┌───────┴──────┐
        │              │
┌───────▼──────┐  ┌───▼────────┐
│ RDS (Postgr) │  │ S3 (Media) │
└──────────────┘  └────────────┘
```

### 🔧 Variables de Entorno AWS

```bash
# Backend .env (Producción)
DEBUG=False
SECRET_KEY=<random-key>
ALLOWED_HOSTS=api.smartsales365.com

DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/db
REDIS_URL=redis://elasticache-endpoint:6379

AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=smartsales365-media
AWS_S3_REGION_NAME=us-east-1

STRIPE_SECRET_KEY=sk_live_...
```

### 📦 Deployment Manual (Sin Docker)

**Backend (EC2):**

```bash
# 1. SSH a EC2
ssh -i key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# 2. Instalar dependencias
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql-client

# 3. Clonar repo
git clone https://github.com/tu-usuario/smartsales365-backend.git
cd smartsales365-backend

# 4. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configurar .env
cp .env.example .env
nano .env  # Editar variables

# 6. Migraciones
python manage.py migrate
python manage.py collectstatic --noinput

# 7. Gunicorn + Nginx
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

**Frontend (Vercel/Netlify):**

```bash
# Build local
npm run build

# Deploy a Vercel
vercel --prod

# O a Netlify
netlify deploy --prod --dir=dist
```

---

## 11. ROLES DEL EQUIPO

### 👥 División de Trabajo (2 personas)

#### **PERSONA 1: Backend + IA**

**Ciclo 1:** Setup Django, Auth, Productos, Carrito, Pedidos  
**Ciclo 2:** Reportes dinámicos (Parser, QueryBuilder), IA (ML)  
**Ciclo 3:** Deploy backend, Testing, Documentación UML

#### **PERSONA 2: Frontend + Móvil**

**Ciclo 1:** Setup React, Login, Catálogo, Carrito, Checkout  
**Ciclo 2:** Dashboard analítico, Reportes UI, Web Speech API  
**Ciclo 3:** App Flutter completa, Push, Deploy frontend, Video demo

---

## ✅ CHECKLIST FINAL

### **Presentación 1 (28/10):**

- [ ] Backend: Auth, Productos, Carrito
- [ ] Seeders funcionando
- [ ] Swagger completo

### **Presentación 2 (04/11):**

- [ ] Reportes dinámicos (texto/voz)
- [ ] IA funcionando (predicciones)
- [ ] Dashboard analítico

### **Presentación 3 (11/11):**

- [ ] App móvil funcional
- [ ] Deploy completo (AWS)
- [ ] Documentación (UML)
- [ ] Video demo

### **Defensa Final (13/11):**

- [ ] Proyecto 100% funcional
- [ ] Código limpio
- [ ] Presentación preparada

---

## 📚 COMANDOS ÚTILES

### Backend:

```bash
# Activar venv
source venv/bin/activate

# Seeders
python scripts/seed_data.py

# Entrenar modelo IA
python scripts/train_ml_model.py

# Tests
pytest --cov=apps
```

### Frontend:

```bash
# Dev
npm run dev

# Build
npm run build
```

### Git (3 repos):

```bash
# Crear feature
git checkout -b feature/nombre-funcionalidad

# Commit convencional
git commit -m "feat(auth): agregar login con JWT"

# Push
git push origin feature/nombre-funcionalidad
```
