from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler as drf_exception_handler

# creating custom exception handler for model clean function to be compatible with rest_framework
def exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(as_serializer_error(exc))

    return drf_exception_handler(exc, context)


from http import HTTPStatus
from typing import Any
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed,NotAuthenticated
from rest_framework.views import Response

def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Custom API exception handler."""
    error_payload = {
            "error": {
                "status_code": 0,
                "message": "",
                "detail": "",
            }
        }
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        http_code_to_message = {v.value: v.description for v in HTTPStatus}        
        error = error_payload["error"]
        status_code = response.status_code
        error["status_code"] = status_code
        error["message"] = http_code_to_message[status_code]
        
        if isinstance(exc, PermissionDenied):
            # Custom handling for PermissionDenied
            error["detail"] = "Permission Denied"
        elif isinstance(exc, AuthenticationFailed):
            # Custom handling for AuthenticationFailed (401 Unauthorized)
            error["detail"] =  "AuthenticationFailed"
            
        elif isinstance(exc, NotAuthenticated):
            error["detail"] = "Not Authenticated"
        else:
            # error["details"] = response.data
            if isinstance(response.data, list):
                error["detail"] = response.data[0] if response.data else ""
            elif isinstance(response.data, dict):
                response_data = response.data.get('detail', None)
                if response_data and type(response_data) != list:
                    error["detail"] = response_data
                elif response_data and type(response_data) == list:
                    error["detail"] = response_data[0]
                else:
                    error["detail"] = response.data
            else:
                error["detail"] = response.data
        response.data = error_payload
    return response


