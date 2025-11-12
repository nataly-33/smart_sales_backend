from apps.notifications.services import notification_service
from apps.accounts.models import User

print("\n" + "="*60)
print("PRUEBA DEL SISTEMA DE NOTIFICACIONES")
print("="*60)

user = User.objects.first()

if user:
    print(f"\nUsuario encontrado: {user.email}")
    print("\nEnviando notificación...")
    
    result = notification_service.send_to_user(
        user=user,
        title="Test de Backend",
        body="Si ves esto en logs, el backend funciona!",
        notification_type="general",
        save_to_db=True
    )
    
    print(f"Resultado: {result}")
    print("\nSi ves un mensaje arriba, la notificacion se envio!")
else:
    print("ERROR: No hay usuarios en la BD")
    print("Ejecuta: python manage.py createsuperuser")

print("="*60 + "\n")
