# 📊 Sistema de Reportes Dinámicos con AI - SmartSales365

## 📋 Descripción General

El sistema de reportes de SmartSales365 permite generar reportes personalizados utilizando **lenguaje natural** (texto o voz). Los usuarios pueden solicitar reportes como "Ventas de septiembre en PDF" o "Top 10 productos más vendidos en Excel" y el sistema los genera automáticamente.

### Características Principales

✅ **Generación desde Prompts**: Texto o voz en español
✅ **Múltiples Formatos**: PDF, Excel, CSV
✅ **Parser Inteligente**: Interpreta períodos, filtros, agrupaciones
✅ **Analytics Dashboard**: Estadísticas en tiempo real
✅ **API RESTful**: Endpoints bien documentados
✅ **Generadores Modulares**: Fácil de extender

---

## 🏗️ Arquitectura

### Flujo de Generación de Reportes

```
Usuario → Frontend (Prompt) → API Endpoint
                                    ↓
                            PromptParser
                                    ↓
                            QueryBuilder
                                    ↓
                          Obtener Datos (ORM)
                                    ↓
                      ReportGenerator (PDF/Excel/CSV)
                                    ↓
                      Archivo Descargable
```

### Componentes del Backend

```
apps/reports/
├── generators/          # Generadores de archivos
│   ├── base.py         # Clase base abstracta
│   ├── pdf_generator.py
│   ├── excel_generator.py
│   └── csv_generator.py
├── services/           # Lógica de negocio
│   ├── analytics_service.py      # Métricas y estadísticas
│   ├── prompt_parser.py          # Interpretación de prompts
│   ├── query_builder.py          # Construcción de queries
│   └── report_generator_service.py  # Coordinador principal
├── views.py            # API endpoints (ViewSets)
├── serializers.py      # Validación de requests
├── urls.py             # Rutas de la app
└── README.md           # Este archivo
```

---

## 🚀 Endpoints de la API

### 1. Generar Reporte desde Prompt

**`POST /api/reports/generate/`**

Genera un reporte interpretando un comando en lenguaje natural.

**Request:**
```json
{
  "prompt": "Reporte de ventas de septiembre en PDF"
}
```

**Response:**
- Archivo binario (PDF/Excel/CSV)
- Headers: `Content-Disposition: attachment; filename="..."`

**Ejemplos de Prompts:**
```
"Reporte de ventas del último mes en PDF"
"Top 10 productos más vendidos en Excel"
"Clientes registrados este año en CSV"
"Pedidos pendientes en PDF"
"Ventas agrupadas por producto del último mes en Excel"
```

---

### 2. Generar Reporte Predefinido

**`POST /api/reports/predefined/`**

Genera un reporte sin usar prompts (para programación).

**Request:**
```json
{
  "report_type": "ventas",
  "format": "pdf",
  "filters": {
    "estado": "confirmado"
  }
}
```

**Parámetros:**
- `report_type`: `ventas` | `productos` | `clientes` | `analytics`
- `format`: `pdf` | `excel` | `csv`
- `filters`: Objeto con filtros opcionales

---

### 3. Analytics Overview

**`GET /api/analytics/overview/?months=12&days=30`**

Obtiene resumen analítico completo del sistema.

**Response:**
```json
{
  "sales_by_month": [...],
  "products_by_category": [...],
  "activity_by_day": [...],
  "top_selling_products": [...],
  "sales_by_status": [...],
  "summary": {
    "total_orders": 123,
    "total_sales": 12345.67,
    "total_products": 45,
    "total_customers": 67
  },
  "inventory_summary": {...},
  "customer_analytics": {...}
}
```

---

### 4. Otros Endpoints de Analytics

- **`GET /api/analytics/summary/`** - Resumen general
- **`GET /api/analytics/sales/?months=12`** - Ventas por mes
- **`GET /api/analytics/products/`** - Analytics de productos
- **`GET /api/analytics/inventory/`** - Resumen de inventario
- **`GET /api/analytics/customers/`** - Analytics de clientes

---

## 🧠 Parser de Prompts

El `PromptParser` interpreta comandos en lenguaje natural y extrae:

### Tipos de Reportes Soportados
```python
REPORT_TYPES = {
    'ventas': ['ventas', 'pedidos', 'ordenes'],
    'productos': ['productos', 'prendas', 'inventario', 'stock'],
    'clientes': ['clientes', 'usuarios'],
    'analytics': ['analytics', 'estadísticas', 'resumen'],
}
```

### Períodos de Tiempo
- **Predefinidos**: `hoy`, `ayer`, `esta semana`, `este mes`, `último mes`, `este año`
- **Meses**: `enero`, `febrero`, ..., `diciembre`
- **Relativos**: `últimos 7 días`, `últimas 4 semanas`, `últimos 3 meses`
- **Fechas Específicas**: `01/09/2024`, `2024-09-01`
- **Rangos**: `desde 01/09/2024 hasta 30/09/2024`

### Formatos
- `pdf`, `excel`, `xlsx`, `csv`

### Filtros
- **Estados**: `pendiente`, `confirmado`, `enviado`, `entregado`, `cancelado`
- **Categoría**: `categoría Vestidos`
- **Marca**: `marca Zara`

### Agrupación
- `agrupado por producto`
- `agrupado por categoría`
- `agrupado por cliente`
- `agrupado por mes`

### Límites
- `top 10`
- `primeros 20`

---

## 📁 Generadores de Archivos

### PDF Generator (ReportLab)

