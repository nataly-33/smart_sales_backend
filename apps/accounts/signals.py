from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """Signal que se ejecuta cuando se crea un usuario"""
    if created:
        print(f"Usuario creado: {instance.email} - Rol: {instance.rol}")