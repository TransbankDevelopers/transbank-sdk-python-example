import secrets

from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

ERROR_TEMPLATE = "error_pages/general_error.html"

def get_transbank_transaction():
    return Transaction.build_for_integration(
        IntegrationCommerceCodes.WEBPAY_PLUS_DEFERRED,
        IntegrationApiKeys.WEBPAY
    )

@require_GET
def create(request):
    
    navigation = {
        "request": "Petición",
        "response": "Respuesta",
        "form": "Formulario",
        "example": "Ejemplo",
    }

    try:    
        tx = get_transbank_transaction()
        create_tx = {
            'buy_order': "O-" + str(secrets.randbelow(1001) + 10000),
            'session_id': "S-" + str(secrets.randbelow(1001) + 10000),
            'return_url': request.build_absolute_uri("/webpay-plus-deferred/commit"),
            'amount': secrets.randbelow(1001) + 10000,
        }
        resp = tx.create(create_tx["buy_order"], create_tx["session_id"], create_tx["amount"], create_tx["return_url"])

        context = {
            "active_link": "Webpay Plus Diferido",
            "navigation": navigation,
            "request": create_tx,
            'response_data': resp
        }
      
        return render(request, 'webpay_plus_deferred/create.html', context)
       
    except Exception as e:
        return render(request, "webpay_plus_deferred/create.html", {'error': str(e)})

@require_http_methods(["GET", "POST"])
@csrf_exempt
def commit(request):
    tx = get_transbank_transaction()
    try:
        view = "error/webpay/timeout.html"
        data = {"request": request, "product": "Webpay Plus Diferido"}
        tbk_token = request.GET.get("TBK_TOKEN") or request.POST.get("TBK_TOKEN")
        token_ws = request.GET.get("token_ws") or request.POST.get("token_ws")
        view = "error_pages/timeout.html"

        if tbk_token and token_ws:
            view = "error_pages/form_error.html"
        elif tbk_token:
            view = "error_pages/aborted.html"
            resp = tx.status(tbk_token)
            data["response_data"] = resp
        elif token_ws:
            resp = tx.commit(token_ws)
            view = "webpay_plus_deferred/commit.html"
            data = {
                "response_data": resp,
                "token": token_ws,
                "returnUrl": request.build_absolute_uri("/webpay_plus_deferred/commit"),
            }

        return render(request, view, data)

    except Exception as e:
        return render(request, "error_pages/general_error.html", {"error": str(e)})


@require_GET
def capture(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        buy_order = request.GET.get("buy_order")
        authorization_code = request.GET.get("authorization_code")
        resp = tx.capture(token, buy_order, authorization_code, amount)

        return render(
            request, "webpay_plus_deferred/capture.html", {"response_data": resp, "token": token}
        )

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})

@require_GET
def refund(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        resp = tx.refund(token, amount)

        return render(
            request, "webpay_plus_deferred/refund.html", {"response_data": resp, "token": token}
        )

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def status(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token")
        resp = tx.status(token)

        return render(
            request, "webpay_plus_deferred/status.html", {"response_data": resp, "req": request, "token": token}
        )

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})
