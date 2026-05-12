from decimal import Decimal, InvalidOperation

from django.shortcuts import render
from transbank.error.transbank_error import TransbankError

ERROR_TEMPLATE = "error_pages/general_error.html"
GENERIC_ERROR_MESSAGE = "Ocurrió un error inesperado al procesar la operación."


def required_text_param(request, key):
    value = request.GET.get(key)
    if value:
        return value
    raise ValueError(f"El parámetro {key} es obligatorio.")


def required_decimal_param(request, key):
    value = required_text_param(request, key)
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"El parámetro {key} debe ser numérico.") from exc


def required_integer_param(request, key):
    value = required_text_param(request, key)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"El parámetro {key} debe ser un entero.") from exc


def render_error(request, exception, template=ERROR_TEMPLATE):
    return render(request, template, {"error": displayable_error_message(exception)})


def displayable_error_message(exception):
    current = exception

    while current:
        if isinstance(current, TransbankError):
            return str(current)
        current = current.__cause__ or current.__context__

    return GENERIC_ERROR_MESSAGE
