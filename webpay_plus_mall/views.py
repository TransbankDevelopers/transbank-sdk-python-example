import secrets
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.csrf import csrf_exempt

from transbank.webpay.webpay_plus.mall_transaction import MallTransaction
from transbank.webpay.webpay_plus.request import MallTransactionCreateDetails
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

ERROR_TEMPLATE = "error_pages/general_error.html"


def get_transbank_transaction():
    return MallTransaction.build_for_integration(
        IntegrationCommerceCodes.WEBPAY_PLUS_MALL,
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

        details = MallTransactionCreateDetails(
            1000,
            IntegrationCommerceCodes.WEBPAY_PLUS_MALL_CHILD1,
            f"childBuyOrder1_{secrets.randbelow(1000)}"
            
        ).add(
            2000,
            IntegrationCommerceCodes.WEBPAY_PLUS_MALL_CHILD2,
            f"childBuyOrder2_{secrets.randbelow(1000)}"
        )
        create_tx = {
            'buy_order': "O-" + str(secrets.randbelow(10000) + 1),
            'session_id': "S-" + str(secrets.randbelow(10000) + 1),
            'return_url': request.build_absolute_uri("/webpay-plus-mall/commit"),
            'details': [
                {
                    'amount': 1000,
                    'commerce_code': IntegrationCommerceCodes.WEBPAY_PLUS_MALL_CHILD1,
                    'buy_order': details.details[0].buy_order
                },
                {
                    'amount': 2000,
                    'commerce_code': IntegrationCommerceCodes.WEBPAY_PLUS_MALL_CHILD2,
                    'buy_order': details.details[1].buy_order
                }
            ],
        }
        
        resp = tx.create(create_tx["buy_order"], create_tx["session_id"], create_tx["return_url"], details)

        context = {
            "active_link": "Webpay Plus Mall",
            "navigation": navigation,
            "request": create_tx,
            'response_data': resp
        }
      
        return render(request, 'webpay_plus_mall/create.html', context)
       
    except Exception as e:
        return render(request, ERROR_TEMPLATE, {'error': str(e)})

@require_http_methods(["GET", "POST"])
@csrf_exempt
def commit(request):
    tx = get_transbank_transaction()
    try:
        view = "error_pages/timeout.html"
        data = {"request": request, "product": "Webpay Plus Mall"}
        tbk_token = request.GET.get("TBK_TOKEN") or request.POST.get("TBK_TOKEN")
        token_ws = request.GET.get("token_ws") or request.POST.get("token_ws")
        
        if tbk_token and token_ws:
            view = "error_pages/form_error.html"
        elif tbk_token:
            view = "error_pages/aborted.html"
            resp = tx.status(tbk_token)
            data["response_data"] = resp
        elif token_ws:
            resp = tx.commit(token_ws)
            view = "webpay_plus_mall/commit.html"
            data = {
                "response_data": resp,
                "token": token_ws,
                "returnUrl": request.build_absolute_uri("/webpay-plus-mall/commit"),
            }

        return render(request, view, data)

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})

@require_GET
def refund(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token")
        commerce_code = request.GET.get("commerce_code")
        buy_order = request.GET.get("buy_order")
        amount = int(request.GET.get("amount", "0"))
        
        resp = tx.refund(token, buy_order, commerce_code, amount)

        return render(
            request, "webpay_plus_mall/refund.html", {
                "response_data": resp, 
                "token": token,
                "commerce_code": commerce_code,
                "buy_order": buy_order
            }
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
            request, "webpay_plus_mall/status.html", {
                "response_data": resp, 
                "req": request, 
                "token": token
            }
        )

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})