```python
from apps.reports.generators import PDFReportGenerator

pdf = PDFReportGenerator(title="Reporte de Ventas")
pdf.add_title("Ventas de Septiembre 2024")
pdf.add_metadata("SmartSales365", "Juan Pérez")
pdf.add_table(data, headers=['Producto', 'Cantidad', 'Total'])
pdf_bytes = pdf.generate()
```

**Características:**
- Tablas con estilos personalizados
- Encabezados y pies de página
- Colores corporativos
- Paginación automática

---

### Excel Generator (openpyxl)

```python
from apps.reports.generators import ExcelReportGenerator

excel = ExcelReportGenerator(title="Reporte de Productos")
sheet = excel.create_sheet("Datos")
excel.add_table(data, headers=['Nombre', 'Precio', 'Stock'])
excel_bytes = excel.generate()
```

**Características:**
- Múltiples hojas
- Formato de celdas
- Anchos de columna automáticos
- Colores alternados en filas

---

### CSV Generator

```python
from apps.reports.generators import CSVReportGenerator

csv = CSVReportGenerator(title="Reporte de Clientes")
csv.add_table(data, headers=['Nombre', 'Email', 'Total Gastado'])
csv_bytes = csv.generate()
```

---

## 🔧 Query Builder

El `QueryBuilder` construye queries dinámicos de Django ORM basados en la configuración parseada.

### Reportes Soportados

#### 1. Ventas/Pedidos
```python
config = {
    'type': 'ventas',
    'period': {'start_date': date(...), 'end_date': date(...)},
    'filters': {'estado': 'confirmado'},
    'group_by': ['producto'],
    'limit': 10
}
```

**Agrupaciones:**
- Por producto
- Por mes
- Por cliente

#### 2. Productos
```python
config = {
    'type': 'productos',
    'filters': {'categoria': 'Vestidos', 'marca': 'Zara'},
    'group_by': ['categoria']
}
```

#### 3. Clientes
```python
config = {
    'type': 'clientes',
    'period': {'start_date': ...},
    'limit': 50
}
```

#### 4. Analytics
```python
config = {
    'type': 'analytics'
}
```

Retorna datos completos de `AnalyticsService`.

---

## 📊 Analytics Service

Proporciona métricas precalculadas del sistema.

### Métodos Disponibles

```python
from apps.reports.services import AnalyticsService

# Ventas por mes
sales = AnalyticsService.get_sales_by_month(months=12)

# Productos por categoría
products = AnalyticsService.get_products_by_category()

# Top productos más vendidos
top = AnalyticsService.get_top_selling_products(limit=10)

# Resumen general
summary = AnalyticsService.get_summary()

# Resumen de inventario
inventory = AnalyticsService.get_inventory_summary()

# Analytics de clientes
customers = AnalyticsService.get_customer_analytics()
```

---

## 🎯 Ejemplos de Uso

### Desde el Frontend (React/TypeScript)

```typescript
import { reportsService } from '@/modules/reports/services/reports.service';

// Generar reporte desde prompt
const handleGenerate = async (prompt: string) => {
  try {
    const blob = await reportsService.generateFromPrompt(prompt);
    const filename = reportsService.generateFilename(prompt, 'pdf');
    reportsService.downloadBlob(blob, filename);
  } catch (error) {
    console.error('Error:', error);
  }
};

// Usar desde un componente
<ReportPromptInput
  onSubmit={(prompt, format) => handleGenerate(prompt)}
  isLoading={isLoading}
/>
```

### Desde Python (Backend)

```python
from apps.reports.services import ReportGeneratorService

# Generar desde prompt
file_content, filename, mime_type = ReportGeneratorService.generate_from_prompt(
    prompt="Ventas del último mes en PDF",
    user_name="Juan Pérez",
    organization_name="SmartSales365"
)

# Generar reporte predefinido
file_content, filename, mime_type = ReportGeneratorService.generate_predefined_report(
    report_type='ventas',
    format_type='excel',
    filters={'estado': 'confirmado'},
    user_name="Juan Pérez"
)
```

---

## 🧪 Testing

### Probar Endpoints con cURL

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@smartsales365.com","password":"Admin2024!"}'

# Copiar el token de access

# 2. Generar reporte
curl -X POST http://localhost:8000/api/reports/generate/ \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Reporte de ventas del último mes en PDF"}' \
  --output reporte.pdf

# 3. Obtener analytics
curl -X GET "http://localhost:8000/api/analytics/overview/?months=6" \
  -H "Authorization: Bearer {TOKEN}"
```

---

## 📝 Notas de Implementación

### Dependencias Requeridas

```txt
# Ya incluidas en requirements.txt
reportlab==4.0.7      # PDF generation
openpyxl==3.1.2       # Excel generation
```

### Configuración

No requiere configuración adicional. La app se registra automáticamente en `settings/base.py`:

```python
LOCAL_APPS = [
    ...
    'apps.reports',
]
```

### Permisos

Todos los endpoints requieren autenticación (`IsAuthenticated`). Los usuarios deben tener un token JWT válido.

---

## 🔮 Futuras Mejoras

- [ ] **Reportes Programados**: Envío automático por email
- [ ] **Caché de Reportes**: Guardar reportes generados
- [ ] **Más Visualizaciones**: Gráficos en PDF
- [ ] **Exportar Gráficos**: Imágenes PNG/JPG
- [ ] **Webhooks**: Notificaciones cuando reporte esté listo
- [ ] **Plantillas Personalizadas**: Templates de reportes

---

## 👥 Soporte

Para dudas o problemas, contacta al equipo de desarrollo.

---

**Implementado por:** Claude Code Assistant
**Fecha:** Noviembre 2024
**Versión:** 1.0.0
