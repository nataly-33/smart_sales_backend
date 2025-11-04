from rest_framework import serializers
from .models import Pedido, DetallePedido, Pago, MetodoPago, HistorialEstadoPedido
from apps.products.serializers import PrendaListSerializer, TallaSerializer
from apps.customers.serializers import DireccionSerializer
from apps.accounts.serializers import UserSerializer
from apps.core.constants import ESTADOS_PEDIDO


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo', 'requiere_procesador']


class DetallePedidoSerializer(serializers.ModelSerializer):
    prenda_detalle = PrendaListSerializer(source='prenda', read_only=True)
    talla_detalle = TallaSerializer(source='talla', read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = [
            'id', 'prenda', 'prenda_detalle', 'talla', 'talla_detalle',
            'cantidad', 'precio_unitario', 'subtotal', 'producto_snapshot'
        ]
        read_only_fields = ['subtotal', 'producto_snapshot']


class PagoSerializer(serializers.ModelSerializer):
    metodo_pago_detalle = MetodoPagoSerializer(source='metodo_pago', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id', 'metodo_pago', 'metodo_pago_detalle', 'monto', 'estado',
            'transaction_id', 'created_at'
        ]


class HistorialEstadoPedidoSerializer(serializers.ModelSerializer):
    usuario_cambio_detalle = UserSerializer(source='usuario_cambio', read_only=True)
    
    class Meta:
        model = HistorialEstadoPedido
        fields = [
            'id', 'estado_anterior', 'estado_nuevo', 'usuario_cambio',
            'usuario_cambio_detalle', 'notas', 'created_at'
        ]


class PedidoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'numero_pedido', 'estado', 'total', 'total_items',
            'created_at', 'updated_at'
        ]


class PedidoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles"""
    usuario_detalle = UserSerializer(source='usuario', read_only=True)
    direccion_envio_detalle = DireccionSerializer(source='direccion_envio', read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    pagos = PagoSerializer(many=True, read_only=True)
    historial_estados = HistorialEstadoPedidoSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    puede_cancelar = serializers.ReadOnlyField()
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'numero_pedido', 'usuario', 'usuario_detalle',
            'direccion_envio', 'direccion_envio_detalle', 'direccion_snapshot',
            'subtotal', 'descuento', 'costo_envio', 'total', 'estado',
            'notas_cliente', 'notas_internas', 'detalles', 'pagos',
            'historial_estados', 'total_items', 'puede_cancelar',
            'metadata', 'created_at', 'updated_at'
        ]


class CheckoutSerializer(serializers.Serializer):
    """Serializer para el proceso de checkout"""
    direccion_envio_id = serializers.UUIDField()
    metodo_pago = serializers.ChoiceField(choices=['efectivo', 'tarjeta', 'paypal', 'billetera'])
    notas_cliente = serializers.CharField(required=False, allow_blank=True)
    
    # Campos opcionales para pagos con tarjeta
    payment_method_id = serializers.CharField(required=False, allow_blank=True)  # Para Stripe
    paypal_order_id = serializers.CharField(required=False, allow_blank=True)  # Para PayPal
    
    def validate_direccion_envio_id(self, value):
        from apps.customers.models import Direccion
        
        try:
            direccion = Direccion.objects.get(
                id=value,
                usuario=self.context['request'].user,
                deleted_at__isnull=True
            )
            return direccion
        except Direccion.DoesNotExist:
            raise serializers.ValidationError("Dirección no encontrada")
    
    def validate(self, data):
        metodo_pago = data.get('metodo_pago')
        
        # Validar campos requeridos según el método de pago
        if metodo_pago == 'tarjeta' and not data.get('payment_method_id'):
            raise serializers.ValidationError({
                'payment_method_id': 'Este campo es requerido para pagos con tarjeta'
            })
        
        if metodo_pago == 'paypal' and not data.get('paypal_order_id'):
            raise serializers.ValidationError({
                'paypal_order_id': 'Este campo es requerido para pagos con PayPal'
            })
        
        return data


class CambiarEstadoPedidoSerializer(serializers.Serializer):
    """Serializer para cambiar estado del pedido"""
    nuevo_estado = serializers.ChoiceField(choices=[estado[0] for estado in ESTADOS_PEDIDO])
    notas = serializers.CharField(required=False, allow_blank=True)