from rest_framework.views import exception_handler


def vopt_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(response.data, dict):
        response.data = {"erro": response.data}
    else:
        response.data = {"erro": response.data}
    return response
