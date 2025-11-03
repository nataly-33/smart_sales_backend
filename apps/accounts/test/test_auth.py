import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, Role


@pytest.mark.django_db
class TestAuthentication:
    """Tests de autenticación"""
    
    def setup_method(self):
        """Setup que se ejecuta antes de cada test"""
        self.client = APIClient()
        
        # Crear rol Admin
        self.admin_role = Role.objects.create(
            nombre='Admin',
            descripcion='Administrador',
            es_rol_sistema=True
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            email='test@smartsales365.com',
            password='Test2024!',
            nombre='Test',
            apellido='User',
            rol=self.admin_role
        )
    
    def test_login_success(self):
        """Test: Login exitoso"""
        url = reverse('login')
        data = {
            'email': 'test@smartsales365.com',
            'password': 'Test2024!'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_login_invalid_credentials(self):
        """Test: Login con credenciales inválidas"""
        url = reverse('login')
        data = {
            'email': 'test@smartsales365.com',
            'password': 'WrongPassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self):
        """Test: Obtener usuario actual autenticado"""
        # Hacer login primero
        login_url = reverse('login')
        login_data = {
            'email': 'test@smartsales365.com',
            'password': 'Test2024!'
        }
        
        login_response = self.client.post(login_url, login_data, format='json')
        token = login_response.data['access']
        
        # Obtener usuario actual
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('user-me')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@smartsales365.com'