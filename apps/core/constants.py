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

ROLES = ['Admin', 'Empleado', 'Cliente', 'Delivery']

ESTADOS_PEDIDO = [
    ('pendiente', 'Pendiente de pago'),
    ('pago_recibido', 'Pago recibido'),
    ('confirmado', 'Confirmado'),
    ('preparando', 'Preparando'),
    ('enviado', 'Enviado'),
    ('entregado', 'Entregado'),
    ('cancelado', 'Cancelado'),
    ('reembolsado', 'Reembolsado'),
]

METODOS_PAGO = [
    ('efectivo', 'Efectivo'),
    ('tarjeta', 'Tarjeta'),
    ('paypal', 'PayPal'),
    ('billetera', 'Billetera Virtual'),
]

ESTADOS_PAGO = [
    ('pendiente', 'Pendiente'),
    ('procesando', 'Procesando'),
    ('completado', 'Completado'),
    ('fallido', 'Fallido'),
    ('reembolsado', 'Reembolsado'),
]

TALLAS = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

COLORES = [
    'Rojo', 'Azul', 'Verde', 'Amarillo', 'Negro', 'Celeste',
    'Blanco', 'Gris', 'Rosa', 'Morado', 'Naranja', 'Lavanda'
]