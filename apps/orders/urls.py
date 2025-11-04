from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, MetodoPagoViewSet, StripeWebhookView

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'metodos-pago', MetodoPagoViewSet, basename='metodo-pago')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
]