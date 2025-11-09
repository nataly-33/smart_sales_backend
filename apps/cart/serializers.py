from rest_framework import serializers
from .models import Carrito, ItemCarrito
from apps.products.serializers import PrendaListSerializer, TallaSerializer
from apps.products.models import StockPrenda


class ItemCarritoSerializer(serializers.ModelSerializer):
    prenda_detalle = PrendaListSerializer(source='prenda', read_only=True)
    talla_detalle = TallaSerializer(source='talla', read_only=True)
    subtotal = serializers.SerializerMethodField()
    stock_disponible = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemCarrito
        fields = [
            'id', 'prenda', 'prenda_detalle', 'talla', 'talla_detalle',
            'cantidad', 'precio_unitario', 'subtotal', 'stock_disponible',
            'created_at'
        ]
        read_only_fields = ['id', 'precio_unitario', 'created_at']
    
    def get_subtotal(self, obj):
        return obj.subtotal
    
    def get_stock_disponible(self, obj):
        stock = StockPrenda.objects.filter(
            prenda=obj.prenda,
            talla=obj.talla
        ).first()
        return stock.cantidad if stock else 0
    
    def validate(self, data):
        prenda = data.get('prenda')
        talla = data.get('talla')
        cantidad = data.get('cantidad', 1)
        
        # Verificar que la prenda esté activa
        if not prenda.activa:
            raise serializers.ValidationError("Este producto no está disponible")
        
        # Verificar que la talla esté disponible para esta prenda
        if not prenda.tallas_disponibles.filter(id=talla.id).exists():
            raise serializers.ValidationError("Esta talla no está disponible para este producto")
        
        # Verificar stock
        stock = StockPrenda.objects.filter(prenda=prenda, talla=talla).first()
        if not stock or stock.cantidad < cantidad:
            disponible = stock.cantidad if stock else 0
            raise serializers.ValidationError(
                f"Stock insuficiente. Solo hay {disponible} unidades disponibles"
            )
        
        return data


class CarritoSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    cantidad_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'items', 'total_items', 'cantidad_items', 'subtotal', 'total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'usuario', 'created_at', 'updated_at']
    
    def get_items(self, obj):
        """Obtener solo los items activos (no eliminados) del carrito"""
        items_activos = obj.items.filter(deleted_at__isnull=True)
        return ItemCarritoSerializer(items_activos, many=True, context=self.context).data
    
    def get_total_items(self, obj):
        return obj.total_items
    
    def get_cantidad_items(self, obj):
        return obj.cantidad_total_items
    
    def get_subtotal(self, obj):
        return obj.subtotal
    
    def get_total(self, obj):
        return obj.total


class AgregarItemCarritoSerializer(serializers.Serializer):
    """Serializer para agregar items al carrito"""
    prenda = serializers.UUIDField()
    talla = serializers.UUIDField()
    cantidad = serializers.IntegerField(min_value=1, default=1)
    
    def validate(self, data):
        from apps.products.models import Prenda, Talla
        
        # Verificar que la prenda existe
        try:
            prenda = Prenda.objects.get(id=data['prenda'], activa=True, deleted_at__isnull=True)
            data['prenda_obj'] = prenda
        except Prenda.DoesNotExist:
            raise serializers.ValidationError({"prenda": "Producto no encontrado o no disponible"})
        
        # Verificar que la talla existe
        try:
            talla = Talla.objects.get(id=data['talla'], deleted_at__isnull=True)
            data['talla_obj'] = talla
        except Talla.DoesNotExist:
            raise serializers.ValidationError({"talla": "Talla no encontrada"})
        
        # Verificar que la talla está disponible para esta prenda
        if not prenda.tallas_disponibles.filter(id=talla.id).exists():
            raise serializers.ValidationError({"talla": "Esta talla no está disponible para este producto"})
        
        # Verificar stock
        stock = StockPrenda.objects.filter(prenda=prenda, talla=talla).first()
        if not stock or stock.cantidad < data['cantidad']:
            disponible = stock.cantidad if stock else 0
            raise serializers.ValidationError({
                "cantidad": f"Stock insuficiente. Solo hay {disponible} unidades disponibles"
            })
        
        return data


class ActualizarCantidadSerializer(serializers.Serializer):
    """Serializer para actualizar cantidad de un item"""
    cantidad = serializers.IntegerField(min_value=1)
    
    def validate_cantidad(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1")
        if value > 50:
            raise serializers.ValidationError("La cantidad máxima es 50")
        return value