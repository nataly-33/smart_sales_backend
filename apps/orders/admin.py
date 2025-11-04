from django.contrib import admin
from .models import MetodoPago, Pedido, DetallePedido, Pago, HistorialEstadoPedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ['precio_unitario', 'subtotal', 'producto_snapshot']
    fields = ['prenda', 'talla', 'cantidad', 'precio_unitario', 'subtotal']


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    readonly_fields = ['created_at']
    fields = ['metodo_pago', 'monto', 'estado', 'transaction_id', 'created_at']


class HistorialEstadoInline(admin.TabularInline):
    model = HistorialEstadoPedido
    extra = 0
    readonly_fields = ['created_at']
    fields = ['estado_anterior', 'estado_nuevo', 'usuario_cambio', 'notas', 'created_at']


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'activo', 'requiere_procesador', 'created_at']
    list_filter = ['activo', 'requiere_procesador']
    search_fields = ['nombre', 'codigo']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_pedido', 'usuario', 'estado', 'total', 
        'total_items', 'created_at'
    ]
    list_filter = ['estado', 'created_at']
    search_fields = ['numero_pedido', 'usuario__email', 'usuario__nombre']
    readonly_fields = [
        'numero_pedido', 'subtotal', 'total', 'direccion_snapshot',
        'total_items', 'puede_cancelar', 'created_at', 'updated_at'
    ]
    inlines = [DetallePedidoInline, PagoInline, HistorialEstadoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario', 'estado')
        }),
        ('Dirección de Envío', {
            'fields': ('direccion_envio', 'direccion_snapshot')
        }),
        ('Montos', {
            'fields': ('subtotal', 'descuento', 'costo_envio', 'total')
        }),
        ('Notas', {
            'fields': ('notas_cliente', 'notas_internas')
        }),
        ('Información Adicional', {
            'fields': ('total_items', 'puede_cancelar', 'metadata', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Total Items'


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'prenda', 'talla', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['pedido__numero_pedido', 'prenda__nombre']
    readonly_fields = ['subtotal', 'producto_snapshot', 'created_at']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'metodo_pago', 'monto', 'estado', 'transaction_id', 'created_at']
    list_filter = ['estado', 'metodo_pago', 'created_at']
    search_fields = ['pedido__numero_pedido', 'transaction_id', 'stripe_payment_intent_id', 'paypal_order_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HistorialEstadoPedido)
class HistorialEstadoPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'estado_anterior', 'estado_nuevo', 'usuario_cambio', 'created_at']
    list_filter = ['estado_nuevo', 'created_at']
    search_fields = ['pedido__numero_pedido']
    readonly_fields = ['created_at']