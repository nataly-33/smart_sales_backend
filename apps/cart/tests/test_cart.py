import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, Role
from apps.products.models import Prenda, Marca, Categoria, Talla, StockPrenda
from apps.cart.models import Carrito, ItemCarrito
from decimal import Decimal


@pytest.mark.django_db
class TestCart:
    
    def setup_method(self):
        self.client = APIClient()
        
        # Crear rol cliente
        cliente_role = Role.objects.create(nombre='Cliente', es_rol_sistema=True)
        
        # Crear usuario cliente
        self.cliente = User.objects.create_user(
            email='test@cliente.com',
            password='Test2024!',
            nombre='Test',
            apellido='Cliente',
            rol=cliente_role
        )
        
        # Crear marca y categoría
        self.marca = Marca.objects.create(nombre='Test Marca')
        self.categoria = Categoria.objects.create(nombre='Test Categoria')
        
        # Crear talla
        self.talla = Talla.objects.create(nombre='M', orden=1)
        
        # Crear prenda
        self.prenda = Prenda.objects.create(
            nombre='Test Prenda',
            descripcion='Descripción test',
            precio=Decimal('100.00'),
            marca=self.marca,
            color='Negro',
            activa=True
        )
        self.prenda.categorias.add(self.categoria)
        self.prenda.tallas_disponibles.add(self.talla)
        
        # Crear stock
        StockPrenda.objects.create(
            prenda=self.prenda,
            talla=self.talla,
            cantidad=10
        )
        
        # Login
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'email': 'test@cliente.com',
            'password': 'Test2024!'
        }, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_ver_carrito_vacio(self):
        """Test: Ver carrito vacío"""
        url = reverse('carrito-mi-carrito')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0
    
    def test_agregar_al_carrito(self):
        """Test: Agregar producto al carrito"""
        url = reverse('carrito-agregar')
        data = {
            'prenda': str(self.prenda.id),
            'talla': str(self.talla.id),
            'cantidad': 2
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['carrito']['total_items'] == 1
        
        # Verificar que se creó el item
        carrito = Carrito.objects.get(usuario=self.cliente)
        assert carrito.items.count() == 1
        
        item = carrito.items.first()
        assert item.cantidad == 2
        assert item.prenda == self.prenda
    
    def test_agregar_sin_stock(self):
        """Test: Intentar agregar más cantidad que el stock disponible"""
        url = reverse('carrito-agregar')
        data = {
            'prenda': str(self.prenda.id),
            'talla': str(self.talla.id),
            'cantidad': 15  # Solo hay 10 en stock
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST