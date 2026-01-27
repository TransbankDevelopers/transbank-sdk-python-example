import secrets
import logging
import re

from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from transbank.webpay.transaccion_completa.transaction import Transaction
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

logger = logging.getLogger(__name__)

ERROR_TEMPLATE = "error_pages/general_error.html"


def get_transbank_transaction():
    return Transaction.build_for_integration(
        IntegrationCommerceCodes.TRANSACCION_COMPLETA_DEFERRED,
        IntegrationApiKeys.WEBPAY
    )


@require_GET
def index(request):
    return render(request, "transaccion_completa_diferida/index.html")


@require_POST
def create(request):
    tx = get_transbank_transaction()
    try:
        card_number = request.POST.get("number", "")
        expiry = request.POST.get("expiry", "")
        cvc = request.POST.get("cvc", "")
        
        card_number_clean = re.sub(r"\s+", "", card_number)
        
        if "/" in expiry:
            month, year = expiry.split("/")
            card_expiry_formatted = f"{year}/{month}"
        else:
            card_expiry_formatted = expiry
        
        buy_order = f"O-{secrets.randbelow(10001)}"
        session_id = f"S-{secrets.randbelow(10001)}"
        amount = secrets.randbelow(1001) + 1000
        
        resp = tx.create(
            buy_order,
            session_id,
            amount,
            cvc,
            card_number_clean,
            card_expiry_formatted
        )
        
        request.session["transaccion_completa_diferida_amount"] = amount
        
        request_data = {
            "buy_order": buy_order,
            "session_id": session_id,
            "amount": amount,
        }
        
        context = {
            "request_data": request_data,
            "response_data": resp,
        }
        
        return render(request, "transaccion_completa_diferida/create.html", context)
        
    except Exception as e:
        logger.error(f"Error en Transacción Completa Diferida - Create: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def installments(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token")
        installments_number = int(request.GET.get("installments_number", "0"))
        
        resp = tx.installments(token, installments_number)
        
        request_data = {
            "token": token,
            "installments_number": installments_number,
        }
        
        context = {
            "request_data": request_data,
            "response_data": resp,
        }
        
        return render(request, "transaccion_completa_diferida/installments.html", context)
        
    except Exception as e:
        logger.error(f"Error en Transacción Completa Diferida - Installments: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def commit(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token") or request.POST.get("token")
        id_query_installments = request.GET.get("idQueryInstallments") or request.POST.get("idQueryInstallments")
        deferred_period_index = None
        grace_period = False
        
        resp = tx.commit(
            token,
            id_query_installments if id_query_installments else None,
            deferred_period_index,
            grace_period
        )
        
        amount = request.session.get("transaccion_completa_diferida_amount")
        if "transaccion_completa_diferida_amount" in request.session:
            del request.session["transaccion_completa_diferida_amount"]
        
        request_data = {
            "token": token,
            "idQueryInstallments": id_query_installments,
        }
        
        context = {
            "request_data": request_data,
            "response_data": resp,
            "amount": amount,
        }
        
        return render(request, "transaccion_completa_diferida/commit.html", context)
        
    except Exception as e:
        logger.error(f"Error en Transacción Completa Diferida - Commit: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def status(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token")
        
        resp = tx.status(token)
        
        request_data = {
            "token": token,
        }
        
        context = {
            "request_data": request_data,
            "response_data": resp,
        }
        
        return render(request, "transaccion_completa_diferida/status.html", context)
        
    except Exception as e:
        logger.error(f"Error en Transacción Completa Diferida - Status: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def refund(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token")
        amount = int(request.GET.get("amount", "0"))
        
        resp = tx.refund(token, amount)
        
        request_data = {
            "token": token,
            "amount": amount,
        }
        
        context = {
            "request_data": request_data,
            "response_data": resp,
        }
        
        return render(request, "transaccion_completa_diferida/refund.html", context)
        
    except Exception as e:
        logger.error(f"Error en Transacción Completa Diferida - Refund: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def capture(request):
    tx = get_transbank_transaction()
    try:
        token = request.GET.get("token")
        buy_order = request.GET.get("buy_order")
        authorization_code = request.GET.get("authorization_code")
        amount = int(request.GET.get("amount", "0"))
        
        resp = tx.capture(token, buy_order, authorization_code, amount)
        
        request_data = {
            "token": token,
            "buy_order": buy_order,
            "authorization_code": authorization_code,
            "amount": amount,
        }
        
        context = {
            "request_data": request_data,
            "response_data": resp,
            "token": token,
            "amount": amount,
        }
        
        return render(request, "transaccion_completa_diferida/capture.html", context)
        
    except Exception as e:
        logger.error(f"Error en Transacción Completa Diferida - Capture: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})
