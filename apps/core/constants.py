"""Constantes globales del sistema"""

# Módulos del sistema para permisos
PERMISSIONS = {
    'usuarios': ['crear', 'leer', 'actualizar', 'eliminar'],
    'roles': ['crear', 'leer', 'actualizar', 'eliminar'],
    'productos': ['crear', 'leer', 'actualizar', 'eliminar'],
    'categorias': ['crear', 'leer', 'actualizar', 'eliminar'],
    'marcas': ['crear', 'leer', 'actualizar', 'eliminar'],
    'pedidos': ['crear', 'leer', 'actualizar', 'eliminar', 'aprobar'],
    'ventas': ['crear', 'leer', 'cancelar'],
    'clientes': ['crear', 'leer', 'actualizar'],
    'envios': ['crear', 'leer', 'actualizar', 'entregar'],
    'reportes': ['crear', 'leer', 'exportar'],
    'descuentos': ['crear', 'leer', 'actualizar', 'eliminar'],
    'dashboard': ['leer'],
}

# Roles del sistema
ROLES = ['Admin', 'Empleado', 'Cliente', 'Delivery']

# Estados de pedido
ESTADOS_PEDIDO = [
    ('pendiente', 'Pendiente'),
    ('confirmado', 'Confirmado'),
    ('preparando', 'Preparando'),
    ('enviado', 'Enviado'),
    ('entregado', 'Entregado'),
    ('cancelado', 'Cancelado'),
]

# Métodos de pago
METODOS_PAGO = [
    ('efectivo', 'Efectivo'),
    ('tarjeta', 'Tarjeta'),
    ('billetera', 'Billetera Virtual'),
]

# Tallas disponibles
TALLAS = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

# Colores disponibles
COLORES = [
    'Rojo', 'Azul', 'Verde', 'Amarillo', 'Negro', 'Celeste',
    'Blanco', 'Gris', 'Rosa', 'Morado', 'Naranja', 'Lavanda'
]