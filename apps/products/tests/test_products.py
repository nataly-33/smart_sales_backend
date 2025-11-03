import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Categoria, Marca, Talla, Prenda
from decimal import Decimal


@pytest.mark.django_db
class TestProducts:
    
    def setup_method(self):
        """Setup que se ejecuta antes de cada test"""
        self.client = APIClient()
        
        # Crear datos de prueba
        self.categoria = Categoria.objects.create(
            nombre='Vestidos',
            descripcion='Test categoria',
            activa=True
        )
        
        self.marca = Marca.objects.create(
            nombre='Zara',
            descripcion='Test marca',
            activa=True
        )
        
        self.talla = Talla.objects.create(
            nombre='M',
            orden=1
        )
        
        self.prenda = Prenda.objects.create(
            nombre='Vestido Elegante',
            descripcion='Vestido de prueba',
            precio=Decimal('250.00'),
            marca=self.marca,
            color='Negro',
            activa=True
        )
        self.prenda.categorias.add(self.categoria)
        self.prenda.tallas_disponibles.add(self.talla)
    
    def test_listar_categorias(self):
        """Test: Listar categorías sin autenticación"""
        url = reverse('categoria-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_listar_prendas(self):
        """Test: Listar prendas"""
        url = reverse('prenda-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_detalle_prenda(self):
        """Test: Ver detalle de prenda"""
        url = reverse('prenda-detail', kwargs={'pk': self.prenda.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'Vestido Elegante'
        assert float(response.data['precio']) == 250.00
    
    def test_filtrar_por_precio(self):
        """Test: Filtrar prendas por rango de precio"""
        url = reverse('prenda-list')
        response = self.client.get(url, {'precio_min': 200, 'precio_max': 300})
        
        assert response.status_code == status.HTTP_200_OK
        for prenda in response.data['results']:
            precio = float(prenda['precio'])
            assert 200 <= precio <= 300
    
    def test_buscar_prenda(self):
        """Test: Buscar prenda por nombre"""
        url = reverse('prenda-list')
        response = self.client.get(url, {'search': 'Vestido'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0