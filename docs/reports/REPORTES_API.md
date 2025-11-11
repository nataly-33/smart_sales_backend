# API de Reportes Dinámicos - SmartSales365

## Base URL

```
Local: http://localhost:8000/api
Producción: https://api.smartsales365.com/api
```

## Autenticación

Todos los endpoints requieren autenticación JWT.

```http
Authorization: Bearer <access_token>
```

Para obtener tokens:

```http
POST /api/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Respuesta:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Endpoints

### 1. Generar Reporte desde Prompt

Genera un reporte completo a partir de un comando en lenguaje natural.

**Endpoint:**

```
POST /api/reports/generate/
```

**Headers:**

```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**

```json
{
  "prompt": "Ventas del año 2025 en Excel"
}
```

**Response:**

- **Success:** `200 OK` - Archivo binario (PDF/Excel/CSV)
- **Headers:**
  ```http
  Content-Type: application/pdf | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | text/csv
  Content-Disposition: attachment; filename="reporte_ventas_2025_2025-11-10.xlsx"
  ```

**Errors:**

- `400 Bad Request` - Prompt inválido o no se pudo interpretar
  ```json
  {
    "error": "No se pudo identificar el tipo de reporte. Tipos válidos: ['ventas', 'productos', 'clientes', 'analytics']"
  }
  ```
- `401 Unauthorized` - Token inválido o expirado
- `500 Internal Server Error` - Error al generar el reporte

**Ejemplo curl:**

```bash
curl -X POST "http://localhost:8000/api/reports/generate/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ventas del año 2025 en Excel"}' \
  --output reporte.xlsx
```

---

### 2. Preview de Reporte

Valida el prompt y devuelve una muestra de máximo 20 filas sin generar el archivo completo.

**Endpoint:**

```
POST /api/reports/preview/
```

**Headers:**

```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**

```json
{
  "prompt": "Top 10 productos más vendidos"
}
```

**Response:**

```json
{
  "data": [
    {
      "producto": "Vestido Floral",
      "precio_unitario": 299.99,
      "cantidad_vendida": 45,
      "total_ingresos": 13499.55
    },
    ...
  ],
  "metadata": {
    "total_records": 10,
    "period": "Todo el tiempo",
    "limit": 10
  },
  "total_rows": 10,
  "config": {
    "type": "top_productos",
    "format": "pdf",
    "period": null,
    "filters": {},
    "group_by": [],
    "limit": 10
  },
  "message": "Preview generado. Los datos reales pueden ser más extensos."
}
```

**Errors:**

- `400 Bad Request` - Prompt inválido
- `401 Unauthorized` - No autenticado

**Ejemplo curl:**

```bash
curl -X POST "http://localhost:8000/api/reports/preview/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ventas del último mes"}'
```

---

### 3. Generar Reporte Predefinido

Genera un reporte usando un tipo predefinido sin necesidad de parsear lenguaje natural.

**Endpoint:**

```
POST /api/reports/predefined/
```

**Headers:**

```http
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**

```json
{
  "report_type": "ventas",
  "format": "excel",
  "filters": {
    "estado": "confirmado"
  }
}
```

**Parámetros:**

- `report_type` (string, requerido): `"ventas"`, `"productos"`, `"clientes"`, `"analytics"`
- `format` (string, opcional): `"pdf"`, `"excel"`, `"csv"` (default: `"pdf"`)
- `filters` (object, opcional): Filtros adicionales específicos del reporte

**Response:**

- **Success:** `200 OK` - Archivo binario

**Ejemplo curl:**

```bash
curl -X POST "http://localhost:8000/api/reports/predefined/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"report_type": "ventas", "format": "excel"}' \
  --output reporte.xlsx
```

---

### 4. Obtener Plantillas de Reportes

Lista todas las plantillas de reportes predefinidos disponibles con ejemplos de prompts.

**Endpoint:**

```
GET /api/reports/templates/
```

**Headers:**

```http
Authorization: Bearer <token>
```

**Response:**

```json
[
  {
    "id": "ventas_mes_actual",
    "name": "Ventas del mes actual",
    "description": "Listado completo de todas las ventas del mes en curso",
    "prompt_example": "Ventas del mes actual en PDF",
    "category": "ventas"
  },
  {
    "id": "ventas_2025",
    "name": "Ventas del año 2025",
    "description": "Todas las ventas realizadas en el año 2025",
    "prompt_example": "Ventas del año 2025 en Excel",
    "category": "ventas"
  },
  ...
]
```

