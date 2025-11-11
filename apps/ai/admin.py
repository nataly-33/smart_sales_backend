from django.contrib import admin
from .models import MLModel, PrediccionVentas


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'version', 'activo', 'fecha_entrenamiento', 'r2_score', 'mae', 'registros_entrenamiento']
    list_filter = ['activo', 'fecha_entrenamiento']
    search_fields = ['nombre', 'version', 'descripcion']
    readonly_fields = ['fecha_entrenamiento', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'version', 'descripcion', 'activo')
        }),
        ('Archivos', {
            'fields': ('archivo_modelo',)
        }),
        ('Métricas de rendimiento', {
            'fields': ('mae', 'mse', 'rmse', 'r2_score')
        }),
        ('Entrenamiento', {
            'fields': ('registros_entrenamiento', 'features_utilizadas', 'hiperparametros')
        }),
        ('Metadata', {
            'fields': ('fecha_entrenamiento', 'notas', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_modelo']
    
    def activar_modelo(self, request, queryset):
        """Acción para activar un modelo seleccionado"""
        if queryset.count() > 1:
            self.message_user(request, "Solo puedes activar un modelo a la vez", level='error')
            return
        
        modelo = queryset.first()
        modelo.activar()
        self.message_user(request, f"Modelo {modelo.nombre} v{modelo.version} activado correctamente")
    
    activar_modelo.short_description = "Activar modelo seleccionado"


@admin.register(PrediccionVentas)
class PrediccionVentasAdmin(admin.ModelAdmin):
    list_display = ['periodo_predicho', 'categoria', 'ventas_predichas', 'ventas_reales', 'error', 'fecha_prediccion']
    list_filter = ['categoria', 'fecha_prediccion']
    search_fields = ['periodo_predicho', 'categoria']
    readonly_fields = ['fecha_prediccion', 'error', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Predicción', {
            'fields': ('modelo', 'periodo_predicho', 'categoria', 'producto_id', 'ventas_predichas')
        }),
        ('Features', {
            'fields': ('features_input',),
            'classes': ('collapse',)
        }),
        ('Validación', {
            'fields': ('ventas_reales', 'error')
        }),
        ('Metadata', {
            'fields': ('fecha_prediccion', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
