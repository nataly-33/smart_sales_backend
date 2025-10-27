import pandas as pd
from users.models import Permission, Role, User
from users.constants.permissions import Permissions
from django.db import transaction

class DatabaseSeeder:
    """
    Orquestador principal para poblar la base de datos.
    Sigue un orden específico para asegurar la integridad referencial.
    """
    def __init__(self):
        self.messages = []
        self.created_count = 0
        self.updated_count = 0

    def add_message(self, msg, status="info"):
        self.messages.append({"status": status, "message": msg})

    @transaction.atomic
    def run(self):
        """
        Ejecuta todos los seeders en el orden correcto.
        """
        self.add_message("Iniciando el seeder de la base de datos...")
        
        # 1. Poblar permisos
        self.seed_permissions()
        
        # 2. Poblar roles y SuperUsuario (que depende de los permisos)
        self.seed_roles_and_superuser()
        
        self.add_message(f"Seeder finalizado. {self.created_count} registros creados, {self.updated_count} actualizados.")
        return self.messages

    def seed_permissions(self):
        """
        Puebla la tabla Permission usando el Enum 'users.constants.permissions.Permissions'.
        Esto es vital para que los roles puedan asignarse.
        """
        self.add_message("Poblando permisos...")
        permissions_enum = Permissions
        created = 0
        
        for perm in permissions_enum:
            permission_name = perm.value
            
            # Usamos get_or_create para evitar duplicados
            obj, created_flag = Permission.objects.get_or_create(
                name=permission_name,
                defaults={'description': f'Permiso para {permission_name.lower()}'}
            )
            if created_flag:
                created += 1
        
        self.add_message(f"Se crearon {created} nuevos permisos.")
        self.created_count += created

    def seed_roles_and_superuser(self):
        """
        Crea el Rol 'SuperAdmin' y le asigna todos los permisos.
        Luego crea un usuario SuperAdmin y lo asigna a ese rol.
        """
        self.add_message("Creando Rol 'SuperAdmin' y usuario superusuario...")
        
        # 1. Crear/Obtener el Rol SuperAdmin
        role_super_admin, role_created = Role.objects.get_or_create(name="SuperAdmin")
        if role_created:
            self.add_message("Rol 'SuperAdmin' creado.")
            self.created_count += 1
        else:
            self.add_message("Rol 'SuperAdmin' ya existía.")
            
        # 2. Asignar TODOS los permisos al Rol SuperAdmin
        all_permissions = Permission.objects.all()
        if role_super_admin.permissions.count() != all_permissions.count():
            role_super_admin.permissions.set(all_permissions)
            self.add_message(f"Todos los {all_permissions.count()} permisos asignados al rol 'SuperAdmin'.")
            self.updated_count += 1

        # 3. Crear el SuperUsuario (usando pandas como solicitaste para la estructura)
        # Definimos los datos del superusuario
        user_data = {
            'ci': '000000',
            'name': 'Super',
            'lastname': 'Admin',
            'email': 'admin@smartsales.com',
            'phone': '77777777',
            'password': 'admin12345', 
            'role_name': 'SuperAdmin'
        }
        df = pd.DataFrame([user_data])
        
        # Iteramos (aunque solo es 1, esto escala para 1000 usuarios)
        for _, row in df.iterrows():
            
            # Verificar si el usuario ya existe
            if not User.objects.filter(email=row['email']).exists():
                try:
                    # Usamos el manager 'create_superuser'
                    User.objects.create_superuser(
                        email=row['email'],
                        password=row['password'],
                        ci=row['ci'],
                        name=row['name'],
                        lastname=row['lastname'],
                        phone=row['phone'],
                        role=role_super_admin # Asignamos el rol con todos los permisos
                    )
                    self.add_message(f"SuperUsuario '{row['email']}' creado con contraseña '{row['password']}'.")
                    self.created_count += 1
                except Exception as e:
                    self.add_message(f"Error al crear SuperUsuario: {str(e)}", status="error")
            else:
                self.add_message(f"SuperUsuario '{row['email']}' ya existía.", status="info")
