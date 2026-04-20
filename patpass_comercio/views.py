import secrets

from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.patpass_comercio.inscription import Inscription

ERROR_TEMPLATE = "error_pages/general_error.html"
SESSION_TOKEN_KEY = "patpass_j_token"
DEFAULT_VOUCHER_URL = "https://pagoautomaticocontarjetasint.transbank.cl/nuevo-ic-rest/tokenVoucherLogin"


def get_transbank_inscription():
    return Inscription.build_for_integration(
        IntegrationCommerceCodes.PATPASS_COMERCIO,
        IntegrationApiKeys.PATPASS_COMERCIO,
    )


@require_GET
def start(request):
    navigation = {
        "request": "Peticion",
        "response": "Respuesta",
        "form": "Formulario",
        "example": "Ejemplo",
    }

    try:
        inscription = get_transbank_inscription()
        request_data = {
            "service_id": f"Service-{secrets.randbelow(10000) + 1}",
            "max_amount": 100,
            "return_url": request.build_absolute_uri("/patpass-comercio/commit"),
            "final_url": request.build_absolute_uri("/patpass-comercio/voucher"),
            "name": "Isaac",
            "last_name": "Newton",
            "second_last_name": "Gonzales",
            "rut": "11111111-1",
            "phone": "123456734",
            "cell_phone": "123456723",
            "patpass_name": "Membresia de cable",
            "person_email": "developer@continuum.cl",
            "commerce_email": "developer@continuum.cl",
            "address": "Satelite 101",
            "city": "Santiago",
        }

        response_data = inscription.start(
            request_data["return_url"],
            request_data["name"],
            request_data["last_name"],
            request_data["second_last_name"],
            request_data["rut"],
            request_data["service_id"],
            request_data["final_url"],
            request_data["max_amount"],
            request_data["phone"],
            request_data["cell_phone"],
            request_data["patpass_name"],
            request_data["person_email"],
            request_data["commerce_email"],
            request_data["address"],
            request_data["city"],
        )

        context = {
            "active_link": "Patpass Comercio",
            "navigation": navigation,
            "request_data": request_data,
            "response_data": response_data,
        }
        return render(request, "patpass_comercio/start.html", context)
    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_http_methods(["GET", "POST"])
@csrf_exempt
def commit(request):
    try:
        j_token = get_incoming_token(request, "j_token", "J_TOKEN", "token")
        if not j_token:
            message = get_missing_token_message(request.method)
            return render(request, ERROR_TEMPLATE, {"error": message})

        if request.method == "POST":
            request.session[SESSION_TOKEN_KEY] = j_token
            result = redirect("patpass_comercio:commit")
        else:
            inscription = get_transbank_inscription()
            response_data = inscription.status(j_token)
            request.session[SESSION_TOKEN_KEY] = j_token

            context = {
                "navigation": {
                    "data": "Datos recibidos",
                    "request": "Peticion",
                    "response": "Respuesta",
                    "form": "Formulario",
                },
                "token": j_token,
                "response_data": response_data,
                "voucher_url": response_data.get("url_voucher") or DEFAULT_VOUCHER_URL,
                "response_payload": {
                    "authorized": response_data.get("status"),
                    "voucher_url": response_data.get("url_voucher"),
                },
            }
            result = render(request, "patpass_comercio/commit.html", context)

        return result
    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_http_methods(["GET", "POST"])
@csrf_exempt
def voucher(request):
    try:
        j_token = get_incoming_token(request, "j_token", "J_TOKEN", "tokenComercio", "token")
        if not j_token:
            message = get_missing_token_message(request.method)
            return render(request, ERROR_TEMPLATE, {"error": message})

        if request.method == "POST":
            request.session[SESSION_TOKEN_KEY] = j_token
            result = redirect("patpass_comercio:voucher")
        else:
            context = {
                "navigation": {"form": "Formulario"},
                "token": j_token,
                "voucher_url": DEFAULT_VOUCHER_URL,
            }
            result = render(request, "patpass_comercio/voucher.html", context)

        return result
    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


def get_incoming_token(request, *keys):
    for key in keys:
        value = request.POST.get(key) or request.GET.get(key)
        if value:
            return value
    return request.session.get(SESSION_TOKEN_KEY)


def get_missing_token_message(method):
    if method == "POST":
        return "No se recibio el token de inscripcion (J_TOKEN)."
    return "No se encontro el token de inscripcion (J_TOKEN)."
