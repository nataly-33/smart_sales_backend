"""
Serializers para la API de Reportes
"""

from rest_framework import serializers


class GenerateReportSerializer(serializers.Serializer):
    """Serializer para generar reportes desde prompts"""
    prompt = serializers.CharField(
        required=True,
        help_text="Comando en lenguaje natural para generar el reporte. "
                  "Ejemplo: 'Reporte de ventas de septiembre en PDF'"
    )
    format = serializers.ChoiceField(
        choices=['pdf', 'excel', 'csv'],
        required=False,
        allow_null=True,
        help_text="Formato del reporte (sobreescribe el formato mencionado en el prompt)"
    )

    def validate_prompt(self, value):
        """Validar que el prompt no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El prompt no puede estar vacío")
        return value.strip()


class PredefinedReportSerializer(serializers.Serializer):
    """Serializer para reportes predefinidos"""
    report_type = serializers.ChoiceField(
        choices=['ventas', 'productos', 'clientes', 'analytics'],
        required=True,
        help_text="Tipo de reporte a generar"
    )
    format = serializers.ChoiceField(
        choices=['pdf', 'excel', 'csv'],
        default='pdf',
        help_text="Formato del reporte"
    )
    filters = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Filtros adicionales en formato JSON"
    )


class AnalyticsSerializer(serializers.Serializer):
    """Serializer para parámetros de analytics"""
    months = serializers.IntegerField(
        default=12,
        min_value=1,
        max_value=24,
        help_text="Número de meses a incluir en gráficos históricos"
    )
    days = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=90,
        help_text="Número de días para actividad reciente"
    )
