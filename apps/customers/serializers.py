from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Direccion, Favoritos
from apps.accounts.serializers import UserSerializer
from apps.products.serializers import PrendaListSerializer

User = get_user_model()


class DireccionSerializer(serializers.ModelSerializer):
    direccion_completa = serializers.ReadOnlyField()
    
    class Meta:
        model = Direccion
        fields = [
            'id', 'nombre_completo', 'telefono', 
            'direccion_linea1', 'direccion_linea2',
            'ciudad', 'departamento', 'codigo_postal', 'pais',
            'referencia', 'es_principal', 'activa',
            'direccion_completa', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Asignar el usuario del contexto
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer para el perfil del cliente"""
    direccion_principal = serializers.SerializerMethodField()
    total_compras = serializers.SerializerMethodField()
    total_favoritos = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'nombre', 'apellido', 'nombre_completo',
            'telefono', 'foto_perfil', 'saldo_billetera',
            'email_verificado', 'direccion_principal',
            'total_compras', 'total_favoritos', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'saldo_billetera', 'email_verificado', 'created_at']
    
    def get_direccion_principal(self, obj):
        direccion = obj.direcciones.filter(es_principal=True).first()
        if direccion:
            return DireccionSerializer(direccion).data
        return None
    
    def get_total_compras(self, obj):
        # TODO: Implementar cuando tengamos el modelo de Pedido
        return 0
    
    def get_total_favoritos(self, obj):
        return obj.favoritos.filter(deleted_at__isnull=True).count()


class FavoritosSerializer(serializers.ModelSerializer):
    prenda_detalle = PrendaListSerializer(source='prenda', read_only=True)
    
    class Meta:
        model = Favoritos
        fields = ['id', 'prenda', 'prenda_detalle', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class WalletRechargeSerializer(serializers.Serializer):
    """Serializer para recargar billetera"""
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    metodo_pago = serializers.ChoiceField(choices=['tarjeta', 'transferencia'])
    
    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        if value > 10000:
            raise serializers.ValidationError("El monto máximo es 10,000")
        return value