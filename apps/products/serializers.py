from rest_framework import serializers
from .models import Categoria, Marca, Talla, Prenda, StockPrenda, ImagenPrenda


class CategoriaSerializer(serializers.ModelSerializer):
    total_prendas = serializers.SerializerMethodField()
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'imagen', 'activa', 'total_prendas', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_total_prendas(self, obj):
        return obj.prendas.filter(activa=True, deleted_at__isnull=True).count()


class MarcaSerializer(serializers.ModelSerializer):
    total_prendas = serializers.SerializerMethodField()
    
    class Meta:
        model = Marca
        fields = ['id', 'nombre', 'descripcion', 'logo', 'activa', 'total_prendas', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_total_prendas(self, obj):
        return obj.prendas.filter(activa=True, deleted_at__isnull=True).count()


class TallaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talla
        fields = ['id', 'nombre', 'orden']
        read_only_fields = ['id']


class ImagenPrendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenPrenda
        fields = ['id', 'imagen', 'es_principal', 'orden', 'alt_text']
        read_only_fields = ['id']


class StockPrendaSerializer(serializers.ModelSerializer):
    talla_detalle = TallaSerializer(source='talla', read_only=True)
    alerta_stock_bajo = serializers.ReadOnlyField()
    
    class Meta:
        model = StockPrenda
        fields = ['id', 'talla', 'talla_detalle', 'cantidad', 'stock_minimo', 'alerta_stock_bajo']
        read_only_fields = ['id', 'alerta_stock_bajo']
    
    def to_representation(self, instance):
        """Mostrar talla_detalle en respuestas GET"""
        ret = super().to_representation(instance)
        ret['talla_detalle'] = TallaSerializer(instance.talla).data
        return ret


class PrendaListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    imagen_principal = serializers.ReadOnlyField()
    stock_total = serializers.ReadOnlyField()
    tiene_stock = serializers.ReadOnlyField()
    tallas_disponibles_detalle = TallaSerializer(source='tallas_disponibles', many=True, read_only=True)
    
    class Meta:
        model = Prenda
        fields = [
            'id', 'nombre', 'precio', 'marca_nombre', 'color', 
            'imagen_principal', 'stock_total', 'tiene_stock',
            'activa', 'destacada', 'es_novedad', 'slug', 'created_at',
            'tallas_disponibles_detalle'
        ]


class PrendaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles"""
    marca_detalle = MarcaSerializer(source='marca', read_only=True)
    categorias_detalle = CategoriaSerializer(source='categorias', many=True, read_only=True)
    tallas_disponibles_detalle = TallaSerializer(source='tallas_disponibles', many=True, read_only=True)
    imagenes = ImagenPrendaSerializer(many=True, read_only=True)
    stocks = StockPrendaSerializer(many=True, read_only=True)
    stock_total = serializers.ReadOnlyField()
    tiene_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Prenda
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 'marca', 'marca_detalle',
            'categorias', 'categorias_detalle', 'tallas_disponibles', 'tallas_disponibles_detalle',
            'color', 'material', 'activa', 'destacada', 'es_novedad',
            'imagenes', 'stocks', 'stock_total', 'tiene_stock',
            'slug', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class PrendaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar prendas con stocks por talla"""
    stocks = serializers.ListField(child=serializers.DictField(), required=False, write_only=True)

    class Meta:
        model = Prenda
        fields = [
            'nombre', 'descripcion', 'precio', 'marca', 'categorias',
            'tallas_disponibles', 'color', 'material', 'activa',
            'destacada', 'es_novedad', 'metadata', 'stocks'
        ]

    def to_internal_value(self, data):
        """
        Parsear el campo stocks si viene como JSON string (desde FormData)
        """
        import json

        # Si stocks viene como string JSON (desde FormData), parsearlo
        if 'stocks' in data and isinstance(data.get('stocks'), str):
            try:
                # Crear una copia mutable de data si es un QueryDict
                if hasattr(data, '_mutable'):
                    data._mutable = True

                parsed_stocks = json.loads(data['stocks'])
                data['stocks'] = parsed_stocks

                if hasattr(data, '_mutable'):
                    data._mutable = False
            except (json.JSONDecodeError, TypeError) as e:
                raise serializers.ValidationError({
                    'stocks': f'El campo stocks debe ser un JSON válido: {str(e)}'
                })

        return super().to_internal_value(data)
    
    def create(self, validated_data):
        categorias = validated_data.pop('categorias', [])
        tallas = validated_data.pop('tallas_disponibles', [])
        stocks_data = validated_data.pop('stocks', [])
        
        prenda = Prenda.objects.create(**validated_data)
        prenda.categorias.set(categorias)
        prenda.tallas_disponibles.set(tallas)
        
        # Crear stocks por talla si se proporcionan
        for stock_data in stocks_data:
            if isinstance(stock_data, dict):
                talla_id = stock_data.get('talla')
                cantidad = int(stock_data.get('cantidad', 0))
                stock_minimo = int(stock_data.get('stock_minimo', 5))
                
                if talla_id:
                    StockPrenda.objects.get_or_create(
                        prenda=prenda,
                        talla_id=talla_id,
                        defaults={'cantidad': cantidad, 'stock_minimo': stock_minimo}
                    )
        
        return prenda
    
    def update(self, instance, validated_data):
        categorias = validated_data.pop('categorias', None)
        tallas = validated_data.pop('tallas_disponibles', None)
        stocks_data = validated_data.pop('stocks', None)
        
        # Actualizar campos simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar relaciones many-to-many
        if categorias is not None:
            instance.categorias.set(categorias)
        if tallas is not None:
            instance.tallas_disponibles.set(tallas)
        
        # Actualizar stocks si se proporcionan
        if stocks_data is not None:
            # Obtener IDs de tallas en el nuevo stock
            new_talla_ids = set()
            
            for stock_data in stocks_data:
                if isinstance(stock_data, dict):
                    talla_id = stock_data.get('talla')
                    cantidad = int(stock_data.get('cantidad', 0))
                    stock_minimo = int(stock_data.get('stock_minimo', 5))
                    
                    if talla_id:
                        new_talla_ids.add(talla_id)
                        stock, created = StockPrenda.objects.get_or_create(
                            prenda=instance,
                            talla_id=talla_id,
                            defaults={'cantidad': cantidad, 'stock_minimo': stock_minimo}
                        )
                        
                        if not created:
                            stock.cantidad = cantidad
                            stock.stock_minimo = stock_minimo
                            stock.save()
            
            # Eliminar stocks de tallas que ya no están en el nuevo set
            instance.stocks.exclude(talla_id__in=new_talla_ids).delete()
        
        return instance