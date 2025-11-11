from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from .models import User, LoginAudit

# Señal personalizada para login exitoso
user_logged_in = Signal()


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """Signal que se ejecuta cuando se crea un usuario"""
    if created:
        print(f"Usuario creado: {instance.email} - Rol: {instance.rol}")


@receiver(user_logged_in)
def log_user_login(sender, user, request, **kwargs):
    """Registrar el login del usuario"""
    
    # Obtener IP del usuario
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    # Obtener user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Crear registro de auditoría
    LoginAudit.objects.create(
        user=user,
        ip_address=ip,
        user_agent=user_agent,
        success=True
    )