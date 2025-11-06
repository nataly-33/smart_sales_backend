# 📚 Guía de Documentación Técnica - Backend SmartSales365

**Versión:** 1.0
**Fecha:** 6 de Noviembre, 2025
**Framework:** Django 4.2.7 + Django REST Framework 3.14.0

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Apps de Django](#apps-de-django)
5. [Modelos de Datos](#modelos-de-datos)
6. [Lógica de Negocio por App](#lógica-de-negocio-por-app)
7. [Sistema de Autenticación](#sistema-de-autenticación)
8. [Permisos y Roles](#permisos-y-roles)
9. [Servicios Externos](#servicios-externos)
10. [Seeders y Datos de Prueba](#seeders-y-datos-de-prueba)
11. [Configuración de Producción](#configuración-de-producción)

---

## 🎯 Introducción

Este documento es la guía técnica completa del backend de **SmartSales365**, un sistema POS/E-commerce de ropa femenina que integra:

- **Gestión Comercial**: Productos, Stock, Carrito, Ventas
- **Inteligencia Artificial**: Predicción de ventas con Random Forest
- **Reportes Dinámicos**: Generación mediante prompts de texto o voz
- **Multi-rol**: Admin, Empleado, Cliente

### Características Principales

- **Django REST Framework** para API RESTful
- **PostgreSQL** como base de datos
- **JWT** para autenticación
- **RBAC** (Role-Based Access Control) granular
- **Soft Delete** en todos los modelos
- **Swagger/OpenAPI** con drf-spectacular
- **AWS S3** para imágenes (producción)
- **PayPal** para pagos online

---

## 🏗️ Arquitectura del Sistema

### Arquitectura de 3 Capas

```
┌─────────────────────────────────────────┐
│         Capa de Presentación            │
│  Frontend (React) + Móvil (Flutter)     │
├─────────────────────────────────────────┤
│         Capa de Lógica de Negocio       │
│  Django REST Framework (API)            │
│  - Views (ViewSets)                     │
│  - Serializers                          │
│  - Services (Lógica compleja)           │
│  - Permissions                          │
├─────────────────────────────────────────┤
│         Capa de Datos                   │
│  PostgreSQL (Modelos ORM)               │
│  - Models con soft delete               │
│  - Migraciones                          │
└─────────────────────────────────────────┘
```

### Flujo de Peticiones

```
Cliente (React/Flutter)
    ↓
API Endpoint (URL)
    ↓
Autenticación (JWT)
    ↓
Permisos (RBAC)
    ↓
ViewSet (DRF)
    ↓
Serializer (Validación)
    ↓
Service (Lógica de negocio)
    ↓
Model (ORM)
    ↓
PostgreSQL
```

---

## 📁 Estructura del Proyecto

```
ss_backend/
├── apps/                           # Aplicaciones Django
│   ├── core/                       # Base: modelos abstractos, permisos
│   ├── accounts/                   # Autenticación, usuarios, roles
│   ├── products/                   # Catálogo, stock, categorías
│   ├── customers/                  # Clientes, direcciones, favoritos
│   ├── cart/                       # Carrito de compras
│   └── orders/                     # Pedidos, pagos, envíos
├── config/                         # Configuración del proyecto
│   ├── settings/
│   │   ├── base.py                 # Settings comunes
│   │   ├── development.py          # Dev
│   │   └── production.py           # Prod
│   ├── urls.py                     # URLs principales
│   └── wsgi.py / asgi.py
├── media/                          # Archivos subidos (local)
├── static/                         # Archivos estáticos
├── scripts/                        # Scripts utilitarios
│   ├── seed_data.py               # Seeder principal
│   └── upload_to_s3.py            # Subir imágenes a S3
├── docs/                           # Documentación
│   ├── documentation_guide.md     # Este archivo
│   ├── endpoints.md               # Lista de endpoints
│   └── status.md                  # Estado del proyecto
├── requirements.txt                # Dependencias Python
├── manage.py
├── .env                           # Variables de entorno
└── README.md
```

---

## 📦 Apps de Django

El backend está organizado en **6 aplicaciones principales**:

### 1. **apps/core/** - Núcleo del Sistema

**Propósito**: Proveer funcionalidad base reutilizable para todas las apps.

**Contenido**:
- `BaseModel`: Modelo abstracto con soft delete, timestamps, UUID
- `IsAdminUser`, `IsEmpleadoOrAdmin`, `IsOwnerOrAdmin`: Permisos personalizados
- `constants.py`: Constantes del sistema (roles, estados, permisos)

**¿Tiene algo especial?**
✅ Sí - Todos los modelos heredan de `BaseModel` para tener `is_deleted`, `created_at`, `updated_at` automáticamente.

---

### 2. **apps/accounts/** - Autenticación y Usuarios

**Propósito**: Gestionar usuarios, roles y permisos del sistema.

#### **Modelos**

##### `User` (Usuario personalizado)
```python
class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(unique=True)  # Username = email
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    foto_perfil = models.ImageField(upload_to='usuarios/', blank=True)
    rol = models.ForeignKey('Role', on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Propiedades
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    # Métodos
    def tiene_permiso(self, codigo_permiso: str) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        if self.rol.nombre == "Admin":
            return True
        return self.rol.permisos.filter(codigo=codigo_permiso).exists()
```

**¿Qué hace especial este modelo?**
- Email como username único
- Relación con `Role` (un usuario = un rol)
- Método `tiene_permiso()` para verificación dinámica
- Soft delete heredado de `BaseModel`

##### `Role` (Rol)
```python
class Role(BaseModel):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    permisos = models.ManyToManyField('Permission', related_name='roles')
    es_rol_sistema = models.BooleanField(default=False)  # No eliminable
```

**Roles del sistema**:
1. **Admin** - Todos los permisos
2. **Empleado** - Gestión de productos, ventas, clientes
3. **Cliente** - Solo lectura de productos, gestión de su carrito/pedidos

##### `Permission` (Permiso)
```python
class Permission(BaseModel):
    codigo = models.CharField(max_length=50, unique=True)  # ej: "productos.crear"
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    modulo = models.CharField(max_length=50)  # ej: "productos"
```

**Estructura de permisos**: `{módulo}.{acción}`

Ejemplos:
- `productos.crear`
- `productos.leer`
- `pedidos.aprobar`
- `reportes.generar`

#### **ViewSets**

- `LoginViewSet`: Login con JWT (POST `/api/auth/login/`)
- `RegisterViewSet`: Registro público (crea Cliente) (POST `/api/auth/register/`)
- `UserViewSet`: CRUD de usuarios (Admin) (GET/POST/PATCH/DELETE `/api/auth/users/`)
- `RoleViewSet`: CRUD de roles (Admin) (GET/POST/PATCH/DELETE `/api/auth/roles/`)
- `PermissionViewSet`: Listar permisos (GET `/api/auth/permissions/`)

#### **Serializadores Especiales**

**`CustomTokenObtainPairSerializer`**
```python
# Response del login incluye:
{
    "access": "token...",
    "refresh": "token...",
    "user": {
        "id": "uuid",
        "email": "usuario@mail.com",
        "nombre_completo": "Juan Perez",
        "rol_detalle": {
            "nombre": "Cliente",
            "permisos": [...]
        }
    }
}
```

#### **¿Es solo CRUD o tiene lógica especial?**

✅ **Tiene lógica especial**:
- Login personalizado que retorna usuario completo con rol y permisos
- Registro automático asigna rol "Cliente"
- Endpoint `/api/auth/users/me/` retorna usuario actual sin ID
- Verificación de permisos antes de cada acción sensible

---

### 3. **apps/products/** - Catálogo de Productos

**Propósito**: Gestionar el catálogo de ropa femenina (prendas, stock, categorías, marcas).

#### **Modelos**

##### `Categoria`
```python
class Categoria(BaseModel):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True)
    activa = models.BooleanField(default=True)
```

**Ejemplos**: Vestidos, Blusas, Pantalones, Faldas

##### `Marca`
```python
class Marca(BaseModel):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    logo = models.ImageField(upload_to='marcas/', blank=True)
    activa = models.BooleanField(default=True)
```

##### `Talla`
```python
class Talla(BaseModel):
    nombre = models.CharField(max_length=10, unique=True)  # XS, S, M, L, XL
    orden = models.IntegerField(default=0)  # Para ordenar
```

##### `Prenda` (Producto principal)
```python
class Prenda(BaseModel):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)  # Auto-generado
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    categorias = models.ManyToManyField(Categoria, related_name='prendas')
    tallas = models.ManyToManyField(Talla, through='StockPrenda')
    color = models.CharField(max_length=50)
    material = models.CharField(max_length=100, blank=True)

    # Flags
    activa = models.BooleanField(default=True)
    destacada = models.BooleanField(default=False)
    es_novedad = models.BooleanField(default=False)

    # Propiedades calculadas
    @property
    def imagen_principal(self):
        """Retorna la primera imagen o None"""
        return self.imagenes.filter(es_principal=True).first() or self.imagenes.first()

    @property
    def stock_total(self):
        """Suma del stock de todas las tallas"""
        return self.stocks.aggregate(total=Sum('cantidad'))['total'] or 0
```

**¿Qué hace especial este modelo?**
- Slug auto-generado en `save()` (para URLs amigables)
- Relación ManyToMany con `Talla` a través de `StockPrenda` (tabla intermedia)
- `imagen_principal` retorna la imagen marcada como principal
- `stock_total` calcula el stock sumando todas las tallas

##### `StockPrenda` (Inventario por talla)
```python
class StockPrenda(BaseModel):
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE)
    talla = models.ForeignKey(Talla, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)

    class Meta:
        unique_together = ['prenda', 'talla']

    @property
    def alerta_stock_bajo(self):
        return self.cantidad <= self.stock_minimo

    def reducir_stock(self, cantidad: int):
        if self.cantidad < cantidad:
            raise ValueError("Stock insuficiente")
        self.cantidad -= cantidad
        self.save()

    def aumentar_stock(self, cantidad: int):
        self.cantidad += cantidad
        self.save()
```

**¿Qué hace especial?**
- `unique_together` asegura una sola fila por (prenda, talla)
- Métodos `reducir_stock()` y `aumentar_stock()` con validación
- Property `alerta_stock_bajo` para UI

##### `ImagenPrenda` (Galería)
```python
class ImagenPrenda(BaseModel):
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')
    es_principal = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Si se marca como principal, desmarcar las demás
        if self.es_principal:
            ImagenPrenda.objects.filter(prenda=self.prenda, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)
```

**¿Qué hace especial?**
- Al marcar una como `es_principal=True`, desmarca las demás automáticamente

#### **ViewSets**

- `PrendaViewSet`: CRUD de productos
  - Lectura: Pública
  - Crear/Editar/Eliminar: Solo Admin
  - Filtros: búsqueda, categoría, marca, precio_min, precio_max
- `CategoriaViewSet`: CRUD de categorías (Admin)
- `MarcaViewSet`: CRUD de marcas (Admin)
- `TallaViewSet`: Listar tallas (Público)

#### **¿Es solo CRUD o tiene servicios especiales?**

✅ **Servicios especiales**:
- Al crear/editar prenda, automáticamente se crean `StockPrenda` para cada talla seleccionada
- Al eliminar (soft delete), NO se elimina el stock (queda huérfano pero accesible para auditoría)
- Endpoint personalizado `/api/products/prendas/{slug}/stock/` para ver stock por talla

---

### 4. **apps/customers/** - Gestión de Clientes

**Propósito**: Gestionar perfiles de clientes, direcciones de envío y favoritos.

#### **Modelos**

##### `Direccion`
```python
class Direccion(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones')
    calle = models.CharField(max_length=200)
    numero_exterior = models.CharField(max_length=20)
    numero_interior = models.CharField(max_length=20, blank=True)
    colonia = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    pais = models.CharField(max_length=100, default='Bolivia')
    telefono_contacto = models.CharField(max_length=20, blank=True)
    es_principal = models.BooleanField(default=False)

    @property
    def direccion_completa(self):
        parts = [self.calle, self.numero_exterior]
        if self.numero_interior:
            parts.append(f"Int. {self.numero_interior}")
        if self.colonia:
            parts.append(self.colonia)
        parts.extend([self.ciudad, self.estado, self.codigo_postal])
        return ", ".join(parts)

    def save(self, *args, **kwargs):
        # Primera dirección del usuario es principal automáticamente
        if not Direccion.objects.filter(usuario=self.usuario, is_deleted=False).exists():
            self.es_principal = True
        # Si se marca como principal, desmarcar las demás
        if self.es_principal:
            Direccion.objects.filter(usuario=self.usuario, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)
```

**¿Qué hace especial?**
- Property `direccion_completa` para formatear dirección
- Al crear la primera dirección, se marca como principal automáticamente
- Al marcar una como principal, las demás se desmarcan

##### `Favoritos`
```python
class Favoritos(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    prenda = models.ForeignKey('products.Prenda', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['usuario', 'prenda']
```

**¿Qué hace especial?**
- `unique_together` previene favoritos duplicados

#### **ViewSets**

- `ProfileViewSet`: Ver/editar perfil del usuario actual
- `DireccionViewSet`: CRUD de direcciones (solo del usuario actual)
- `FavoritosViewSet`: CRUD de favoritos

#### **¿Es solo CRUD o tiene servicios especiales?**

⚠️ **Mayormente CRUD**, pero:
- Endpoint `/api/customers/profile/` retorna perfil completo (usuario + direcciones + favoritos)
- Todas las queries filtran automáticamente por `request.user` (no pueden ver datos de otros)

---

### 5. **apps/cart/** - Carrito de Compras

**Propósito**: Gestionar el carrito de compras de cada usuario.

#### **Modelos**

##### `Carrito`
```python
class Carrito(BaseModel):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')

    @property
    def total_items(self):
        return self.items.filter(is_deleted=False).aggregate(total=Sum('cantidad'))['total'] or 0

    @property
    def subtotal(self):
        return self.items.filter(is_deleted=False).aggregate(
            total=Sum(F('precio_unitario') * F('cantidad'))
        )['total'] or Decimal('0.00')

    @property
    def total(self):
        # Aquí podrías agregar descuentos, envío, etc.
        return self.subtotal

    def limpiar(self):
        """Soft delete de todos los items"""
        self.items.update(is_deleted=True)
```

**¿Qué hace especial?**
- OneToOne con User (un usuario = un carrito)
- Properties calculadas en tiempo real (`total_items`, `subtotal`, `total`)
- Método `limpiar()` hace soft delete de items (no los elimina, por auditoría)

##### `ItemCarrito`
```python
class ItemCarrito(BaseModel):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    prenda = models.ForeignKey('products.Prenda', on_delete=models.PROTECT)
    talla = models.ForeignKey('products.Talla', on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['carrito', 'prenda', 'talla']

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def verificar_stock(self):
        """Verifica si hay stock disponible para la cantidad solicitada"""
        stock = StockPrenda.objects.get(prenda=self.prenda, talla=self.talla)
        if stock.cantidad < self.cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {stock.cantidad}")

    def save(self, *args, **kwargs):
        # Guardar precio actual de la prenda (snapshot)
        if not self.precio_unitario:
            self.precio_unitario = self.prenda.precio
        # Verificar stock antes de guardar
        self.verificar_stock()
        super().save(*args, **kwargs)
```

**¿Qué hace especial?**
- Guarda `precio_unitario` al momento de agregar (snapshot del precio, por si cambia después)
- `verificar_stock()` antes de guardar (evita agregar más de lo disponible)
- `unique_together` previene duplicados (mismo producto + talla)

#### **ViewSets**

- `CarritoViewSet`:
  - `GET /api/cart/` - Obtener mi carrito
  - `POST /api/cart/add/` - Agregar item
  - `PATCH /api/cart/{item_id}/update-item/` - Actualizar cantidad
  - `DELETE /api/cart/{item_id}/remove/` - Eliminar item
  - `POST /api/cart/clear/` - Vaciar carrito

#### **¿Es solo CRUD o tiene servicios especiales?**

✅ **Servicios especiales**:
- Al agregar item, automáticamente verifica stock y guarda snapshot del precio
- Al actualizar cantidad, re-verifica stock
- Al eliminar, hace soft delete (no elimina realmente)
- Endpoint `clear` vacía el carrito sin eliminarlo

---

### 6. **apps/orders/** - Pedidos y Pagos

**Propósito**: Gestionar pedidos, pagos y seguimiento de envíos.

#### **Modelos**

##### `MetodoPago`
```python
class MetodoPago(BaseModel):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)  # 'efectivo', 'paypal', etc.
    descripcion = models.TextField(blank=True)
    requiere_procesador = models.BooleanField(default=False)  # True para PayPal, Stripe
    activo = models.BooleanField(default=True)
    configuracion = models.JSONField(default=dict, blank=True)  # Datos específicos del procesador
```

##### `Pedido`
```python
class Pedido(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pedidos')
    numero_pedido = models.CharField(max_length=50, unique=True, blank=True)

    # Dirección de envío (snapshot)
    direccion = models.ForeignKey('customers.Direccion', on_delete=models.SET_NULL, null=True)
    direccion_snapshot = models.JSONField(default=dict)  # Backup si se elimina la dirección

    # Items y totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Estados
    estado = models.CharField(max_length=50, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('pago_recibido', 'Pago Recibido'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'Preparando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ])

    notas = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Generar número de pedido único
        if not self.numero_pedido:
            import random
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_part = random.randint(1000, 9999)
            self.numero_pedido = f"ORD-{timestamp}-{random_part}"

        # Guardar snapshot de dirección
        if self.direccion and not self.direccion_snapshot:
            self.direccion_snapshot = {
                'calle': self.direccion.calle,
                'ciudad': self.direccion.ciudad,
                'estado': self.direccion.estado,
                'codigo_postal': self.direccion.codigo_postal,
                'direccion_completa': self.direccion.direccion_completa,
            }

        super().save(*args, **kwargs)

    def cambiar_estado(self, nuevo_estado: str, usuario: User, notas: str = ""):
        """Cambia el estado y registra en historial"""
        self.estado = nuevo_estado
        self.save()
        HistorialEstadoPedido.objects.create(
            pedido=self,
            estado_anterior=self.estado,
            estado_nuevo=nuevo_estado,
            usuario=usuario,
            notas=notas
        )

    @property
    def puede_cancelar(self):
        return self.estado in ['pendiente', 'pago_recibido', 'confirmado']
```

**¿Qué hace especial?**
- `numero_pedido` se genera automáticamente (ORD-{timestamp}-{random})
- `direccion_snapshot` guarda copia de la dirección (por si el cliente la elimina después)
- Método `cambiar_estado()` registra automáticamente en `HistorialEstadoPedido`
- Property `puede_cancelar` valida si el pedido aún se puede cancelar

##### `DetallePedido`
```python
class DetallePedido(BaseModel):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    prenda = models.ForeignKey('products.Prenda', on_delete=models.PROTECT)
    talla = models.ForeignKey('products.Talla', on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    # Snapshot del producto (por si se elimina después)
    producto_snapshot = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        # Calcular subtotal
        self.subtotal = self.precio_unitario * self.cantidad

        # Guardar snapshot del producto
        if not self.producto_snapshot:
            self.producto_snapshot = {
                'nombre': self.prenda.nombre,
                'marca': self.prenda.marca.nombre,
                'color': self.prenda.color,
                'talla': self.talla.nombre,
            }

        super().save(*args, **kwargs)
```

##### `Pago`
```python
class Pago(BaseModel):
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name='pagos')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ])

    # IDs externos (PayPal, Stripe)
    paypal_order_id = models.CharField(max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)

    # Datos del procesador
    response_data = models.JSONField(default=dict, blank=True)

    def marcar_completado(self):
        self.estado = 'completado'
        self.save()
        # Actualizar estado del pedido
        self.pedido.estado = 'pago_recibido'
        self.pedido.save()
```

##### `HistorialEstadoPedido`
```python
class HistorialEstadoPedido(BaseModel):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notas = models.TextField(blank=True)
```

#### **ViewSets**

- `PedidoViewSet`:
  - Cliente: Ver sus pedidos, crear, cancelar
  - Admin/Empleado: Ver todos, actualizar estado
- `MetodoPagoViewSet`: Listar métodos de pago activos

#### **Servicios Especiales**

**`PayPalService`** (archivo: `apps/orders/services/paypal_service.py`)
```python
class PayPalService:
    def create_order(self, pedido: Pedido):
        """Crea orden en PayPal"""
        # Llama a PayPal API
        # Retorna paypal_order_id

    def capture_order(self, paypal_order_id: str):
        """Captura el pago"""
        # Llama a PayPal API
        # Actualiza estado del pago
```

**¿Es solo CRUD o tiene servicios especiales?**

✅ **Servicios especiales complejos**:
- Proceso de checkout completo:
  1. Valida stock de todos los items
  2. Crea pedido con snapshot de dirección
  3. Crea detalles del pedido con snapshot de productos
  4. Reduce stock automáticamente
  5. Crea pago pendiente
  6. Si es PayPal, crea orden externa
  7. Vacía el carrito
- Webhook de PayPal para confirmar pagos
- Cancelación de pedido restaura stock

---

## 🔐 Sistema de Autenticación

### JWT (JSON Web Tokens)

**Librería**: `djangorestframework-simplejwt`

**Configuración** (en `config/settings/base.py`):
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

**Flujo de Autenticación**:

1. **Login**:
   ```
   POST /api/auth/login/
   Body: { "email": "usuario@mail.com", "password": "pass123" }

   Response:
   {
       "access": "eyJ...",
       "refresh": "eyJ...",
       "user": { ... }
   }
   ```

2. **Usar Access Token**:
   ```
   GET /api/products/prendas/
   Headers: { "Authorization": "Bearer eyJ..." }
   ```

3. **Refresh Token** (cuando access expira):
   ```
   POST /api/auth/refresh/
   Body: { "refresh": "eyJ..." }

   Response: { "access": "nuevo_token..." }
   ```

---

## 🛡️ Permisos y Roles

### Sistema RBAC (Role-Based Access Control)

**Arquitectura**:
```
User → Role → Permissions
```

**Permisos disponibles** (ver `apps/core/constants.py`):

```python
PERMISSIONS = {
    'productos': ['crear', 'leer', 'actualizar', 'eliminar'],
    'categorias': ['crear', 'leer', 'actualizar', 'eliminar'],
    'marcas': ['crear', 'leer', 'actualizar', 'eliminar'],
    'pedidos': ['crear', 'leer', 'actualizar', 'eliminar', 'aprobar'],
    'usuarios': ['crear', 'leer', 'actualizar', 'eliminar'],
    'roles': ['crear', 'leer', 'actualizar', 'eliminar'],
    'reportes': ['generar', 'exportar'],
    # ...
}
```

**Roles y sus permisos**:

| Rol      | Permisos                                                           |
|----------|--------------------------------------------------------------------|
| Admin    | TODOS (100%)                                                       |
| Empleado | productos.*, categorias.*, pedidos.*, clientes.*, ventas.*         |
| Cliente  | productos.leer, categorias.leer, pedidos.crear, pedidos.leer       |

**Uso en ViewSets**:

```python
# Opción 1: Permission classes
class PrendaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]  # Solo Admin puede escribir

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]  # Lectura pública
        return super().get_permissions()

# Opción 2: Verificación manual
def create(self, request):
    if not request.user.tiene_permiso('productos.crear'):
        return Response({'error': 'Sin permisos'}, status=403)
    # ...
```

---

## 🌐 Servicios Externos

### 1. AWS S3 (Almacenamiento de Imágenes)

**Estado**: Configurado pero `USE_S3=False` en desarrollo

**Configuración** (producción):
```python
# settings/production.py
USE_S3 = True
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-east-1'
```

**Script de subida** (ver `scripts/upload_to_s3.py`):
```bash
python scripts/upload_to_s3.py --category vestidos --folder ./datasets/vestidos/
```

### 2. PayPal

**Estado**: Parcialmente implementado

**Configuración**:
```python
PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = env('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = env('PAYPAL_MODE', 'sandbox')  # 'sandbox' o 'live'
```

**Servicio**: `apps/orders/services/paypal_service.py`

**Endpoints**:
- `POST /api/orders/paypal/create-order/` - Crea orden en PayPal
- `POST /api/orders/paypal/capture/` - Captura el pago

### 3. Stripe

**Estado**: Configurado pero NO implementado en views

**Para implementar**:
1. Crear vista `POST /api/orders/stripe/create-payment-intent/`
2. Crear webhook `POST /api/orders/stripe/webhook/`

---

## 🌱 Seeders y Datos de Prueba

### Script Principal: `scripts/seed_data.py`

**Ejecutar**:
```bash
python manage.py shell < scripts/seed_data.py
```

**Qué crea**:

1. **Permisos del sistema** (basado en `PERMISSIONS` de constants.py)
2. **3 Roles**:
   - Admin (todos los permisos)
   - Empleado (productos, pedidos, clientes)
   - Cliente (solo lectura)
3. **Usuarios de prueba**:
   - `admin@smartsales365.com` / `Admin2024!`
   - `empleado@smartsales365.com` / `Empleado2024!`
   - `cliente@gmail.com` / `Cliente2024!`
4. **4 Categorías**: Vestidos, Blusas, Pantalones, Faldas
5. **5 Marcas**: Zara, H&M, Mango, Forever 21, Shein
6. **6 Tallas**: XS, S, M, L, XL, XXL
7. **Productos con stock** (ejemplo):
   ```python
   Prenda.objects.create(
       nombre="Vestido Floral Rosa",
       precio=350.00,
       marca=marca_zara,
       # ...
   )
   # Stock para cada talla
   ```
8. **Métodos de pago**:
   - Efectivo
   - PayPal
   - (Stripe si se habilita)

### Script de Subida a S3: `scripts/upload_to_s3.py`

**Uso**:
```bash
# Subir dataset de vestidos
python scripts/upload_to_s3.py \
    --category vestidos \
    --folder ./datasets/vestidos/ \
    --bucket smartsales365-products

# El script:
# 1. Lee todas las imágenes del folder
# 2. Las sube a S3 en la carpeta productos/{categoria}/
# 3. Retorna las URLs de S3
# 4. (Opcional) Crea productos automáticamente con esas URLs
```

**Integración con seeder**:
```python
# En seed_data.py
from scripts.upload_to_s3 import upload_category_images

# Subir imágenes y obtener URLs
urls_vestidos = upload_category_images('vestidos', './datasets/vestidos/')

# Crear productos con esas URLs
for i, url in enumerate(urls_vestidos):
    Prenda.objects.create(
        nombre=f"Vestido {i+1}",
        imagen_url=url,
        categoria=categoria_vestidos,
        # ...
    )
```

---

## ⚙️ Configuración de Producción

### Variables de Entorno Requeridas

**Archivo**: `.env`

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgres://user:password@host:port/dbname

# AWS S3
USE_S3=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket

# PayPal
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-secret
PAYPAL_MODE=live

# CORS (Frontend)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Deployment

**Plataformas recomendadas**:
- AWS EC2 + RDS (PostgreSQL)
- Heroku
- Railway
- Render

**Pasos**:
1. Configurar variables de entorno
2. `python manage.py migrate`
3. `python manage.py collectstatic`
4. `python scripts/seed_data.py` (datos iniciales)
5. Configurar Gunicorn/uWSGI
6. Configurar Nginx (reverse proxy)
7. Configurar SSL (Let's Encrypt)

---

## 📊 Módulos Pendientes de Implementar

### 1. Reportes Dinámicos (Prioridad Alta)

**Requerimiento**: Generación de reportes mediante prompts de texto o voz.

**Componentes a crear**:

**a) Parser de Prompts** (`apps/reports/services/prompt_parser.py`)
```python
class PromptParser:
    def parse(self, prompt: str) -> ReportQuery:
        """
        Interpreta prompts como:
        "Reporte de ventas de septiembre agrupado por producto en PDF"

        Returns: {
            'tipo': 'ventas',
            'periodo': ('2025-09-01', '2025-09-30'),
            'agrupacion': 'producto',
            'formato': 'pdf'
        }
        """
        # Usar regex o NLP simple
```

**b) Query Builder** (`apps/reports/services/query_builder.py`)
```python
class QueryBuilder:
    def build_query(self, report_query: ReportQuery):
        """Construye query SQL/ORM dinámicamente"""
        if report_query['tipo'] == 'ventas':
            queryset = Pedido.objects.filter(
                created_at__range=report_query['periodo']
            )
            if report_query['agrupacion'] == 'producto':
                queryset = queryset.values('detalles__prenda__nombre').annotate(
                    total_ventas=Sum('total')
                )
        return queryset
```

**c) Generadores** (`apps/reports/services/generators.py`)
```python
class PDFGenerator:
    def generate(self, data, title):
        """Genera PDF con ReportLab"""

class ExcelGenerator:
    def generate(self, data, title):
        """Genera Excel con openpyxl"""
```

**d) ViewSet** (`apps/reports/views.py`)
```python
class ReportViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def generate(self, request):
        prompt = request.data.get('prompt')
        # 1. Parsear prompt
        # 2. Construir query
        # 3. Generar reporte
        # 4. Retornar archivo
```

### 2. IA Predictiva con Random Forest (Prioridad Alta)

**Requerimiento**: Dashboard con predicción de ventas futuras.

**Componentes a crear**:

**a) Preparación de Datos** (`apps/ai/services/data_preparation.py`)
```python
class DataPreparation:
    def prepare_training_data(self):
        """
        Obtiene datos históricos de ventas y los transforma:
        - Características: mes, año, categoría, precio promedio
        - Target: cantidad vendida
        """
        ventas = DetallePedido.objects.values(
            'prenda__categoria__nombre',
            'created_at__month',
            'created_at__year'
        ).annotate(
            total_vendido=Sum('cantidad'),
            precio_promedio=Avg('precio_unitario')
        )

        df = pd.DataFrame(ventas)
        X = df[['created_at__month', 'created_at__year', 'precio_promedio']]
        y = df['total_vendido']
        return X, y
```

**b) Entrenamiento** (`apps/ai/services/model_training.py`)
```python
from sklearn.ensemble import RandomForestRegressor
import joblib

class ModelTraining:
    def train(self):
        X, y = DataPreparation().prepare_training_data()

        # Entrenar Random Forest
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Guardar modelo
        joblib.dump(model, 'models/ventas_predictor.pkl')

        return model
```

**c) Predicción** (`apps/ai/services/prediction.py`)
```python
class PredictionService:
    def predict_sales(self, mes: int, año: int, categoria: str):
        # Cargar modelo
        model = joblib.load('models/ventas_predictor.pkl')

        # Preparar features
        X_pred = [[mes, año, precio_promedio_categoria]]

        # Predecir
        ventas_predichas = model.predict(X_pred)

        return ventas_predichas[0]
```

**d) ViewSet** (`apps/ai/views.py`)
```python
class PredictionViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def sales_forecast(self, request):
        mes = request.query_params.get('mes')
        año = request.query_params.get('año')

        prediccion = PredictionService().predict_sales(mes, año)

        return Response({
            'mes': mes,
            'año': año,
            'ventas_predichas': prediccion
        })
```

### 3. Notificaciones (Prioridad Media)

**Crear app**: `apps/notifications/`

**Modelos**:
```python
class Notification(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)  # 'pedido', 'stock_bajo', etc.
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    url = models.CharField(max_length=200, blank=True)
```

**Endpoints**:
- `GET /api/notifications/` - Listar notificaciones
- `PATCH /api/notifications/{id}/mark-read/` - Marcar como leída

---

## 📚 Recursos y Referencias

- **Documentación oficial**: Ver `README.md`
- **Endpoints completos**: Ver `docs/endpoints.md`
- **Estado del proyecto**: Ver `docs/status.md`
- **Swagger**: http://localhost:8000/api/docs/
- **Admin Django**: http://localhost:8000/admin/

---

**Última actualización**: 6 de Noviembre 2025
**Creado por**: Claude Code Assistant
