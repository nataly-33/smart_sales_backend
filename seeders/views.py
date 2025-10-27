from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from config.response import SuccessResponse, ServerErrorResponse
from .seeders import DatabaseSeeder

@extend_schema(tags=['Seeders'])
class SeederRunView(APIView):
    """
    Endpoint para ejecutar los seeders de la base de datos.
    Accesible sin autenticación (para la configuración inicial).
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Ejecutar seeders de la base de datos",
        description="Este endpoint ejecuta el seeder principal para inicializar la base de datos.",
        responses={
            200: {
                "description": "Seeder ejecutado exitosamente.",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True,
                            "message": "Seeder ejecutado exitosamente.",
                            "data": {
                                "logs": ["Seeder 1 ejecutado", "Seeder 2 ejecutado"]
                            }
                        }
                    }
                }
            },
            500: {
                "description": "Error durante la ejecución del seeder.",
                "content": {
                    "application/json": {
                        "example": {
                            "success": False,
                            "message": "Error durante la ejecución del seeder: <detalle del error>"
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """
        Ejecuta el seeder principal al recibir una petición GET.
        """
        try:
            seeder = DatabaseSeeder()
            messages = seeder.run()
            return SuccessResponse(
                message="Seeder ejecutado exitosamente.",
                data={"logs": messages}
            )
        except Exception as e:
            return ServerErrorResponse(
                message=f"Error durante la ejecución del seeder: {str(e)}"
            )