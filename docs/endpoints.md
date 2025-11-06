# 🔌 Endpoints API - SmartSales365 Backend

**Base URL**: `http://localhost:8000/api/`
**Documentación interactiva**: http://localhost:8000/api/docs/

---

## 📋 Índice de Módulos

1. [Autenticación](#autenticación) - 6 endpoints
2. [Productos](#productos) - 12 endpoints
3. [Clientes](#clientes) - 8 endpoints
4. [Carrito](#carrito) - 5 endpoints
5. [Pedidos](#pedidos) - 7 endpoints
6. [Reportes](#reportes) - 4 endpoints (Pendiente)
7. [IA Predictiva](#ia-predictiva) - 3 endpoints (Pendiente)

**Total**: 41 endpoints activos + 7 pendientes

---

## 🔐 Autenticación

### 1. Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "usuario@mail.com",
    "password": "password123"
}
```

**Response 200**:
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "uuid",
        "email": "usuario@mail.com",
        "nombre": "Juan",
        "apellido": "Pérez",
        "nombre_completo": "Juan Pérez",
        "rol_detalle": {
            "nombre": "Cliente",
            "permisos": [
                { "codigo": "productos.leer", "nombre": "Leer productos" }
            ]
        }
    }
}
```

**Permisos**: Público

---

### 2. Registro
```http
POST /api/auth/register/register/
Content-Type: application/json

{
    "email": "nuevo@mail.com",
    "password": "password123",
    "nombre": "María",
    "apellido": "García",
    "telefono": "+59175123456"
}
```

**Response 201**: Usuario creado con rol "Cliente"

**Permisos**: Público

---

### 3. Refresh Token
```http
POST /api/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200**:
```json
{
    "access": "nuevo_access_token..."
}
```

**Permisos**: Público

---

### 4. Usuario Actual
```http
GET /api/auth/users/me/
Authorization: Bearer {access_token}
```

**Response 200**: Datos completos del usuario autenticado

**Permisos**: Autenticado

---

### 5. Listar Usuarios (Admin)
```http
GET /api/auth/users/
Authorization: Bearer {admin_token}
```

**Query params**:
- `?search=juan` - Buscar por nombre/email
- `?rol=Cliente` - Filtrar por rol
- `?is_active=true` - Filtrar activos

**Permisos**: Admin

---

### 6. Crear Usuario (Admin)
```http
POST /api/auth/users/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
    "email": "empleado@tienda.com",
    "password": "password123",
    "nombre": "Carlos",
    "apellido": "López",
    "rol_id": "uuid-del-rol-empleado"
}
```

**Permisos**: Admin (`usuarios.crear`)

---

## 🛍️ Productos

### 7. Listar Productos
```http
GET /api/products/prendas/
```

**Query params**:
- `?search=vestido` - Buscar en nombre/descripción
- `?categoria=uuid` - Filtrar por categoría
- `?marca=uuid` - Filtrar por marca
- `?precio_min=100` - Precio mínimo
- `?precio_max=500` - Precio máximo
- `?activa=true` - Solo activas
- `?destacada=true` - Solo destacadas
- `?es_novedad=true` - Solo novedades

**Response 200**:
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/products/prendas/?page=2",
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "nombre": "Vestido Floral Rosa",
            "slug": "vestido-floral-rosa",
            "descripcion": "Hermoso vestido...",
            "precio": "350.00",
            "marca": {
                "id": "uuid",
                "nombre": "Zara"
            },
            "categorias": [
                { "id": "uuid", "nombre": "Vestidos" }
            ],
            "color": "Rosa",
            "material": "Algodón",
            "imagen_principal": {
                "imagen": "http://s3.../vestido.jpg",
                "es_principal": true
            },
            "stock_total": 45,
            "activa": true,
            "destacada": true,
            "es_novedad": false
        }
    ]
}
```

**Permisos**: Público

---

### 8. Detalle de Producto
```http
GET /api/products/prendas/{slug}/
```

**Response 200**: Producto completo con:
- Todas las imágenes
- Stock por talla
- Categorías
- Marca completa

**Permisos**: Público

---

### 9. Crear Producto (Admin)
```http
POST /api/products/prendas/
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

{
    "nombre": "Blusa Elegante",
    "descripcion": "...",
    "precio": 250.00,
    "marca_id": "uuid",
    "categoria_ids": ["uuid1", "uuid2"],
    "talla_ids": ["uuid-S", "uuid-M", "uuid-L"],
    "color": "Blanco",
    "material": "Seda",
    "imagen": (archivo)
}
```

**Permisos**: Admin (`productos.crear`)

---

### 10. Actualizar Producto
```http
PATCH /api/products/prendas/{id}/
Authorization: Bearer {admin_token}

{
    "precio": 300.00,
    "destacada": true
}
```

**Permisos**: Admin (`productos.actualizar`)

---

### 11. Eliminar Producto (Soft Delete)
```http
DELETE /api/products/prendas/{id}/
Authorization: Bearer {admin_token}
```

**Permisos**: Admin (`productos.eliminar`)

---

### 12. Listar Categorías
```http
GET /api/products/categorias/
```

**Permisos**: Público

---

### 13. Crear Categoría
```http
POST /api/products/categorias/
Authorization: Bearer {admin_token}

{
    "nombre": "Accesorios",
    "descripcion": "...",
    "imagen": (archivo)
}
```

**Permisos**: Admin

---

### 14-18. Marcas y Tallas
Similar a categorías (CRUD completo).

---

## 👤 Clientes

### 19. Perfil del Cliente
```http
GET /api/customers/profile/
Authorization: Bearer {token}
```

**Response 200**:
```json
{
    "usuario": {
        "id": "uuid",
        "email": "cliente@mail.com",
        "nombre_completo": "Juan Pérez"
    },
    "telefono": "+59175123456",
    "foto_perfil": "http://...",
    "direcciones": [
        {
            "id": "uuid",
            "direccion_completa": "Av. Principal 123, La Paz, Bolivia",
            "es_principal": true
        }
    ],
    "favoritos_count": 5
}
```

**Permisos**: Autenticado

---

### 20. Actualizar Perfil
```http
PATCH /api/customers/profile/
Authorization: Bearer {token}

{
    "telefono": "+59176000000",
    "foto_perfil": (archivo)
}
```

**Permisos**: Autenticado

---

### 21. Listar Direcciones
```http
GET /api/customers/addresses/
Authorization: Bearer {token}
```

**Permisos**: Autenticado

---

### 22. Crear Dirección
```http
POST /api/customers/addresses/
Authorization: Bearer {token}

{
    "calle": "Av. Simón Bolívar",
    "numero_exterior": "456",
    "ciudad": "Santa Cruz",
    "estado": "Santa Cruz",
    "codigo_postal": "00000",
    "es_principal": true
}
```

**Permisos**: Autenticado

---

### 23-26. Favoritos (CRUD)
```http
GET /api/customers/favorites/
POST /api/customers/favorites/
DELETE /api/customers/favorites/{id}/
```

**Permisos**: Autenticado

---

## 🛒 Carrito

### 27. Obtener Carrito
```http
GET /api/cart/
Authorization: Bearer {token}
```

**Response 200**:
```json
{
    "id": "uuid",
    "usuario": {
        "id": "uuid",
        "nombre_completo": "Juan Pérez"
    },
    "items": [
        {
            "id": "uuid",
            "prenda": {
                "id": "uuid",
                "nombre": "Vestido Floral",
                "imagen_principal": "http://..."
            },
            "talla": {
                "id": "uuid",
                "nombre": "M"
            },
            "cantidad": 2,
            "precio_unitario": "350.00",
            "subtotal": "700.00"
        }
    ],
    "total_items": 2,
    "subtotal": "700.00",
    "total": "700.00"
}
```

**Permisos**: Autenticado

---

### 28. Agregar al Carrito
```http
POST /api/cart/add/
Authorization: Bearer {token}

{
    "prenda_id": "uuid",
    "talla_id": "uuid",
    "cantidad": 1
}
```

**Response 201**: Item agregado (o cantidad actualizada si ya existía)

**Permisos**: Autenticado

---

### 29. Actualizar Cantidad
```http
PATCH /api/cart/{item_id}/update-item/
Authorization: Bearer {token}

{
    "cantidad": 3
}
```

**Permisos**: Autenticado

---

### 30. Eliminar Item
```http
DELETE /api/cart/{item_id}/remove/
Authorization: Bearer {token}
```

**Permisos**: Autenticado

---

### 31. Vaciar Carrito
```http
POST /api/cart/clear/
Authorization: Bearer {token}
```

**Permisos**: Autenticado

---

## 📦 Pedidos

### 32. Listar Pedidos
```http
GET /api/orders/pedidos/
Authorization: Bearer {token}
```

**Query params (Admin)**:
- `?estado=pendiente` - Filtrar por estado
- `?usuario=uuid` - Filtrar por usuario
- `?fecha_desde=2025-01-01` - Desde fecha
- `?fecha_hasta=2025-12-31` - Hasta fecha

**Response**:
- Cliente: Solo sus pedidos
- Admin: Todos los pedidos

**Permisos**: Autenticado

---

### 33. Crear Pedido (Checkout)
```http
POST /api/orders/pedidos/
Authorization: Bearer {token}

{
    "direccion_envio_id": "uuid",
    "metodo_pago_id": "uuid",
    "notas": "Entrega en la mañana"
}
```

**Flujo**:
1. Valida stock de items del carrito
2. Crea pedido con snapshot de dirección
3. Crea detalles con snapshot de productos
4. Reduce stock
5. Crea pago pendiente
6. Si es PayPal, crea orden externa
7. Vacía carrito

**Response 201**:
```json
{
    "id": "uuid",
    "numero_pedido": "ORD-20251106143025-1234",
    "estado": "pendiente",
    "total": "700.00",
    "detalles": [...],
    "pagos": [...]
}
```

**Permisos**: Autenticado

---

### 34. Detalle de Pedido
```http
GET /api/orders/pedidos/{id}/
Authorization: Bearer {token}
```

**Permisos**: Propietario o Admin

---

### 35. Actualizar Estado (Admin)
```http
PATCH /api/orders/pedidos/{id}/
Authorization: Bearer {admin_token}

{
    "estado": "enviado"
}
```

**Permisos**: Admin/Empleado

---

### 36. Cancelar Pedido
```http
POST /api/orders/pedidos/{id}/cancel/
Authorization: Bearer {token}
```

**Restricciones**:
- Solo si estado es: `pendiente`, `pago_recibido` o `confirmado`
- Cliente: Solo sus pedidos
- Admin: Cualquier pedido

**Permisos**: Propietario o Admin

---

### 37. Métodos de Pago
```http
GET /api/orders/metodos-pago/
```

**Response 200**:
```json
[
    {
        "id": "uuid",
        "nombre": "Efectivo",
        "codigo": "efectivo",
        "requiere_procesador": false,
        "activo": true
    },
    {
        "id": "uuid",
        "nombre": "PayPal",
        "codigo": "paypal",
        "requiere_procesador": true,
        "activo": true
    }
]
```

**Permisos**: Público

---

### 38. Crear Orden PayPal
```http
POST /api/orders/paypal/create-order/
Authorization: Bearer {token}

{
    "pedido_id": "uuid"
}
```

**Response 200**:
```json
{
    "paypal_order_id": "6H576345YT123456A",
    "approval_url": "https://www.paypal.com/checkoutnow?token=..."
}
```

**Permisos**: Autenticado

---

## 📊 Reportes (PENDIENTE)

### 39. Generar Reporte Dinámico
```http
POST /api/reports/generate/
Authorization: Bearer {token}
Content-Type: application/json

{
    "prompt": "Quiero un reporte de ventas de septiembre agrupado por producto en PDF"
}
```

**ó con voz**:
```json
{
    "voice_text": "Quiero un reporte en Excel de las ventas del 1 al 30 de octubre"
}
```

**Response 200**:
```json
{
    "report_id": "uuid",
    "tipo": "ventas",
    "formato": "pdf",
    "url_descarga": "http://.../reports/uuid.pdf"
}
```

**Permisos**: Admin/Empleado (`reportes.generar`)

---

### 40-41. Listar/Descargar Reportes Generados
```http
GET /api/reports/
GET /api/reports/{id}/download/
```

**Permisos**: Admin/Empleado

---

## 🤖 IA Predictiva (PENDIENTE)

### 42. Predicción de Ventas
```http
GET /api/ai/predictions/sales-forecast/
Authorization: Bearer {admin_token}

Query params:
?mes=11
&año=2025
&categoria=uuid
```

**Response 200**:
```json
{
    "mes": 11,
    "año": 2025,
    "categoria": "Vestidos",
    "ventas_predichas": 125.5,
    "confianza": 0.85,
    "datos_historicos": [...]
}
```

**Permisos**: Admin (`reportes.ver_predicciones`)

---

### 43. Dashboard de IA
```http
GET /api/ai/dashboard/
Authorization: Bearer {admin_token}
```

**Response**: Datos completos para dashboard (ventas históricas + predicciones + gráficos)

**Permisos**: Admin

---

### 44. Entrenar Modelo
```http
POST /api/ai/train-model/
Authorization: Bearer {admin_token}
```

**Response 200**:
```json
{
    "status": "success",
    "model_version": "v1.2",
    "accuracy": 0.92,
    "trained_at": "2025-11-06T14:30:00Z"
}
```

**Permisos**: Admin

---

## 📝 Notas Importantes

### Autenticación
Todos los endpoints (excepto públicos) requieren header:
```http
Authorization: Bearer {access_token}
```

### Paginación
Endpoints de listado retornan:
```json
{
    "count": 100,
    "next": "http://.../page=2",
    "previous": null,
    "results": [...]
}
```

### Soft Delete
Los recursos eliminados tienen `is_deleted=True` pero NO se eliminan de la DB.

### Permisos
Ver `documentation_guide.md` para lista completa de permisos.

---

**Última actualización**: 6 de Noviembre 2025
