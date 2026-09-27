from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # DRF standart xato javobini {success:false, error:{code,message}} ga o'raymiz
        detail = response.data

        if isinstance(detail, dict) and "detail" in detail:
            message = str(detail["detail"])
        elif isinstance(detail, dict):
            # serializer validation errors — {"field": ["error1", "error2"]}
            message = detail
        elif isinstance(detail, list):
            message = detail[0] if detail else "Xatolik yuz berdi."
        else:
            message = str(detail)

        code_map = {
            400: "VALIDATION_ERROR",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
        }
        code = code_map.get(response.status_code, "ERROR")

        response.data = {
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        }

    return response