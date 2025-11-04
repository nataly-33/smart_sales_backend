import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Servicio para integración con Stripe"""
    
    @staticmethod
    def crear_payment_intent(monto, moneda='usd', metadata=None):
        """
        Crear un Payment Intent en Stripe
        
        Args:
            monto: Monto en la menor denominación (centavos para USD/EUR)
            moneda: Código de moneda (usd, eur, bob, etc)
            metadata: Diccionario con metadata adicional
        
        Returns:
            Payment Intent object
        """
        try:
            # Convertir monto a centavos (int)
            amount_cents = int(Decimal(str(monto)) * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=moneda,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            return {
                'success': True,
                'payment_intent': payment_intent,
                'client_secret': payment_intent.client_secret
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def confirmar_payment_intent(payment_intent_id):
        """Confirmar un Payment Intent"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'payment_intent': payment_intent,
                'status': payment_intent.status
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def crear_refund(payment_intent_id, monto=None):
        """Crear un reembolso"""
        try:
            refund_data = {'payment_intent': payment_intent_id}
            
            if monto:
                amount_cents = int(Decimal(str(monto)) * 100)
                refund_data['amount'] = amount_cents
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'success': True,
                'refund': refund
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def construir_evento_webhook(payload, sig_header, webhook_secret):
        """Construir y verificar evento de webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return {
                'success': True,
                'event': event
            }
        except ValueError:
            return {
                'success': False,
                'error': 'Invalid payload'
            }
        except stripe.error.SignatureVerificationError:
            return {
                'success': False,
                'error': 'Invalid signature'
            }