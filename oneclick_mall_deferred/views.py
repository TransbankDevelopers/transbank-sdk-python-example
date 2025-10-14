from django.shortcuts import render

import secrets
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from transbank.webpay.oneclick.mall_inscription import MallInscription
from transbank.webpay.oneclick.mall_transaction import MallTransaction
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

ERROR_TEMPLATE = "error_pages/general_error.html"

def get_transbank_inscription():
    return MallInscription.build_for_integration(
        IntegrationCommerceCodes.ONECLICK_MALL_DEFERRED,
        IntegrationApiKeys.WEBPAY
    )

def get_transbank_transaction():
    return MallTransaction.build_for_integration(
        IntegrationCommerceCodes.ONECLICK_MALL_DEFERRED,
        IntegrationApiKeys.WEBPAY
    )

@require_GET
def start(request):
    try:
        inscription = get_transbank_inscription()

        username = f"User-{secrets.randbelow(1000)}"
        email = f"user.{secrets.randbelow(1000)}@example.com"
        response_url = request.build_absolute_uri("/oneclick-mall-diferido/finish")

        request.session["username"] = username
        request.session["email"] = email

        resp = inscription.start(username, email, response_url)

        context = {
            "request_data": {
                "username": username,
                "email": email,
                "response_url": response_url,
            },
            "response_data": resp,
        }

        return render(request, "oneclick_mall_deferred/start.html", context)

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def finish(request):
    """Equivale al método Finish"""
    try:
        inscription = get_transbank_inscription()
        tbk_token = request.GET.get("TBK_TOKEN")

        resp = inscription.finish(tbk_token)

        request.session["tbk_user"] = resp.tbk_user

        context = {
            "username": request.session.get("username", ""),
            "tbk_user": resp.tbk_user,
            "token": tbk_token,
            "response_data": resp,
            "child_commerce_code_1": IntegrationCommerceCodes.ONECLICK_MALL_DEFERRED_CHILD1,
            "child_commerce_code_2": IntegrationCommerceCodes.ONECLICK_MALL_DEFERRED_CHILD2,
        }

        return render(request, "oneclick_mall_deferred/finish.html", context)

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def delete(request):

    try:
        inscription = get_transbank_transaction()
        username = request.GET.get("username")
        tbk_user = request.GET.get("tbk_user")

        inscription.delete(tbk_user, username)

        return render(request, "oneclick_mall_deferred/delete.html")

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def authorize(request):

    try:
        transaction = get_transbank_transaction()

        username = request.GET.get("username")
        tbk_user = request.GET.get("tbk_user")

        child_code_1 = request.GET.get("child_commerce_code1")
        child_code_2 = request.GET.get("child_commerce_code2")
        amount1 = float(request.GET.get("child_commerce_amount1", "0"))
        amount2 = float(request.GET.get("child_commerce_amount2", "0"))
        installments1 = int(request.GET.get("child_commerce_installments1", "0"))
        installments2 = int(request.GET.get("child_commerce_installments2", "0"))

        buy_order = f"buyOrder_{secrets.randbelow(1000)}"
        buy_order_child1 = f"childBuyOrder1_{secrets.randbelow(1000)}"
        buy_order_child2 = f"childBuyOrder2_{secrets.randbelow(1000)}"

        details = [
            {
                "commerce_code": child_code_1,
                "buy_order": buy_order_child1,
                "amount": amount1,
                "installments": installments1,
            },
            {
                "commerce_code": child_code_2,
                "buy_order": buy_order_child2,
                "amount": amount2,
                "installments": installments2,
            },
        ]

        resp = transaction.authorize(username, tbk_user, buy_order, details)

        context = {"response_data": resp}
        return render(request, "oneclick_mall_deferred/authorize.html", context)

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def status(request):
    """Equivale al método Status"""
    try:
        transaction = get_transbank_transaction()
        buy_order = request.GET.get("buy_order")
        resp = transaction.status(buy_order)
        return render(request, "oneclick_mall_deferred/status.html", {"response_data": resp})
    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def refund(request):
    """Equivale al método Refund"""
    try:
        transaction = get_transbank_transaction()
        buy_order = request.GET.get("buy_order")
        child_buy_order = request.GET.get("child_buy_order")
        child_commerce_code = request.GET.get("child_commerce_code")
        amount = float(request.GET.get("amount", "0"))

        resp = transaction.refund(buy_order, child_commerce_code, child_buy_order, amount)

        return render(request, "oneclick_mall_deferred/refund.html", {"response_data": resp})

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def capture(request):
    """Equivale al método Capture"""
    try:
        transaction = get_transbank_transaction()
        buy_order = request.GET.get("buy_order")
        child_buy_order = request.GET.get("child_buy_order")
        authorization_code = request.GET.get("authorization_code")
        amount = float(request.GET.get("amount", "0"))
        child_commerce_code = request.GET.get("child_commerce_code")

        resp = transaction.capture(child_commerce_code, child_buy_order, authorization_code, amount)

        context = {
            "buy_order": buy_order,
            "child_buy_order": child_buy_order,
            "child_commerce_code": child_commerce_code,
            "response_data": resp,
        }

        return render(request, "oneclick_mall_deferred/capture.html", context)

    except Exception as e:
        return render(request, ERROR_TEMPLATE, {"error": str(e)})

