from django.contrib import admin
from .models import Categoria, Marca, Talla, Prenda, StockPrenda, ImagenPrenda


class ImagenPrendaInline(admin.TabularInline):
    model = ImagenPrenda
    extra = 1
    fields = ['imagen', 'es_principal', 'orden', 'alt_text']


class StockPrendaInline(admin.TabularInline):
    model = StockPrenda
    extra = 1
    fields = ['talla', 'cantidad', 'stock_minimo']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa', 'created_at']
    list_filter = ['activa']
    search_fields = ['nombre']
    prepopulated_fields = {}


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa', 'created_at']
    list_filter = ['activa']
    search_fields = ['nombre']


@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden']
    ordering = ['orden']


@admin.register(Prenda)
class PrendaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'marca', 'precio', 'color', 'stock_total', 'activa', 'destacada', 'created_at']
    list_filter = ['activa', 'destacada', 'es_novedad', 'marca', 'categorias']
    search_fields = ['nombre', 'descripcion', 'color']
    filter_horizontal = ['categorias', 'tallas_disponibles']
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenPrendaInline, StockPrendaInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'precio', 'marca', 'slug')
        }),
        ('Categorización', {
            'fields': ('categorias', 'tallas_disponibles', 'color', 'material')
        }),
        ('Estado', {
            'fields': ('activa', 'destacada', 'es_novedad')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockPrenda)
class StockPrendaAdmin(admin.ModelAdmin):
    list_display = ['prenda', 'talla', 'cantidad', 'stock_minimo', 'alerta_stock_bajo']
    list_filter = ['talla']
    search_fields = ['prenda__nombre']
    
    def alerta_stock_bajo(self, obj):
        return obj.alerta_stock_bajo
    alerta_stock_bajo.boolean = True
    alerta_stock_bajo.short_description = 'Stock bajo'


@admin.register(ImagenPrenda)
class ImagenPrendaAdmin(admin.ModelAdmin):
    list_display = ['prenda', 'es_principal', 'orden', 'created_at']
    list_filter = ['es_principal']
    search_fields = ['prenda__nombre']