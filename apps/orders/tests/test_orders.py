import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, Role
from apps.products.models import Prenda, Marca, Categoria, Talla, StockPrenda
from apps.customers.models import Direccion
from apps.cart.models import Carrito, ItemCarrito
from apps.orders.models import MetodoPago, Pedido
from decimal import Decimal


@pytest.mark.django_db
class TestOrders:
    
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
            rol=cliente_role,
            saldo_billetera=Decimal('1000.00')
        )
        
        # Crear datos necesarios
        self.marca = Marca.objects.create(nombre='Test Marca')
        self.categoria = Categoria.objects.create(nombre='Test Categoria')
        self.talla = Talla.objects.create(nombre='M', orden=1)
        
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
        self.stock = StockPrenda.objects.create(
            prenda=self.prenda,
            talla=self.talla,
            cantidad=10
        )
        
        # Crear dirección
        self.direccion = Direccion.objects.create(
            usuario=self.cliente,
            nombre_completo='Test Cliente',
            telefono='+591 70000000',
            direccion_linea1='Calle Test 123',
            ciudad='Cochabamba',
            departamento='Cochabamba',
            pais='Bolivia',
            es_principal=True
        )
        
        # Crear método de pago
        self.metodo_pago = MetodoPago.objects.create(
            codigo='billetera',
            nombre='Billetera Virtual',
            activo=True
        )
        
        # Crear carrito con items
        self.carrito = Carrito.objects.create(usuario=self.cliente)
        ItemCarrito.objects.create(
            carrito=self.carrito,
            prenda=self.prenda,
            talla=self.talla,
            cantidad=2,
            precio_unitario=self.prenda.precio
        )
        
        # Login
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'email': 'test@cliente.com',
            'password': 'Test2024!'
        }, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_listar_metodos_pago(self):
        """Test: Listar métodos de pago"""
        url = reverse('metodo-pago-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_checkout_exitoso(self):
        """Test: Hacer checkout exitoso"""
        url = reverse('pedido-checkout')
        data = {
            'direccion_envio_id': str(self.direccion.id),
            'metodo_pago': 'billetera',
            'notas_cliente': 'Test checkout'
        }
        
        saldo_inicial = self.cliente.saldo_billetera
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'pedido' in response.data
        
        # Verificar que se creó el pedido
        pedido = Pedido.objects.get(id=response.data['pedido']['id'])
        assert pedido.usuario == self.cliente
        assert pedido.estado == 'pago_recibido'
        
        # Verificar que se descontó de billetera
        self.cliente.refresh_from_db()
        assert self.cliente.saldo_billetera < saldo_inicial
        
        # Verificar que se redujo stock
        self.stock.refresh_from_db()
        assert self.stock.cantidad == 8
        
        # Verificar que se limpió el carrito
        assert self.carrito.items.filter(deleted_at__isnull=True).count() == 0
    
    def test_checkout_sin_saldo(self):
        """Test: Checkout sin saldo suficiente"""
        # Reducir saldo
        self.cliente.saldo_billetera = Decimal('10.00')
        self.cliente.save()
        
        url = reverse('pedido-checkout')
        data = {
            'direccion_envio_id': str(self.direccion.id),
            'metodo_pago': 'billetera'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'saldo insuficiente' in response.data['error'].lower()
    
    def test_listar_mis_pedidos(self):
        """Test: Listar pedidos del cliente"""
        # Crear un pedido
        pedido = Pedido.objects.create(
            usuario=self.cliente,
            direccion_envio=self.direccion,
            subtotal=Decimal('200.00'),
            total=Decimal('210.00'),
            estado='pago_recibido'
        )
        
        url = reverse('pedido-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_cancelar_pedido(self):
        """Test: Cancelar un pedido"""
        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=self.cliente,
            direccion_envio=self.direccion,
            subtotal=Decimal('200.00'),
            total=Decimal('210.00'),
            estado='confirmado'
        )
        
        url = reverse('pedido-cancelar', kwargs={'pk': pedido.id})
        response = self.client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que se canceló
        pedido.refresh_from_db()
        assert pedido.estado == 'cancelado'