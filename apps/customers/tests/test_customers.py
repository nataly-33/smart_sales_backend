import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, Role
from apps.customers.models import Direccion, Favoritos
from apps.products.models import Prenda, Marca, Categoria
from decimal import Decimal


@pytest.mark.django_db
class TestCustomers:
    
    def setup_method(self):
        self.client = APIClient()
        
        # Crear rol cliente
        cliente_role = Role.objects.create(
            nombre='Cliente',
            descripcion='Cliente del sistema',
            es_rol_sistema=True
        )
        
        # Crear usuario cliente
        self.cliente = User.objects.create_user(
            email='test@cliente.com',
            password='Test2024!',
            nombre='Test',
            apellido='Cliente',
            rol=cliente_role,
            saldo_billetera=Decimal('1000.00')
        )
        
        # Login
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'email': 'test@cliente.com',
            'password': 'Test2024!'
        }, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_ver_perfil(self):
        """Test: Ver perfil del cliente"""
        url = reverse('customer-profile-me')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@cliente.com'
        assert float(response.data['saldo_billetera']) == 1000.00
    
    def test_crear_direccion(self):
        """Test: Crear dirección"""
        url = reverse('address-list')
        data = {
            'nombre_completo': 'Test Cliente',
            'telefono': '+591 70000000',
            'direccion_linea1': 'Calle Test 123',
            'ciudad': 'Cochabamba',
            'departamento': 'Cochabamba',
            'pais': 'Bolivia'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Direccion.objects.filter(usuario=self.cliente).count() == 1
    
    def test_ver_saldo_billetera(self):
        """Test: Ver saldo de billetera"""
        url = reverse('customer-profile-wallet')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data['saldo']) == 1000.00