**Ejemplo curl:**

```bash
curl -X GET "http://localhost:8000/api/reports/templates/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 5. Analytics Overview

Obtiene un resumen completo de analytics y estadísticas del sistema.

**Endpoint:**

```
GET /api/analytics/overview/
```

**Headers:**

```http
Authorization: Bearer <token>
```

**Query Parameters:**

- `months` (integer, opcional): Número de meses históricos (default: 12, max: 24)
- `days` (integer, opcional): Número de días para actividad reciente (default: 30, max: 90)

**Response:**

```json
{
  "sales_by_month": [
    {
      "month": "Nov 2024",
      "total_sales": 45678.90,
      "order_count": 123
    },
    ...
  ],
  "products_by_category": [
    {
      "category": "Vestidos",
      "product_count": 45
    },
    ...
  ],
  "activity_by_day": [...],
  "top_selling_products": [
    {
      "product_name": "Vestido Floral",
      "quantity_sold": 45,
      "total_revenue": 13499.55,
      "price": 299.99
    },
    ...
  ],
  "summary": {
    "total_orders": 1234,
    "orders_this_month": 78,
    "total_sales": 567890.12,
    "sales_this_month": 34567.89,
    "total_products": 234,
    "total_customers": 456,
    "customers_this_month": 23
  },
  "inventory_summary": {
    "total_products": 234,
    "total_stock": 4567,
    "low_stock_items": 12,
    "out_of_stock_items": 3
  },
  "customer_analytics": {
    "total_customers": 456,
    "customers_with_orders": 234,
    "average_order_value": 456.78
  }
}
```

**Ejemplo curl:**

```bash
curl -X GET "http://localhost:8000/api/analytics/overview/?months=6&days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 6. Resumen General

Obtiene métricas generales del sistema.

**Endpoint:**

```
GET /api/analytics/summary/
```

**Response:**

```json
{
  "total_orders": 1234,
  "orders_this_month": 78,
  "total_sales": 567890.12,
  "sales_this_month": 34567.89,
  "average_order_value": 460.26,
  "total_products": 234,
  "total_customers": 456,
  "customers_this_month": 23
}
```

---

### 7. Ventas por Mes

Obtiene datos de ventas agrupados por mes.

**Endpoint:**

```
GET /api/analytics/sales/
```

**Query Parameters:**

- `months` (integer, opcional): Número de meses (default: 12)

**Response:**

```json
[
  {
    "month": "Nov 2024",
    "total_sales": 45678.90,
    "order_count": 123
  },
  {
    "month": "Oct 2024",
    "total_sales": 38456.50,
    "order_count": 98
  },
  ...
]
```

---

### 8. Analytics de Productos

Obtiene estadísticas de productos.

**Endpoint:**

```
GET /api/analytics/products/
```

**Response:**

```json
{
  "by_category": [
    {
      "category": "Vestidos",
      "product_count": 45
    },
    {
      "category": "Pantalones",
      "product_count": 32
    },
    ...
  ],
  "top_selling": [
    {
      "product_name": "Vestido Floral",
      "quantity_sold": 45,
      "total_revenue": 13499.55,
      "price": 299.99
    },
    ...
  ]
}
```

---

### 9. Resumen de Inventario

Obtiene estadísticas de inventario.

**Endpoint:**

```
GET /api/analytics/inventory/
```

**Response:**

```json
{
  "total_products": 234,
  "total_stock": 4567,
  "low_stock_items": 12,
  "out_of_stock_items": 3,
  "average_stock_per_product": 19.5
}
```

---

### 10. Analytics de Clientes

Obtiene estadísticas de clientes.

**Endpoint:**

```
GET /api/analytics/customers/
```

**Response:**

```json
{
  "total_customers": 456,
  "customers_with_orders": 234,
  "average_order_value": 456.78,
  "repeat_customer_rate": 0.65,
  "new_customers_this_month": 23
}
```

---

## Lista Blanca de Reportes

El sistema solo genera reportes sobre los siguientes tipos (protección contra SQL injection):

| ID              | Nombre         | Descripción             | Keywords                                                |
| --------------- | -------------- | ----------------------- | ------------------------------------------------------- |
| `ventas`        | Ventas/Pedidos | Órdenes de compra       | ventas, venta, pedidos, pedido, ordenes, orden, compras |
| `productos`     | Productos      | Inventario y productos  | productos, producto, prendas, prenda, inventario, stock |
| `clientes`      | Clientes       | Información de clientes | clientes, cliente, usuarios, usuario, compradores       |
| `analytics`     | Analytics      | Métricas generales      | analytics, estadísticas, resumen, dashboard, métricas   |
| `logins`        | Logins         | Auditoría de accesos    | logins, inicios de sesión, sesiones, accesos            |
| `carritos`      | Carritos       | Carritos activos        | carritos, carritos activos, carros de compra            |
| `top_productos` | Top Productos  | Productos más vendidos  | top productos, productos más vendidos, más vendidos     |
| `ingresos`      | Ingresos       | Facturación             | ingresos, ganancias, facturación, revenue               |

---

## Ejemplos de Prompts Válidos (20+ ejemplos)

### Ventas

1. "Ventas del año 2025 en Excel"
2. "Ventas del último mes en PDF"
3. "Reporte de ventas de septiembre en CSV"
4. "Ventas del año 2025 agrupadas por producto en Excel"
5. "Ventas agrupadas por cliente del último trimestre en PDF"
6. "Pedidos pendientes en Excel"
7. "Pedidos confirmados del mes actual en PDF"
8. "Ventas de los últimos 30 días en CSV"

### Productos

9. "Top 10 productos más vendidos en PDF"
10. "Top 5 productos más vendidos del año 2025 en Excel"
11. "Inventario completo en Excel"
12. "Productos con stock bajo en CSV"
13. "Productos agrupados por categoría en PDF"
14. "Reporte de productos activos en Excel"

### Clientes

15. "Clientes registrados en el año 2025 en Excel"
16. "Clientes del último mes en CSV"
17. "Top 10 clientes con más compras en PDF"
18. "Clientes registrados este año en Excel"
19. "Nuevos clientes del trimestre en CSV"

### Analytics y Métricas

20. "Reporte de analytics completo en PDF"
21. "Logins de los últimos 7 días en Excel"
22. "Logins de hoy en CSV"
23. "Logins de los últimos 30 días en Excel"
24. "Carritos activos con items en PDF"
25. "Ingresos por día del mes actual en Excel"
26. "Ingresos del año 2025 en Excel"
27. "Resumen del mes actual en PDF"

---

## Códigos de Error

| Código | Mensaje                        | Descripción                      | Solución                                      |
| ------ | ------------------------------ | -------------------------------- | --------------------------------------------- |
| 400    | `Prompt inválido`              | No se pudo interpretar el prompt | Revisar sintaxis del prompt o usar plantillas |
| 400    | `Tipo de reporte no soportado` | El tipo solicitado no existe     | Consultar lista blanca de reportes            |
| 400    | `Formato no soportado`         | Formato inválido                 | Usar: pdf, excel, o csv                       |
| 401    | `Unauthorized`                 | Token inválido o ausente         | Autenticarse y enviar token válido            |
| 403    | `Forbidden`                    | Sin permisos para este reporte   | Verificar rol del usuario                     |
| 404    | `Not Found`                    | Endpoint no existe               | Verificar URL                                 |
| 429    | `Too Many Requests`            | Límite de rate excedido          | Esperar antes de reintentar                   |
| 500    | `Internal Server Error`        | Error en el servidor             | Reportar al soporte                           |

---

## Rate Limiting

| Usuario     | Límite               |
| ----------- | -------------------- |
| Anónimo     | 10 requests/hora     |
| Autenticado | 100 requests/hora    |
| Reportes    | 20 generaciones/hora |

---

## Límites y Restricciones

- **Máximo de filas por reporte:** 10,000
- **Timeout por reporte:** 120 segundos
- **Preview:** máximo 20 filas
- **Tamaño máximo de archivo:** 50 MB
- **Formatos soportados:** PDF, Excel (.xlsx), CSV

---

## Versionamiento

Esta es la API **v1**. Futuros cambios breaking incluirán versionamiento en la URL:

```
/api/v2/reports/generate/
```

---

## Soporte

- **Documentación general:** `/docs/REPORTES_README.md`
- **Consultas SQL:** `/docs/REPORTES_CONSULTAS.md`
- **GitHub Issues:** [tu-repo]/issues
- **Email:** support@smartsales365.com

---

## Changelog

### v1.0.0 (2025-11-10)

- ✨ Sistema inicial de reportes dinámicos
- ✨ Soporte para lenguaje natural (texto y voz)
- ✨ 8 tipos de reportes
- ✨ Formatos: PDF, Excel, CSV
- ✨ Analytics dashboard completo
- ✨ Auditoría de logins
- ✨ 20+ plantillas de reportes
