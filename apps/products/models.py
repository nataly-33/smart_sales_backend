from django.db import models
from apps.core.models import BaseModel
from apps.core.constants import TALLAS, COLORES


class Categoria(BaseModel):
    """Categorías de productos (Vestidos, Blusas, Pantalones, etc.)"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    imagen = models.ImageField(upload_to='categorias/', null=True, blank=True, verbose_name='Imagen')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Marca(BaseModel):
    """Marcas de ropa"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    logo = models.ImageField(upload_to='marcas/', null=True, blank=True, verbose_name='Logo')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        db_table = 'marca'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Talla(BaseModel):
    """Tallas disponibles"""
    nombre = models.CharField(max_length=10, unique=True, verbose_name='Nombre')
    orden = models.IntegerField(default=0, verbose_name='Orden')
    
    class Meta:
        db_table = 'talla'
        verbose_name = 'Talla'
        verbose_name_plural = 'Tallas'
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class Prenda(BaseModel):
    """Producto principal - Prenda de ropa"""
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    
    # Relaciones
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='prendas', verbose_name='Marca')
    categorias = models.ManyToManyField(Categoria, related_name='prendas', verbose_name='Categorías')
    tallas_disponibles = models.ManyToManyField(Talla, related_name='prendas', verbose_name='Tallas disponibles')
    
    # Características
    color = models.CharField(max_length=50, verbose_name='Color')
    material = models.CharField(max_length=200, blank=True, verbose_name='Material')
    
    # Estado y destacados
    activa = models.BooleanField(default=True, verbose_name='Activa')
    destacada = models.BooleanField(default=False, verbose_name='Destacada')
    es_novedad = models.BooleanField(default=False, verbose_name='Es novedad')
    
    # SEO y metadata
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name='Slug')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadata')
    
    class Meta:
        db_table = 'prenda'
        verbose_name = 'Prenda'
        verbose_name_plural = 'Prendas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['activa', '-created_at']),
            models.Index(fields=['destacada', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.marca.nombre}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.nombre)
            slug = base_slug
            counter = 1
            while Prenda.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def imagen_principal(self):
        """Retorna la primera imagen o None"""
        primera = self.imagenes.filter(es_principal=True).first()
        if primera:
            return primera.imagen.url
        primera_disponible = self.imagenes.first()
        if primera_disponible:
            return primera_disponible.imagen.url
        return None
    
    @property
    def stock_total(self):
        """Calcula el stock total sumando todos los stocks por talla"""
        return self.stocks.aggregate(total=models.Sum('cantidad'))['total'] or 0
    
    @property
    def tiene_stock(self):
        """Verifica si tiene stock disponible"""
        return self.stock_total > 0


class StockPrenda(BaseModel):
    """Control de inventario por talla"""
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='stocks', verbose_name='Prenda')
    talla = models.ForeignKey(Talla, on_delete=models.CASCADE, related_name='stocks', verbose_name='Talla')
    cantidad = models.IntegerField(default=0, verbose_name='Cantidad')
    stock_minimo = models.IntegerField(default=5, verbose_name='Stock mínimo')
    
    class Meta:
        db_table = 'stock_prenda'
        verbose_name = 'Stock de Prenda'
        verbose_name_plural = 'Stocks de Prendas'
        unique_together = [['prenda', 'talla']]
        indexes = [
            models.Index(fields=['prenda', 'talla']),
        ]
    
    def __str__(self):
        return f"{self.prenda.nombre} - Talla {self.talla.nombre}: {self.cantidad} unidades"
    
    @property
    def alerta_stock_bajo(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.cantidad <= self.stock_minimo
    
    def reducir_stock(self, cantidad):
        """Reduce el stock de manera segura"""
        if self.cantidad >= cantidad:
            self.cantidad -= cantidad
            self.save()
            return True
        return False
    
    def aumentar_stock(self, cantidad):
        """Aumenta el stock"""
        self.cantidad += cantidad
        self.save()


class ImagenPrenda(BaseModel):
    """Galería de imágenes para cada prenda"""
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='imagenes', verbose_name='Prenda')
    imagen = models.ImageField(upload_to='productos/', verbose_name='Imagen')
    es_principal = models.BooleanField(default=False, verbose_name='Es principal')
    orden = models.IntegerField(default=0, verbose_name='Orden')
    alt_text = models.CharField(max_length=200, blank=True, verbose_name='Texto alternativo')
    
    class Meta:
        db_table = 'imagen_prenda'
        verbose_name = 'Imagen de Prenda'
        verbose_name_plural = 'Imágenes de Prendas'
        ordering = ['orden', '-es_principal']
        indexes = [
            models.Index(fields=['prenda', 'orden']),
        ]
    
    def __str__(self):
        return f"Imagen de {self.prenda.nombre}"
    
    def save(self, *args, **kwargs):
        # Si es principal, desmarcar las demás
        if self.es_principal:
            ImagenPrenda.objects.filter(prenda=self.prenda, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)