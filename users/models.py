import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from config.models import BaseModel
from config.enums import Gender
from users.constants.permissions import Permissions

class Permission(BaseModel):
    name = models.CharField(max_length=60, unique=True, choices=Permissions.choices)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Role(BaseModel):
    name = models.CharField(max_length=60, unique=True)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(Permission, related_name="roles")

    def __str__(self):
        return self.name

#class PermissionRole(BaseModel):
#    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
#    role = models.ForeignKey(Role, on_delete=models.CASCADE)
#
#    def __str__(self):
#        return f"{self.role.name} - {self.permission.name}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    ci = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.OTHER)
    
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # Required for Django admin

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['ci', 'name', 'lastname', 'phone']

    def __str__(self):
        return f"{self.name} {self.lastname} ({self.role})"