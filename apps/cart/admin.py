from django.contrib import admin
from .models import Carrito, ItemCarrito


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ['precio_unitario', 'subtotal', 'created_at']
    fields = ['prenda', 'talla', 'cantidad', 'precio_unitario', 'subtotal']
    
    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Subtotal'


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'total_items', 'subtotal', 'total', 'created_at']
    search_fields = ['usuario__email', 'usuario__nombre']
    readonly_fields = ['total_items', 'subtotal', 'total', 'created_at', 'updated_at']
    inlines = [ItemCarritoInline]
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Totales', {
            'fields': ('total_items', 'subtotal', 'total')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['carrito', 'prenda', 'talla', 'cantidad', 'precio_unitario', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['carrito__usuario__email', 'prenda__nombre']
    readonly_fields = ['precio_unitario', 'subtotal', 'created_at', 'updated_at']
    
    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Subtotal'