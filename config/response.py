from rest_framework.response import Response
from rest_framework import status

def _api_response(status_code, success=True, message=None, data=None):
    """
    Generador de respuesta base.
    """
    response_data = {
        'status': 'success' if success else 'error',
    }
    
    if message:
        response_data['message'] = message
    
    if data:
        response_data['data'] = data

    return Response(response_data, status=status_code)


def SuccessResponse(data=None, message="OK", status_code=status.HTTP_200_OK):
    """
    Respuesta 200 OK. Devuelve datos y un mensaje de éxito.
    """
    return _api_response(status_code, success=True, message=message, data=data)

def CreatedResponse(data=None, message="Recurso creado exitosamente."):
    """
    Respuesta 201 Created. Devuelve los datos del nuevo recurso.
    """
    return _api_response(status.HTTP_201_CREATED, success=True, message=message, data=data)

def NoContentResponse(message="Operación exitosa. Sin contenido."):
    """
    Respuesta 204 No Content. Éxito pero no devuelve cuerpo.
    """
    return _api_response(status.HTTP_204_NO_CONTENT, success=True, message=message, data=None)


def ErrorResponse(data=None, message="Error en la solicitud.", status_code=status.HTTP_400_BAD_REQUEST):
    """
    Respuesta 400 Bad Request (Error genérico del cliente).
    Útil para errores de validación (serializers.errors).
    """
    return _api_response(status_code, success=False, message=message, data=data)

def UnauthorizedResponse(message="Autenticación requerida."):
    """
    Respuesta 401 Unauthorized.
    """
    return _api_response(status.HTTP_401_UNAUTHORIZED, success=False, message=message, data=None)

def ForbiddenResponse(message="No tienes permiso para realizar esta acción."):
    """
    Respuesta 403 Forbidden.
    """
    return _api_response(status.HTTP_403_FORBIDDEN, success=False, message=message, data=None)

def NotFoundResponse(message="El recurso solicitado no fue encontrado."):
    """
    Respuesta 404 Not Found.
    """
    return _api_response(status.HTTP_404_NOT_FOUND, success=False, message=message, data=None)

def ServerErrorResponse(message="Error interno del servidor."):
    """
    Respuesta 500 Internal Server Error.
    """
    return _api_response(status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, message=message, data=None)
