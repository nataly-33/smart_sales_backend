import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from apps.core.models import BaseModel

class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo', True)
        
        # Crear rol Admin si no existe
        admin_role, _ = Role.objects.get_or_create(
            nombre='Admin',
            defaults={'descripcion': 'Administrador del sistema', 'es_rol_sistema': True}
        )
        extra_fields.setdefault('rol', admin_role)
        
        return self.create_user(email, password, **extra_fields)


class Role(BaseModel):
    """Roles del sistema"""
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Nombre del rol')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    permisos = models.ManyToManyField('Permission', related_name='roles', blank=True)
    es_rol_sistema = models.BooleanField(default=False, verbose_name='Es rol del sistema')
    
    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre


class Permission(BaseModel):
    """Permisos granulares"""
    codigo = models.CharField(max_length=100, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    modulo = models.CharField(max_length=50, verbose_name='Módulo')
    
    class Meta:
        db_table = 'permiso'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['modulo', 'codigo']
    
    def __str__(self):
        return f"{self.modulo}.{self.codigo}"


class User(AbstractBaseUser, BaseModel):
    """Usuario del sistema"""
    email = models.EmailField(unique=True, verbose_name='Email')
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    foto_perfil = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Foto de perfil')
    
    rol = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='usuarios')
    
    # Empleados
    codigo_empleado = models.CharField(max_length=50, blank=True, verbose_name='Código de empleado')
    
    activo = models.BooleanField(default=True, verbose_name='Activo')
    email_verificado = models.BooleanField(default=False, verbose_name='Email verificado')
    
    # Django admin
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def tiene_permiso(self, codigo_permiso):
        """Verificar si el usuario tiene un permiso específico"""
        if self.is_superuser:
            return True
        if not self.rol:
            return False
        return self.rol.permisos.filter(codigo=codigo_permiso).exists()