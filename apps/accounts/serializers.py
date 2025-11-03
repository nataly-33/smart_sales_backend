from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User, Role, Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'modulo']


class RoleSerializer(serializers.ModelSerializer):
    permisos = PermissionSerializer(many=True, read_only=True)
    permisos_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = ['id', 'nombre', 'descripcion', 'permisos', 'permisos_ids', 'es_rol_sistema', 'created_at']
    
    def create(self, validated_data):
        permisos_ids = validated_data.pop('permisos_ids', [])
        role = Role.objects.create(**validated_data)
        if permisos_ids:
            role.permisos.set(permisos_ids)
        return role
    
    def update(self, instance, validated_data):
        permisos_ids = validated_data.pop('permisos_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permisos_ids is not None:
            instance.permisos.set(permisos_ids)
        
        return instance


class UserSerializer(serializers.ModelSerializer):
    rol_detalle = RoleSerializer(source='rol', read_only=True)
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'nombre', 'apellido', 'nombre_completo',
            'telefono', 'foto_perfil', 'rol', 'rol_detalle',
            'codigo_empleado', 'saldo_billetera', 'activo',
            'email_verificado', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'nombre', 'apellido',
            'telefono', 'rol', 'codigo_empleado', 'activo'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar datos del usuario al response
        data['user'] = UserSerializer(self.user).data
        
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'nombre', 'apellido', 'telefono']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Asignar rol Cliente por defecto
        cliente_role = Role.objects.get(nombre='Cliente')
        
        user = User.objects.create_user(
            password=password,
            rol=cliente_role,
            **validated_data
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden"})
        return attrs