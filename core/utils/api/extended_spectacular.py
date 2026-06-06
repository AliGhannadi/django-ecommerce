from drf_spectacular.utils import OpenApiResponse, OpenApiExample
from rest_framework import serializers
from functools import wraps
from drf_spectacular.utils import extend_schema

class ErrorDetailSerializer(serializers.Serializer):
    status_code = serializers.IntegerField()
    message = serializers.CharField()
    detail = serializers.CharField()

class ErrorResponseSerializer(serializers.Serializer):
    error = ErrorDetailSerializer()
COMMON_ERROR_RESPONSES = {
    400: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Bad request",
        examples=[
            OpenApiExample(
                name="Bad Request",
                value={
                    "error": {
                        "status_code": 400,
                        "message": "Bad request syntax or unsupported method",
                        "detail": "invalid input"
                    }
                },
                status_codes=["400"],
                response_only=True,
            )
        ],
    ),
    401: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Unauthorized",
        examples=[
            OpenApiExample(
                name="Unauthorized",
                value={
                    "error": {
                        "status_code": 401,
                        "message": "No permission -- see authorization schemes",
                        "detail": "Not Authenticated"
                    }
                },
                status_codes=["401"],
                response_only=True,
            )
        ],
    ),
    # Add other common error codes if needed
}



def extend_schema_with_common_errors(**kwargs):
    """Helper to add common error responses to extend_schema."""

    def decorator(func):
        responses = kwargs.get('responses', {})
        # Merge with common errors (without overwriting existing codes)
        for code, resp in COMMON_ERROR_RESPONSES.items():
            responses.setdefault(code, resp)
        kwargs['responses'] = responses

        @extend_schema(**kwargs)
        @wraps(func)
        def wrapper(*args, **inner_kwargs):
            return func(*args, **inner_kwargs)

        return wrapper
    return decorator