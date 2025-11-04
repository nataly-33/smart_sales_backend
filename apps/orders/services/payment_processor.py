from decimal import Decimal
from django.db import transaction
from ..models import Pago, MetodoPago
from .stripe_service import StripeService
from .paypal_service import PayPalService


class PaymentProcessor:
    """Procesador centralizado de pagos"""
    
    @staticmethod
    def procesar_pago_stripe(pedido, payment_method_id):
        """Procesar pago con Stripe"""
        try:
            metodo_pago = MetodoPago.objects.get(codigo='tarjeta')
            
            # Crear Payment Intent
            result = StripeService.crear_payment_intent(
                monto=pedido.total,
                moneda='usd',
                metadata={
                    'pedido_id': str(pedido.id),
                    'numero_pedido': pedido.numero_pedido,
                    'usuario_email': pedido.usuario.email
                }
            )
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result.get('error', 'Error desconocido')
                }
            
            # Registrar pago
            pago = Pago.objects.create(
                pedido=pedido,
                metodo_pago=metodo_pago,
                monto=pedido.total,
                estado='procesando',
                stripe_payment_intent_id=result['payment_intent']['id'],
                response_data=result
            )
            
            return {
                'success': True,
                'pago': pago,
                'client_secret': result['client_secret']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def procesar_pago_paypal(pedido, paypal_order_id):
        """Procesar pago con PayPal"""
        try:
            metodo_pago = MetodoPago.objects.get(codigo='paypal')
            paypal_service = PayPalService()
            
            # Capturar orden de PayPal
            result = paypal_service.capturar_orden(paypal_order_id)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result.get('error', 'Error desconocido')
                }
            
            # Verificar estado
            if result['status'] != 'COMPLETED':
                return {
                    'success': False,
                    'error': f'Pago no completado. Estado: {result["status"]}'
                }
            
            # Registrar pago
            pago = Pago.objects.create(
                pedido=pedido,
                metodo_pago=metodo_pago,
                monto=pedido.total,
                estado='completado',
                paypal_order_id=paypal_order_id,
                transaction_id=paypal_order_id,
                response_data=result
            )
            
            # Actualizar estado del pedido
            pedido.cambiar_estado('pago_recibido', notas='Pago completado via PayPal')
            
            return {
                'success': True,
                'pago': pago
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def procesar_pago_billetera(pedido, usuario):
        """Procesar pago con billetera virtual"""
        try:
            # Verificar saldo
            if usuario.saldo_billetera < pedido.total:
                return {
                    'success': False,
                    'error': 'Saldo insuficiente',
                    'saldo_actual': usuario.saldo_billetera,
                    'total_requerido': pedido.total
                }
            
            metodo_pago = MetodoPago.objects.get(codigo='billetera')
            
            with transaction.atomic():
                # Descontar saldo
                usuario.saldo_billetera -= pedido.total
                usuario.save()
                
                # Registrar pago
                pago = Pago.objects.create(
                    pedido=pedido,
                    metodo_pago=metodo_pago,
                    monto=pedido.total,
                    estado='completado',
                    transaction_id=f'WALLET-{pedido.numero_pedido}'
                )
                
                # Actualizar estado del pedido
                pedido.cambiar_estado('pago_recibido', usuario, 'Pago completado con billetera virtual')
            
            return {
                'success': True,
                'pago': pago,
                'nuevo_saldo': usuario.saldo_billetera
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }