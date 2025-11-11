from rest_framework import serializers
from .models import MLModel, PrediccionVentas


class MLModelSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ML"""
    
    class Meta:
        model = MLModel
        fields = [
            'id',
            'nombre',
            'version',
            'descripcion',
            'mae',
            'mse',
            'rmse',
            'r2_score',
            'fecha_entrenamiento',
            'registros_entrenamiento',
            'features_utilizadas',
            'hiperparametros',
            'activo',
            'notas'
        ]
        read_only_fields = ['fecha_entrenamiento']


class MLModelListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para lista de modelos"""
    
    class Meta:
        model = MLModel
        fields = ['id', 'nombre', 'version', 'r2_score', 'fecha_entrenamiento', 'activo']


class PrediccionVentasSerializer(serializers.ModelSerializer):
    """Serializer para predicciones de ventas"""
    modelo_version = serializers.CharField(source='modelo.version', read_only=True)
    
    class Meta:
        model = PrediccionVentas
        fields = [
            'id',
            'modelo',
            'modelo_version',
            'fecha_prediccion',
            'periodo_predicho',
            'ventas_predichas',
            'categoria',
            'producto_id',
            'features_input',
            'ventas_reales',
            'error'
        ]
        read_only_fields = ['fecha_prediccion', 'error']


class PredictRequestSerializer(serializers.Serializer):
    """Serializer para solicitud de predicción"""
    categoria = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    n_months = serializers.IntegerField(default=1, min_value=1, max_value=12)


class TrainModelSerializer(serializers.Serializer):
    """Serializer para solicitud de entrenamiento"""
    n_estimators = serializers.IntegerField(default=100, min_value=10, max_value=500)
    max_depth = serializers.IntegerField(default=10, min_value=3, max_value=50)
    test_size = serializers.FloatField(default=0.2, min_value=0.1, max_value=0.4)


class DashboardResponseSerializer(serializers.Serializer):
    """Serializer para respuesta del dashboard"""
    historical = serializers.ListField()
    predictions = serializers.ListField()
    predictions_by_category = serializers.ListField()
    top_products = serializers.ListField()
    category_sales = serializers.ListField()
    model_info = serializers.DictField()
