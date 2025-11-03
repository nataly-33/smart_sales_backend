from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """Modelo base abstracto con campos comunes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de eliminación')

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Eliminación lógica"""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        """Restaurar registro eliminado"""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        """Verificar si está eliminado"""
        return self.deleted_at is not None