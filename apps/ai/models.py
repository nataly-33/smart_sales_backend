from django.db import models
from apps.core.models import BaseModel


class MLModel(BaseModel):
    """
    Modelo para guardar historial de entrenamientos del modelo de Machine Learning
    """
    nombre = models.CharField(max_length=200, verbose_name='Nombre del modelo')
    version = models.CharField(max_length=50, verbose_name='Versión')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    
    # Archivos del modelo
    archivo_modelo = models.CharField(max_length=500, verbose_name='Ruta del archivo del modelo')
    
    # Métricas de rendimiento
    mae = models.FloatField(null=True, blank=True, verbose_name='Mean Absolute Error')
    mse = models.FloatField(null=True, blank=True, verbose_name='Mean Squared Error')
    rmse = models.FloatField(null=True, blank=True, verbose_name='Root Mean Squared Error')
    r2_score = models.FloatField(null=True, blank=True, verbose_name='R² Score')
    
    # Información de entrenamiento
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de entrenamiento')
    registros_entrenamiento = models.IntegerField(verbose_name='Registros usados en entrenamiento')
    features_utilizadas = models.JSONField(default=list, verbose_name='Features utilizadas')
    
    # Hiperparámetros
    hiperparametros = models.JSONField(default=dict, verbose_name='Hiperparámetros')
    
    # Estado
    activo = models.BooleanField(default=False, verbose_name='Modelo activo')
    notas = models.TextField(blank=True, verbose_name='Notas adicionales')
    
    class Meta:
        db_table = 'ml_model'
        verbose_name = 'Modelo ML'
        verbose_name_plural = 'Modelos ML'
        ordering = ['-fecha_entrenamiento']
        indexes = [
            models.Index(fields=['activo', '-fecha_entrenamiento']),
            models.Index(fields=['version']),
        ]
    
    def __str__(self):
        return f"{self.nombre} v{self.version} - {'Activo' if self.activo else 'Inactivo'}"
    
    def activar(self):
        """Activa este modelo y desactiva los demás"""
        MLModel.objects.filter(activo=True).update(activo=False)
        self.activo = True
        self.save()


class PrediccionVentas(BaseModel):
    """
    Registro de predicciones realizadas por el modelo
    """
    modelo = models.ForeignKey(
        MLModel,
        on_delete=models.PROTECT,
        related_name='predicciones',
        verbose_name='Modelo usado'
    )
    
    # Datos de la predicción
    fecha_prediccion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de la predicción')
    periodo_predicho = models.CharField(max_length=50, verbose_name='Período predicho (ej: 2025-11)')
    
    # Resultados
    ventas_predichas = models.FloatField(verbose_name='Ventas predichas')
    categoria = models.CharField(max_length=100, blank=True, verbose_name='Categoría (si aplica)')
    producto_id = models.IntegerField(null=True, blank=True, verbose_name='ID Producto (si aplica)')
    
    # Features utilizadas en la predicción
    features_input = models.JSONField(default=dict, verbose_name='Features de entrada')
    
    # Para validación posterior
    ventas_reales = models.FloatField(null=True, blank=True, verbose_name='Ventas reales (para comparar)')
    error = models.FloatField(null=True, blank=True, verbose_name='Error de predicción')
    
    class Meta:
        db_table = 'prediccion_ventas'
        verbose_name = 'Predicción de Ventas'
        verbose_name_plural = 'Predicciones de Ventas'
        ordering = ['-fecha_prediccion']
        indexes = [
            models.Index(fields=['-fecha_prediccion']),
            models.Index(fields=['periodo_predicho']),
            models.Index(fields=['categoria']),
        ]
    
    def __str__(self):
        return f"Predicción {self.periodo_predicho}: {self.ventas_predichas:.2f}"
    
    def calcular_error(self):
        """Calcula el error si ya tenemos ventas reales"""
        if self.ventas_reales is not None:
            self.error = abs(self.ventas_predichas - self.ventas_reales)
            self.save()
