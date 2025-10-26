from rest_framework import serializers
from django.core.validators import validate_email, MinLengthValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, Role, Permission, PermissionRole

class PermissionSerializer(serializers.ModelSerializer):
  """
  Serializer para el modelo Permission.
  """
  class Meta:
      model = Permission
      fields = ['id', 'name', 'description']
      read_only_fields = ['id', 'created_at', 'updated_at']

class RoleSerializer(serializers.ModelSerializer):
  """
  Serializer para el modelo Role.
  Incluye permisos anidados y permite asignar permisos por ID.
  """
  permissions = PermissionSerializer(many=True, read_only=True)  # Permisos anidados (solo lectura)
  permission_ids = serializers.PrimaryKeyRelatedField(
      many=True, write_only=True, queryset=Permission.objects.all(), source='permissions'
  )  # Permite asignar permisos usando sus IDs

  class Meta:
      model = Role
      fields = ['id', 'name', 'permissions', 'permission_ids']  # Campos incluidos en la respuesta
      read_only_fields = ['id', 'created_at', 'updated_at']

class RoleListSerializer(serializers.ModelSerializer):
  """
  Serializer simplificado para listar roles.
  """
  class Meta:
      model = Role
      fields = ['id', 'name']
   
class UserSerializer(serializers.ModelSerializer):
  """
  Serializer para el modelo User.
  Incluye validaciones personalizadas y manejo de contraseñas.
  """
  role = RoleListSerializer(read_only=True)  # Rol anidado (solo lectura)
  role_id = serializers.PrimaryKeyRelatedField(
      write_only=True, queryset=Role.objects.all(), source='role', allow_null=True
  )  # Permite asignar el rol usando su ID

  class Meta:
      model = User
      fields = [
          'id', 'ci', 'name', 'lastname', 'email', 'phone', 'gender',
          'is_active', 'role', 'role_id', 'password'
      ]  
      extra_kwargs = {
          'password': {'write_only': True, 'style': {'input_type': 'password', 'required': False}},  
          'is_active': {'read_only': True},  
      }

  def validate_ci(self, value):
      """
      Valida que el CI contenga solo números.
      """
      ci_str = str(value)
      if not ci_str.isdigit():
          raise serializers.ValidationError("El CI debe contener solo números.")
      return 
  
  def validate_name(self, value):
    if not value.strip():
        raise serializers.ValidationError("El nombre no puede estar vacío.")
    return value
  
  def validate_phone(self, value):
    if value:  
        phone_str = str(value)
        if not phone_str.isdigit():
            raise serializers.ValidationError("El número de teléfono debe contener solo números.")
        if len(phone_str) < 7:
            raise serializers.ValidationError("El número de teléfono debe tener al menos 7 dígitos.")
    return value

  def validate_email(self, value):
      try:
          validate_email(value)
      except DjangoValidationError:
          raise serializers.ValidationError("El correo electrónico no tiene un formato válido.")

      if User.objects.filter(email=value).exists():
          raise serializers.ValidationError("Este correo ya está registrado.")
      
      return value

  def create(self, validated_data):
      """
      Crea un usuario y maneja el hashing de la contraseña.
      """
      password = validated_data.pop('password', None) 
      user = User(**validated_data)  
      if password:
          user.set_password(password)  
      user.save()  
      return user

  def update(self, instance, validated_data):
      """
      Actualiza un usuario y maneja el hashing de la contraseña.
      """
      password = validated_data.pop('password', None)  
      user = super().update(instance, validated_data)  
      if password:
          user.set_password(password)  
          user.save()  
      return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
      error_messages={
        'required': "Correo electrónico es obligatorio.",
        'invalid': "Correo electrónico no válido."
      }
    )
    password = serializers.CharField(
        error_messages={
          'required': "Contraseña es obligatoria.",
          'invalid': "Contraseña no válida."
        },
        validators=[MinLengthValidator(6, message="La contraseña debe tener al menos 6 caracteres.")],
        write_only=True
    )

class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()