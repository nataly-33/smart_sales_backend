# Consultas de Reportes - SmartSales365

Este documento detalla las consultas Django ORM utilizadas para generar cada tipo de reporte.

---

## Tabla de Contenidos

1. [Reportes de Ventas](#1-reportes-de-ventas)
2. [Reportes de Productos](#2-reportes-de-productos)
3. [Reportes de Clientes](#3-reportes-de-clientes)
4. [Reportes de Analytics](#4-reportes-de-analytics)
5. [Reportes de Logins](#5-reportes-de-logins)
6. [Reportes de Carritos](#6-reportes-de-carritos)
7. [Reportes de Top Productos](#7-reportes-de-top-productos)
8. [Reportes de Ingresos](#8-reportes-de-ingresos)

---

## 1. Reportes de Ventas

### 1.1 Ventas por Período (Lista Simple)

**Prompt:** "Ventas del año 2025 en Excel"

**ORM Query:**

```python
from apps.orders.models import Pedido
from datetime import datetime

# Filtrar por período
start_date = datetime(2025, 1, 1).date()
end_date = datetime(2025, 12, 31).date()

queryset = Pedido.objects.filter(
    created_at__date__gte=start_date,
    created_at__date__lte=end_date
).select_related('usuario').order_by('-created_at')

# Datos devueltos
data = [{
    'numero_pedido': pedido.numero_pedido,
    'fecha': pedido.created_at.strftime('%d/%m/%Y %H:%M'),
    'cliente': pedido.usuario.nombre_completo,
    'estado': pedido.estado,
    'total': float(pedido.total),
    'items': pedido.detalles.count()
} for pedido in queryset]
```

**SQL Equivalente:**

```sql
SELECT
    p.numero_pedido,
    p.created_at,
    CONCAT(u.nombre, ' ', u.apellido) as cliente,
    p.estado,
    p.total,
    (SELECT COUNT(*) FROM detalle_pedido WHERE pedido_id = p.id) as items
FROM pedido p
INNER JOIN usuario u ON p.usuario_id = u.id
WHERE DATE(p.created_at) >= '2025-01-01'
  AND DATE(p.created_at) <= '2025-12-31'
ORDER BY p.created_at DESC;
```

---

### 1.2 Ventas Agrupadas por Producto

**Prompt:** "Ventas del último mes agrupadas por producto en PDF"

**ORM Query:**

```python
from apps.orders.models import DetallePedido
from django.db.models import Sum, F
from datetime import datetime, timedelta

# Período
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

# Query agrupado
detalles_qs = DetallePedido.objects.filter(
    pedido__created_at__date__gte=start_date,
    pedido__created_at__date__lte=end_date
).values(
    'prenda__nombre',
    'prenda__precio'
).annotate(
    cantidad_total=Sum('cantidad'),
    total_ventas=Sum(F('cantidad') * F('precio_unitario'))
).order_by('-cantidad_total')

# Datos
data = [{
    'producto': item['prenda__nombre'],
    'precio': float(item['prenda__precio']),
    'cantidad_vendida': item['cantidad_total'],
    'total_ventas': float(item['total_ventas'])
} for item in detalles_qs]
```

**SQL Equivalente:**

```sql
SELECT
    pr.nombre as producto,
    pr.precio,
    SUM(dp.cantidad) as cantidad_vendida,
    SUM(dp.cantidad * dp.precio_unitario) as total_ventas
FROM detalle_pedido dp
INNER JOIN prenda pr ON dp.prenda_id = pr.id
INNER JOIN pedido p ON dp.pedido_id = p.id
WHERE DATE(p.created_at) >= CURRENT_DATE - INTERVAL '30 days'
  AND DATE(p.created_at) <= CURRENT_DATE
GROUP BY pr.nombre, pr.precio
ORDER BY cantidad_vendida DESC;
```

---

### 1.3 Ventas Agrupadas por Cliente

**Prompt:** "Ventas agrupadas por cliente del año 2025 en Excel"

**ORM Query:**

```python
from apps.orders.models import Pedido
from django.db.models import Count, Sum

# Query agrupado
ventas_por_cliente = Pedido.objects.filter(
    created_at__year=2025
).values(
    'usuario__nombre',
    'usuario__apellido',
    'usuario__email'
).annotate(
    cantidad_pedidos=Count('id'),
    total_gastado=Sum('total')
).order_by('-total_gastado')

# Datos
data = [{
    'cliente': f"{item['usuario__nombre']} {item['usuario__apellido']}",
    'email': item['usuario__email'],
    'cantidad_pedidos': item['cantidad_pedidos'],
    'total_gastado': float(item['total_gastado'] or 0)
} for item in ventas_por_cliente]
```

**SQL Equivalente:**

```sql
SELECT
    CONCAT(u.nombre, ' ', u.apellido) as cliente,
    u.email,
    COUNT(p.id) as cantidad_pedidos,
    SUM(p.total) as total_gastado
FROM pedido p
INNER JOIN usuario u ON p.usuario_id = u.id
WHERE EXTRACT(YEAR FROM p.created_at) = 2025
GROUP BY u.nombre, u.apellido, u.email
ORDER BY total_gastado DESC;
```

---

### 1.4 Ventas Agrupadas por Mes

**Prompt:** "Ventas agrupadas por mes del año 2025"

**ORM Query:**

```python
from apps.orders.models import Pedido
from django.db.models import Count, Sum

# Query con extra para extraer mes/año
ventas_por_mes = Pedido.objects.filter(
    created_at__year=2025
).extra({
    'mes': "EXTRACT(month FROM created_at)",
    'anio': "EXTRACT(year FROM created_at)"
}).values('mes', 'anio').annotate(
    cantidad_pedidos=Count('id'),
    total_ventas=Sum('total')
).order_by('anio', 'mes')

# Datos
data = [{
    'mes': int(item['mes']),
    'anio': int(item['anio']),
    'cantidad_pedidos': item['cantidad_pedidos'],
    'total_ventas': float(item['total_ventas'] or 0)
} for item in ventas_por_mes]
```

**SQL Equivalente:**

```sql
SELECT
    EXTRACT(MONTH FROM created_at) as mes,
    EXTRACT(YEAR FROM created_at) as anio,
    COUNT(id) as cantidad_pedidos,
    SUM(total) as total_ventas
FROM pedido
WHERE EXTRACT(YEAR FROM created_at) = 2025
GROUP BY mes, anio
ORDER BY anio, mes;
```

---

## 2. Reportes de Productos

### 2.1 Inventario Completo

**Prompt:** "Inventario completo en Excel"

**ORM Query:**

```python
from apps.products.models import Prenda
from django.db.models import Sum

queryset = Prenda.objects.filter(activa=True).annotate(
    stock_total=Sum('stocks__cantidad')
).select_related('marca').prefetch_related('categorias')

data = [{
    'nombre': prenda.nombre,
    'marca': prenda.marca.nombre,
    'precio': float(prenda.precio),
    'stock_total': prenda.stock_total or 0,
    'categorias': ', '.join([cat.nombre for cat in prenda.categorias.all()]),
    'activa': prenda.activa
} for prenda in queryset]
```

**SQL Equivalente:**

```sql
SELECT
    pr.nombre,
    m.nombre as marca,
    pr.precio,
    COALESCE(SUM(sp.cantidad), 0) as stock_total,
    pr.activa
FROM prenda pr
INNER JOIN marca m ON pr.marca_id = m.id
LEFT JOIN stock_prenda sp ON sp.prenda_id = pr.id
WHERE pr.activa = true
GROUP BY pr.id, pr.nombre, m.nombre, pr.precio, pr.activa;
```

---

### 2.2 Productos Agrupados por Categoría

**Prompt:** "Productos agrupados por categoría en PDF"

**ORM Query:**

```python
from apps.products.models import Categoria
from django.db.models import Count, Q

categorias = Categoria.objects.filter(activa=True).annotate(
    cantidad_productos=Count('prendas', filter=Q(prendas__activa=True))
).order_by('-cantidad_productos')

data = [{
    'categoria': cat.nombre,
    'cantidad_productos': cat.cantidad_productos
} for cat in categorias]
```

**SQL Equivalente:**

```sql
SELECT
    c.nombre as categoria,
    COUNT(CASE WHEN pr.activa = true THEN 1 END) as cantidad_productos
FROM categoria c
LEFT JOIN prenda_categorias pc ON pc.categoria_id = c.id
LEFT JOIN prenda pr ON pr.id = pc.prenda_id
WHERE c.activa = true
GROUP BY c.id, c.nombre
ORDER BY cantidad_productos DESC;
```

---

## 3. Reportes de Clientes

### 3.1 Clientes con Estadísticas

**Prompt:** "Clientes del año 2025 en Excel"

**ORM Query:**

```python
from apps.accounts.models import User
from django.db.models import Count, Sum
from datetime import datetime

start_date = datetime(2025, 1, 1).date()
end_date = datetime(2025, 12, 31).date()

queryset = User.objects.filter(
    rol__nombre='Cliente',
    created_at__date__gte=start_date,
    created_at__date__lte=end_date
).annotate(
    cantidad_pedidos=Count('pedidos'),
    total_gastado=Sum('pedidos__total')
).order_by('-total_gastado')

data = [{
    'nombre_completo': user.nombre_completo,
    'email': user.email,
    'telefono': user.telefono or '-',
    'fecha_registro': user.created_at.strftime('%d/%m/%Y'),
    'cantidad_pedidos': user.cantidad_pedidos,
    'total_gastado': float(user.total_gastado or 0)
} for user in queryset]
```

**SQL Equivalente:**

```sql
SELECT
    CONCAT(u.nombre, ' ', u.apellido) as nombre_completo,
    u.email,
    COALESCE(u.telefono, '-') as telefono,
    u.created_at as fecha_registro,
    COUNT(p.id) as cantidad_pedidos,
    COALESCE(SUM(p.total), 0) as total_gastado
FROM usuario u
INNER JOIN rol r ON u.rol_id = r.id
LEFT JOIN pedido p ON p.usuario_id = u.id
WHERE r.nombre = 'Cliente'
  AND DATE(u.created_at) >= '2025-01-01'
  AND DATE(u.created_at) <= '2025-12-31'
GROUP BY u.id, u.nombre, u.apellido, u.email, u.telefono, u.created_at
ORDER BY total_gastado DESC;
```

---

### 3.2 Top Clientes

**Prompt:** "Top 10 clientes con más compras en PDF"

**ORM Query:**

```python
from apps.accounts.models import User
from django.db.models import Count, Sum

top_clientes = User.objects.filter(
    rol__nombre='Cliente'
).annotate(
    cantidad_pedidos=Count('pedidos'),
    total_gastado=Sum('pedidos__total')
).order_by('-total_gastado')[:10]

data = [{
    'posicion': idx + 1,
    'cliente': user.nombre_completo,
    'email': user.email,
    'cantidad_pedidos': user.cantidad_pedidos,
    'total_gastado': float(user.total_gastado or 0)
} for idx, user in enumerate(top_clientes)]
```

---

## 4. Reportes de Analytics

### 4.1 Resumen General

**ORM Query:**

```python
from apps.orders.models import Pedido
from apps.products.models import Prenda
from apps.accounts.models import User
from django.db.models import Sum, Count
from datetime import datetime

# Total de pedidos
total_orders = Pedido.objects.count()

# Pedidos este mes
orders_this_month = Pedido.objects.filter(
    created_at__month=datetime.now().month,
    created_at__year=datetime.now().year
).count()

# Ventas totales
total_sales = Pedido.objects.aggregate(
    total=Sum('total')
)['total'] or 0

# Ventas este mes
sales_this_month = Pedido.objects.filter(
    created_at__month=datetime.now().month,
    created_at__year=datetime.now().year
).aggregate(
    total=Sum('total')
)['total'] or 0

# Productos
total_products = Prenda.objects.filter(activa=True).count()

# Clientes
total_customers = User.objects.filter(rol__nombre='Cliente').count()

summary = {
    'total_orders': total_orders,
    'orders_this_month': orders_this_month,
    'total_sales': float(total_sales),
    'sales_this_month': float(sales_this_month),
    'total_products': total_products,
    'total_customers': total_customers,
}
```

---

## 5. Reportes de Logins

### 5.1 Logins por Período

**Prompt:** "Logins de los últimos 7 días en Excel"

**ORM Query:**

```python
from apps.accounts.models import LoginAudit
from datetime import datetime, timedelta

# Período
end_date = datetime.now().date()
start_date = end_date - timedelta(days=7)

queryset = LoginAudit.objects.filter(
    created_at__date__gte=start_date,
    created_at__date__lte=end_date
).select_related('user').order_by('-created_at')

data = [{
    'usuario': login.user.nombre_completo,
    'email': login.user.email,
    'fecha_hora': login.created_at.strftime('%d/%m/%Y %H:%M:%S'),
    'ip': login.ip_address,
    'exitoso': 'Sí' if login.success else 'No'
} for login in queryset]
```

**SQL Equivalente:**

```sql
SELECT
    CONCAT(u.nombre, ' ', u.apellido) as usuario,
    u.email,
    la.created_at as fecha_hora,
    la.ip_address as ip,
    CASE WHEN la.success = true THEN 'Sí' ELSE 'No' END as exitoso
FROM login_audit la
INNER JOIN usuario u ON la.user_id = u.id
WHERE DATE(la.created_at) >= CURRENT_DATE - INTERVAL '7 days'
  AND DATE(la.created_at) <= CURRENT_DATE
ORDER BY la.created_at DESC;
```

---

## 6. Reportes de Carritos

### 6.1 Carritos Activos

**Prompt:** "Carritos activos con items en PDF"

**ORM Query:**

```python
from apps.cart.models import Carrito
from django.db.models import Count, Q

queryset = Carrito.objects.annotate(
    num_items=Count('items', filter=Q(items__deleted_at__isnull=True))
).filter(num_items__gt=0).select_related('usuario')

data = [{
    'usuario': carrito.usuario.nombre_completo,
    'email': carrito.usuario.email,
    'cantidad_items': carrito.total_items,
    'cantidad_productos': carrito.cantidad_total_items,
    'subtotal': float(carrito.subtotal),
    'fecha_creacion': carrito.created_at.strftime('%d/%m/%Y %H:%M')
} for carrito in queryset]
```

**SQL Equivalente:**

```sql
SELECT
    CONCAT(u.nombre, ' ', u.apellido) as usuario,
    u.email,
    COUNT(CASE WHEN ic.deleted_at IS NULL THEN 1 END) as cantidad_items,
    SUM(CASE WHEN ic.deleted_at IS NULL THEN ic.cantidad ELSE 0 END) as cantidad_productos,
    SUM(CASE WHEN ic.deleted_at IS NULL THEN ic.cantidad * ic.precio_unitario ELSE 0 END) as subtotal,
    c.created_at as fecha_creacion
FROM carrito c
INNER JOIN usuario u ON c.usuario_id = u.id
LEFT JOIN item_carrito ic ON ic.carrito_id = c.id
GROUP BY c.id, u.nombre, u.apellido, u.email, c.created_at
HAVING COUNT(CASE WHEN ic.deleted_at IS NULL THEN 1 END) > 0;
```

---

## 7. Reportes de Top Productos

### 7.1 Productos Más Vendidos

**Prompt:** "Top 10 productos más vendidos del año 2025 en PDF"

**ORM Query:**

```python
from apps.orders.models import DetallePedido
from django.db.models import Sum, F
from datetime import datetime

# Filtro de período
start_date = datetime(2025, 1, 1).date()
end_date = datetime(2025, 12, 31).date()

detalles_qs = DetallePedido.objects.filter(
    pedido__created_at__date__gte=start_date,
    pedido__created_at__date__lte=end_date
).values(
    'prenda__nombre',
    'prenda__precio'
).annotate(
    cantidad_vendida=Sum('cantidad'),
    total_ingresos=Sum(F('cantidad') * F('precio_unitario'))
).order_by('-cantidad_vendida')[:10]

data = [{
    'posicion': idx + 1,
    'producto': item['prenda__nombre'],
    'precio_unitario': float(item['prenda__precio']),
    'cantidad_vendida': item['cantidad_vendida'],
    'total_ingresos': float(item['total_ingresos'])
} for idx, item in enumerate(detalles_qs)]
```

**SQL Equivalente:**

```sql
SELECT
    pr.nombre as producto,
    pr.precio as precio_unitario,
    SUM(dp.cantidad) as cantidad_vendida,
    SUM(dp.cantidad * dp.precio_unitario) as total_ingresos
FROM detalle_pedido dp
INNER JOIN prenda pr ON dp.prenda_id = pr.id
INNER JOIN pedido p ON dp.pedido_id = p.id
WHERE DATE(p.created_at) >= '2025-01-01'
  AND DATE(p.created_at) <= '2025-12-31'
GROUP BY pr.nombre, pr.precio
ORDER BY cantidad_vendida DESC
LIMIT 10;
```

---

## 8. Reportes de Ingresos

### 8.1 Ingresos por Día

**Prompt:** "Ingresos por día del mes actual en Excel"

**ORM Query:**

```python
from apps.orders.models import Pedido
from django.db.models import Count, Sum
from datetime import datetime

# Mes actual
current_month = datetime.now().month
current_year = datetime.now().year

queryset = Pedido.objects.filter(
    created_at__month=current_month,
    created_at__year=current_year
)

ingresos_por_dia = queryset.extra({
    'fecha': "DATE(created_at)"
}).values('fecha').annotate(
    cantidad_pedidos=Count('id'),
    total_ingresos=Sum('total')
).order_by('fecha')

data = [{
    'fecha': item['fecha'].strftime('%d/%m/%Y') if hasattr(item['fecha'], 'strftime') else str(item['fecha']),
    'cantidad_pedidos': item['cantidad_pedidos'],
    'total_ingresos': float(item['total_ingresos'] or 0)
} for item in ingresos_por_dia]
```

**SQL Equivalente:**

```sql
SELECT
    DATE(created_at) as fecha,
    COUNT(id) as cantidad_pedidos,
    SUM(total) as total_ingresos
FROM pedido
WHERE EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM CURRENT_DATE)
  AND EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY DATE(created_at)
ORDER BY fecha;
```

---

## Optimizaciones y Mejores Prácticas

### 1. Uso de select_related() y prefetch_related()

Siempre que se acceda a relaciones ForeignKey o ManyToMany, usar estas funciones para evitar N+1 queries:

```python
# ✅ Correcto
queryset = Pedido.objects.select_related('usuario', 'direccion_envio')

# ❌ Incorrecto (N+1 queries)
queryset = Pedido.objects.all()
for pedido in queryset:
    print(pedido.usuario.nombre)  # Query extra por cada pedido
```

### 2. Índices en Base de Datos

Asegurar que existan índices en:

- Campos de fecha (created_at, updated_at)
- Claves foráneas
- Campos usados frecuentemente en filtros

```python
class Meta:
    indexes = [
        models.Index(fields=['usuario', '-created_at']),
        models.Index(fields=['estado', '-created_at']),
    ]
```

### 3. Limitación de Resultados

Siempre aplicar límites para evitar sobrecarga:

```python
# Con límite explícito
queryset = Pedido.objects.all()[:10000]

# Con paginación
from django.core.paginator import Paginator
paginator = Paginator(queryset, 1000)
```

### 4. Uso de only() y defer()

Para reducir la cantidad de datos transferidos:

```python
# Solo necesitamos algunos campos
queryset = Pedido.objects.only('numero_pedido', 'total', 'created_at')
```

### 5. Agregaciones Eficientes

Usar agregaciones en la base de datos en lugar de Python:

```python
# ✅ Correcto
total = Pedido.objects.aggregate(Sum('total'))['total__sum']

# ❌ Incorrecto
total = sum(pedido.total for pedido in Pedido.objects.all())
```

---

## Referencias

- [Django QuerySet API](https://docs.djangoproject.com/en/4.2/ref/models/querysets/)
- [Django Aggregation](https://docs.djangoproject.com/en/4.2/topics/db/aggregation/)
- [Django Database Optimization](https://docs.djangoproject.com/en/4.2/topics/db/optimization/)

---

**Autor:** SmartSales365 Development Team  
**Última actualización:** 2025-11-10
