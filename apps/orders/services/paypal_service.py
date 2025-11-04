import requests
from django.conf import settings
from decimal import Decimal
import base64


class PayPalService:
    """Servicio para integración con PayPal"""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.mode = settings.PAYPAL_MODE
        
        if self.mode == 'sandbox':
            self.base_url = 'https://api-m.sandbox.paypal.com'
        else:
            self.base_url = 'https://api-m.paypal.com'
    
    def get_access_token(self):
        """Obtener token de acceso"""
        url = f"{self.base_url}/v1/oauth2/token"
        
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()['access_token']
        except requests.RequestException as e:
            print(f"Error obteniendo token: {e}")
            return None
    
    def crear_orden(self, monto, moneda='USD', descripcion='Compra en SmartSales365'):
        """Crear una orden en PayPal"""
        access_token = self.get_access_token()
        
        if not access_token:
            return {'success': False, 'error': 'No se pudo obtener token de acceso'}
        
        url = f"{self.base_url}/v2/checkout/orders"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        payload = {
            'intent': 'CAPTURE',
            'purchase_units': [{
                'amount': {
                    'currency_code': moneda,
                    'value': str(monto)
                },
                'description': descripcion
            }]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            order = response.json()
            
            return {
                'success': True,
                'order_id': order['id'],
                'order': order
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def capturar_orden(self, order_id):
        """Capturar (completar) una orden"""
        access_token = self.get_access_token()
        
        if not access_token:
            return {'success': False, 'error': 'No se pudo obtener token de acceso'}
        
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            capture = response.json()
            
            return {
                'success': True,
                'capture': capture,
                'status': capture['status']
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def obtener_orden(self, order_id):
        """Obtener detalles de una orden"""
        access_token = self.get_access_token()
        
        if not access_token:
            return {'success': False, 'error': 'No se pudo obtener token de acceso'}
        
        url = f"{self.base_url}/v2/checkout/orders/{order_id}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            order = response.json()
            
            return {
                'success': True,
                'order': order
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }