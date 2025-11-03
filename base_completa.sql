-- ========================================
-- MÓDULO 1: AUTENTICACIÓN Y AUTORIZACIÓN
-- ========================================

-- 1. rol (4 roles: admin, empleado, cliente, delivery)
CREATE TABLE rol (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. permiso (granular por módulo)
CREATE TABLE permiso (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(100) UNIQUE NOT NULL, -- ej: 'producto.crear'
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(50), -- productos, ventas, reportes, etc
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. permiso_rol (relación N:N)
CREATE TABLE permiso_rol (
    rol_id UUID REFERENCES rol(id) ON DELETE CASCADE,
    permiso_id UUID REFERENCES permiso(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

-- 4. usuario (todos los usuarios del sistema)
CREATE TABLE usuario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rol_id UUID REFERENCES rol(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    avatar_url TEXT,
    
    -- Para empleados/delivery
    codigo_empleado VARCHAR(50) UNIQUE,
    
    -- Billetera virtual
    saldo_billetera DECIMAL(10,2) DEFAULT 0.00,
    
    -- Estado
    activo BOOLEAN DEFAULT TRUE,
    email_verificado BOOLEAN DEFAULT FALSE,
    
    -- Seguridad
    ultimo_login TIMESTAMP,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- 5. direccion (direcciones de usuarios)
CREATE TABLE direccion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuario(id) ON DELETE CASCADE,
    tipo VARCHAR(20), -- casa, trabajo, otro
    nombre_referencia VARCHAR(100), -- "Casa de mamá"
    calle VARCHAR(255) NOT NULL,
    numero VARCHAR(20),
    zona VARCHAR(100),
    ciudad VARCHAR(100) NOT NULL,
    departamento VARCHAR(100),
    codigo_postal VARCHAR(20),
    referencia TEXT,
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    es_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÓDULO 2: CATÁLOGO DE PRODUCTOS
-- ========================================

-- 6. categoria
CREATE TABLE categoria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    imagen_url TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. marca
CREATE TABLE marca (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) UNIQUE NOT NULL,
    logo_url TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. talla
CREATE TABLE talla (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(20) UNIQUE NOT NULL, -- XS, S, M, L, XL, XXL
    orden INT, -- para ordenar
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9. prenda (productos)
CREATE TABLE prenda (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio_compra DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    marca_id UUID REFERENCES marca(id),
    
    -- Stock total (suma de todos los stock_prenda)
    stock_total INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    
    -- Atributos físicos
    peso DECIMAL(8,2), -- kg
    material VARCHAR(100),
    
    -- Imágenes
    imagen_principal TEXT,
    
    -- SEO y estadísticas
    vistas INT DEFAULT 0,
    ventas_totales INT DEFAULT 0,
    
    activo BOOLEAN DEFAULT TRUE,
    destacado BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- 10. prenda_categoria (N:N - una prenda puede estar en varias categorías)
CREATE TABLE prenda_categoria (
    prenda_id UUID REFERENCES prenda(id) ON DELETE CASCADE,
    categoria_id UUID REFERENCES categoria(id) ON DELETE CASCADE,
    PRIMARY KEY (prenda_id, categoria_id)
);

-- 11. stock_prenda (inventario por talla/color)
CREATE TABLE stock_prenda (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prenda_id UUID REFERENCES prenda(id) ON DELETE CASCADE,
    talla_id UUID REFERENCES talla(id),
    color VARCHAR(50) NOT NULL,
    codigo_color VARCHAR(7), -- hex #FF5733
    stock INT NOT NULL DEFAULT 0,
    ubicacion_almacen VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(prenda_id, talla_id, color)
);

-- 12. imagen_prenda (galería de imágenes)
CREATE TABLE imagen_prenda (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prenda_id UUID REFERENCES prenda(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    descripcion VARCHAR(200),
    orden INT DEFAULT 0,
    es_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÓDULO 3: PROMOCIONES
-- ========================================

-- 13. descuento
CREATE TABLE descuento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    codigo_promocional VARCHAR(50) UNIQUE,
    tipo VARCHAR(20) NOT NULL, -- porcentaje, monto_fijo
    valor DECIMAL(10,2) NOT NULL, -- 15 (si es %) o 50 (si es monto)
    
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    
    usos_maximos INT,
    usos_actuales INT DEFAULT 0,
    monto_minimo_compra DECIMAL(10,2),
    
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 14. descuento_prenda (qué productos aplican al descuento)
CREATE TABLE descuento_prenda (
    descuento_id UUID REFERENCES descuento(id) ON DELETE CASCADE,
    prenda_id UUID REFERENCES prenda(id) ON DELETE CASCADE,
    PRIMARY KEY (descuento_id, prenda_id)
);

-- ========================================
-- MÓDULO 4: VENTAS Y PEDIDOS
-- ========================================

-- 15. metodo_pago
CREATE TABLE metodo_pago (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- efectivo, tarjeta, billetera_virtual
    proveedor VARCHAR(50), -- stripe, paypal, null
    icono_url TEXT,
    comision_porcentaje DECIMAL(5,2) DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    orden INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 16. pedido (orden de compra - POS o E-COMMERCE)
CREATE TABLE pedido (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_pedido VARCHAR(50) UNIQUE NOT NULL, -- PED-2025-00001
    usuario_id UUID REFERENCES usuario(id),
    
    -- Tipo de venta
    tipo_venta VARCHAR(20) NOT NULL, -- presencial, online
    canal VARCHAR(20) NOT NULL, -- pos, web, mobile
    
    -- Estado
    estado VARCHAR(50) DEFAULT 'pendiente', 
    -- Estados: pendiente, confirmado, preparando, enviado, entregado, cancelado
    
    -- Montos
    subtotal DECIMAL(10,2) NOT NULL,
    descuento_total DECIMAL(10,2) DEFAULT 0,
    costo_envio DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    
    -- Pago
    metodo_pago_id UUID REFERENCES metodo_pago(id),
    estado_pago VARCHAR(50) DEFAULT 'pendiente', -- pendiente, pagado, fallido
    
    -- Envío (solo si es online)
    requiere_envio BOOLEAN DEFAULT FALSE,
    direccion_envio_id UUID REFERENCES direccion(id),
    
    -- Cliente (para ventas presenciales sin cuenta)
    cliente_nombre VARCHAR(200),
    cliente_telefono VARCHAR(20),
    cliente_email VARCHAR(255),
    
    -- Notas
    notas_cliente TEXT,
    notas_internas TEXT,
    
    -- Metadata
    ip_address VARCHAR(50),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 17. detalle_pedido (items del pedido)
CREATE TABLE detalle_pedido (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pedido_id UUID REFERENCES pedido(id) ON DELETE CASCADE,
    prenda_id UUID REFERENCES prenda(id),
    stock_prenda_id UUID REFERENCES stock_prenda(id), -- referencia exacta
    
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento_unitario DECIMAL(10,2) DEFAULT 0,
    subtotal DECIMAL(10,2) NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 18. historial_estado_pedido (trazabilidad)
CREATE TABLE historial_estado_pedido (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pedido_id UUID REFERENCES pedido(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50) NOT NULL,
    comentario TEXT,
    usuario_responsable_id UUID REFERENCES usuario(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 19. pago (registro de pagos - puede haber múltiples pagos por pedido)
CREATE TABLE pago (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pedido_id UUID REFERENCES pedido(id) ON DELETE CASCADE,
    metodo_pago_id UUID REFERENCES metodo_pago(id),
    
    monto DECIMAL(10,2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'completado', -- completado, fallido, reembolsado
    
    -- Para pagos con proveedor (Stripe/PayPal)
    referencia_externa VARCHAR(255), -- ID de transacción
    datos_proveedor JSONB, -- metadata del proveedor
    
    -- Para billetera virtual
    saldo_anterior DECIMAL(10,2),
    saldo_posterior DECIMAL(10,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÓDULO 5: ENVÍOS Y DELIVERY
-- ========================================

-- 20. agencia_delivery
CREATE TABLE agencia_delivery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(200),
    telefono VARCHAR(20),
    email VARCHAR(255),
    logo_url TEXT,
    costo_base DECIMAL(8,2) DEFAULT 0,
    tiempo_estimado_dias INT DEFAULT 3,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 21. envio (información de envío)
CREATE TABLE envio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pedido_id UUID REFERENCES pedido(id) ON DELETE CASCADE,
    agencia_delivery_id UUID REFERENCES agencia_delivery(id),
    personal_delivery_id UUID REFERENCES usuario(id), -- si es interno
    
    estado VARCHAR(50) DEFAULT 'pendiente',
    -- pendiente, recogido, en_transito, en_reparto, entregado, fallido
    
    codigo_seguimiento VARCHAR(100),
    metodo VARCHAR(50), -- agencia, delivery_propio
    
    -- Fechas
    fecha_envio TIMESTAMP,
    fecha_entrega_estimada TIMESTAMP,
    fecha_entrega_real TIMESTAMP,
    
    -- Costos
    costo_envio DECIMAL(8,2) DEFAULT 0,
    
    -- Intentos de entrega
    intentos_entrega INT DEFAULT 0,
    
    observacion TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÓDULO 6: RESEÑAS Y FAVORITOS
-- ========================================

-- 22. resena (reviews de productos)
CREATE TABLE resena (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuario(id) ON DELETE CASCADE,
    prenda_id UUID REFERENCES prenda(id) ON DELETE CASCADE,
    pedido_id UUID REFERENCES pedido(id), -- verificar compra
    
    calificacion INT NOT NULL CHECK (calificacion BETWEEN 1 AND 5),
    titulo VARCHAR(200),
    comentario TEXT,
    
    verificada BOOLEAN DEFAULT FALSE,
    
    -- Respuesta del vendedor
    respuesta_vendedor TEXT,
    fecha_respuesta TIMESTAMP,
    
    likes INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 23. favoritos (wishlist)
CREATE TABLE favoritos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuario(id) ON DELETE CASCADE,
    prenda_id UUID REFERENCES prenda(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(usuario_id, prenda_id)
);

-- ========================================
-- MÓDULO 7: CARRITO DE COMPRAS
-- ========================================

-- 24. carrito
CREATE TABLE carrito (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuario(id) ON DELETE CASCADE,
    sesion_id VARCHAR(255), -- para usuarios no registrados
    estado VARCHAR(20) DEFAULT 'activo', -- activo, abandonado, convertido
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(usuario_id)
);

-- 25. item_carrito
CREATE TABLE item_carrito (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    carrito_id UUID REFERENCES carrito(id) ON DELETE CASCADE,
    stock_prenda_id UUID REFERENCES stock_prenda(id) ON DELETE CASCADE,
    cantidad INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÓDULO 8: NOTIFICACIONES
-- ========================================

-- 26. notificacion
CREATE TABLE notificacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuario(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL, -- pedido, promocion, sistema
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    url_accion VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÓDULO 9: REPORTES DINÁMICOS
-- ========================================

-- 27. reporte_generado
CREATE TABLE reporte_generado (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuario(id),
    
    tipo_reporte VARCHAR(100) NOT NULL, -- ventas, productos, clientes
    prompt_original TEXT NOT NULL, -- comando del usuario
    parametros_interpretados JSONB, -- filtros extraídos
    
    query_ejecutado TEXT, -- SQL generado
    formato VARCHAR(20) NOT NULL, -- pdf, excel, json
    archivo_url TEXT,
    
    tiempo_generacion DECIMAL(8,3), -- segundos
    registros_procesados INT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÓDULO 10: INTELIGENCIA ARTIFICIAL
-- ========================================

-- 28. prediccion_ventas
CREATE TABLE prediccion_ventas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    fecha_prediccion TIMESTAMP DEFAULT NOW(),
    periodo VARCHAR(20) NOT NULL, -- dia, semana, mes
    fecha_inicio_periodo DATE NOT NULL,
    fecha_fin_periodo DATE NOT NULL,
    
    -- Segmentación
    categoria_id UUID REFERENCES categoria(id),
    prenda_id UUID REFERENCES prenda(id),
    
    -- Predicción
    ventas_predichas DECIMAL(10,2) NOT NULL,
    confianza DECIMAL(5,4), -- 0.9542
    
    -- Modelo
    modelo_version VARCHAR(50),
    parametros JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 29. entrenamiento_modelo
CREATE TABLE entrenamiento_modelo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    fecha_entrenamiento TIMESTAMP DEFAULT NOW(),
    tipo_modelo VARCHAR(50) NOT NULL, -- random_forest_regressor
    
    -- Datos de entrenamiento
    registros_entrenamiento INT NOT NULL,
    fecha_inicio_datos DATE,
    fecha_fin_datos DATE,
    
    -- Métricas
    accuracy DECIMAL(5,4),
    mse DECIMAL(12,4), -- Mean Squared Error
    mae DECIMAL(12,4), -- Mean Absolute Error
    r2_score DECIMAL(5,4), -- R² Score
    
    -- Configuración
    parametros JSONB,
    features_utilizados JSONB, -- columnas usadas
    
    -- Archivo
    archivo_modelo VARCHAR(255), -- ruta al .pkl
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- MÓDULO 11: AUDITORÍA Y LOGS
-- ========================================

-- 30. auditoria (logs del sistema)
CREATE TABLE auditoria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuario(id),
    
    accion VARCHAR(100) NOT NULL, -- crear_pedido, actualizar_stock, etc
    entidad VARCHAR(100) NOT NULL, -- pedido, prenda, usuario
    entidad_id UUID,
    
    cambios JSONB, -- before/after
    
    ip_address VARCHAR(50),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ========================================

-- Usuarios
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_usuario_rol ON usuario(rol_id);
CREATE INDEX idx_usuario_activo ON usuario(activo);

-- Productos
CREATE INDEX idx_prenda_sku ON prenda(sku);
CREATE INDEX idx_prenda_activo ON prenda(activo);
CREATE INDEX idx_prenda_destacado ON prenda(destacado);
CREATE INDEX idx_stock_prenda_color ON stock_prenda(prenda_id, color);

-- Pedidos
CREATE INDEX idx_pedido_usuario ON pedido(usuario_id);
CREATE INDEX idx_pedido_estado ON pedido(estado);
CREATE INDEX idx_pedido_fecha ON pedido(created_at DESC);
CREATE INDEX idx_pedido_numero ON pedido(numero_pedido);

-- Envíos
CREATE INDEX idx_envio_pedido ON envio(pedido_id);
CREATE INDEX idx_envio_estado ON envio(estado);

-- Reportes y Analytics
CREATE INDEX idx_reporte_usuario ON reporte_generado(usuario_id);
CREATE INDEX idx_prediccion_periodo ON prediccion_ventas(periodo, fecha_inicio_periodo);

-- Auditoría
CREATE INDEX idx_auditoria_usuario ON auditoria(usuario_id);
CREATE INDEX idx_auditoria_fecha ON auditoria(created_at DESC);
```

---

## 📊 DIAGRAMA ER FINAL
```
┌─────────────────────────────────────────────────────────────────┐
│                    MÓDULO AUTENTICACIÓN                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────┐       ┌─────────┐       ┌──────────┐              │
│   │ ROL  │◄──────│PERMISO_ │──────►│ PERMISO  │              │
│   └──┬───┘       │   ROL   │       └──────────┘              │
│      │           └─────────┘                                   │
│      │                                                          │
│      ▼                                                          │
│   ┌────────┐           ┌───────────┐                          │
│   │USUARIO │───────────│ DIRECCION │                          │
│   └────┬───┘           └───────────┘                          │
│        │                                                        │
└────────┼────────────────────────────────────────────────────────┘
         │
         │
┌────────┼────────────────────────────────────────────────────────┐
│        │            MÓDULO CATÁLOGO                             │
├────────┼────────────────────────────────────────────────────────┤
│        │                                                         │
│        │    ┌───────────┐                                       │
│        │    │ CATEGORIA │                                       │
│        │    └─────┬─────┘                                       │
│        │          │                                             │
│        │          ▼                                             │
│        │    ┌──────────────┐                                   │
│        │    │  PRENDA_     │                                   │
│        │    │  CATEGORIA   │                                   │
│        │    └──────┬───────┘                                   │
│        │           │                                            │
│        │           ▼                                            │
│        │    ┌────────────┐      ┌────────┐                    │
│        │    │   PRENDA   │◄─────│ MARCA  │                    │
│        │    └──┬──┬──┬──┘      └────────┘                    │
│        │       │  │  │                                         │
│        │       │  │  └──────────┐                             │
│        │       │  │             │                              │
│        │       │  ▼             ▼                              │
│        │       │ ┌─────────────────┐  ┌──────────────┐       │
│        │       │ │  STOCK_PRENDA   │──│    TALLA     │       │
│        │       │ └─────────────────┘  └──────────────┘       │
│        │       │                                               │
│        │       ▼                                               │
│        │    ┌─────────────┐                                   │
│        │    │IMAGEN_PRENDA│                                   │
│        │    └─────────────┘                                   │
│        │                                                        │
│        ├────────► ┌───────────┐                               │
│        │          │ FAVORITOS │                               │
│        │          └───────────┘                               │
│        │                                                        │
└────────┼────────────────────────────────────────────────────────┘
         │
         │
┌────────┼────────────────────────────────────────────────────────┐
│        │            MÓDULO PROMOCIONES                          │
├────────┼────────────────────────────────────────────────────────┤
│        │                                                         │
│        │    ┌────────────┐       ┌──────────────┐             │
│        │    │ DESCUENTO  │───────│  DESCUENTO_  │             │
│        │    └────────────┘       │   PRENDA     │             │
│        │                         └──────────────┘             │
│        │                                                        │
└────────┼────────────────────────────────────────────────────────┘
         │
         │
┌────────┼────────────────────────────────────────────────────────┐
│        │         MÓDULO VENTAS Y PEDIDOS                        │
├────────┼────────────────────────────────────────────────────────┤
│        │                                                         │
│        │    ┌──────────────┐                                   │
│        └───►│   PEDIDO     │◄───┌───────────────┐             │
│             └──┬─┬─┬───┬───┘    │ METODO_PAGO   │             │
│                │ │ │   │        └───────────────┘             │
│                │ │ │   │                                        │
│                │ │ │   └────► ┌──────┐                        │
│                │ │ │          │ PAGO │                        │
│                │ │ │          └──────┘                        │
│                │ │ │                                            │
│                │ │ └────────► ┌─────────────────┐             │
│                │ │            │ HISTORIAL_ESTADO │             │
│                │ │            │     _PEDIDO      │             │
│                │ │            └─────────────────┘             │
│                │ │                                              │
│                │ └──────────► ┌──────────────┐                │
│                │              │DETALLE_PEDIDO│                │
│                │              └──────────────┘                │
│                │                                                │
│                └────────────► ┌────────┐                      │
│                               │ ENVIO  │                      │
│                               └───┬────┘                      │
│                                   │                            │
│                                   ▼                            │
│                           ┌──────────────────┐                │
│                           │ AGENCIA_DELIVERY │                │
│                           └──────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                MÓDULO CARRITO Y RESEÑAS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐        ┌──────────────┐                         │
│   │CARRITO  │───────►│ ITEM_CARRITO │                         │
│   └─────────┘        └──────────────┘                         │
│                                                                 │
│   ┌─────────┐                                                  │
│   │ RESENA  │                                                  │
│   └─────────┘                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│           MÓDULO INTELIGENCIA ARTIFICIAL                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────┐      ┌──────────────────────┐          │
│   │PREDICCION_VENTAS │      │ENTRENAMIENTO_MODELO  │          │
│   └──────────────────┘      └──────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│           MÓDULO REPORTES Y AUDITORÍA                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────┐      ┌────────────┐                    │
│   │REPORTE_GENERADO  │      │ AUDITORIA  │                    │
│   └──────────────────┘      └────────────┘                    │
│                                                                 │
│   ┌──────────────────┐                                         │
│   │  NOTIFICACION    │                                         │
│   └──────────────────┘                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