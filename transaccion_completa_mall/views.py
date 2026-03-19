import secrets
import logging
import re

from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from transbank.webpay.transaccion_completa.mall_transaction import MallTransaction
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

REQUEST_LABEL = "Petición"
RESPONSE_LABEL = "Respuesta"
FORM_LABEL = "Formulario"

logger = logging.getLogger(__name__)

ERROR_TEMPLATE = "error_pages/general_error.html"
SESSION_DETAILS_KEY = "transaccion_completa_mall_details"


def get_transbank_transaction():
    return MallTransaction.build_for_integration(
        IntegrationCommerceCodes.TRANSACCION_COMPLETA_MALL,
        IntegrationApiKeys.WEBPAY
    )


def build_details():
    return [
        {
            "amount": secrets.randbelow(1001) + 1000,
            "commerce_code": IntegrationCommerceCodes.TRANSACCION_COMPLETA_MALL_CHILD1,
            "buy_order": f"O-{secrets.randbelow(10001)}",
        },
        {
            "amount": secrets.randbelow(1001) + 1000,
            "commerce_code": IntegrationCommerceCodes.TRANSACCION_COMPLETA_MALL_CHILD2,
            "buy_order": f"O-{secrets.randbelow(10001)}",
        },
    ]


@require_GET
def index(request):
    return render(request, "transaccion_completa_mall/index.html")


@require_POST
def create(request):
    navigation = {
        "request": REQUEST_LABEL,
        "response": RESPONSE_LABEL,
        "form": FORM_LABEL,
    }
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
        details = build_details()

        resp = tx.create(
            buy_order,
            session_id,
            card_number_clean,
            card_expiry_formatted,
            details,
            cvc
        )

        request.session[SESSION_DETAILS_KEY] = details

        request_data = {
            "buy_order": buy_order,
            "session_id": session_id,
            "details": details,
        }

        context = {
            "request_data": request_data,
            "response_data": resp,
            "navigation": navigation,
        }

        return render(request, "transaccion_completa_mall/create.html", context)

    except Exception as e:
        logger.error(f"Error en Transacción Completa Mall - Create: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def installments(request):
    tx = get_transbank_transaction()
    navigation = {
        "request": REQUEST_LABEL,
        "response": RESPONSE_LABEL,
        "form": FORM_LABEL,
    }
    try:
        token = request.GET.get("token")
        installments_number = int(request.GET.get("installments_number", "0"))

        details = request.session.get(SESSION_DETAILS_KEY)
        if not details:
            return render(request, ERROR_TEMPLATE, {"error": "Debes crear la transacción antes de consultar cuotas."})

        installment_details = [
            {
                "commerce_code": detail["commerce_code"],
                "buy_order": detail["buy_order"],
                "installments_number": installments_number,
            }
            for detail in details
        ]

        resp = tx.installments(token, installment_details)

        request_data = {
            "token": token,
            "installments_number": installments_number,
        }

        context = {
            "request_data": request_data,
            "response_data": resp,
            "navigation": navigation,
        }

        return render(request, "transaccion_completa_mall/installments.html", context)

    except Exception as e:
        logger.error(f"Error en Transacción Completa Mall - Installments: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def commit(request):
    tx = get_transbank_transaction()
    navigation = {
        "request": REQUEST_LABEL,
        "response": RESPONSE_LABEL,
        "form": FORM_LABEL,
    }
    try:
        token = request.GET.get("token") or request.POST.get("token")
        id_query_installments = request.GET.get("idQueryInstallments") or request.POST.get("idQueryInstallments")
        deferred_period_index = request.GET.get("deferredPeriodIndex") or request.POST.get("deferredPeriodIndex")
        grace_period = request.GET.get("gracePeriod") or request.POST.get("gracePeriod")

        details = request.session.get(SESSION_DETAILS_KEY)
        if not details:
            return render(request, ERROR_TEMPLATE, {"error": "Debes crear la transacción antes de confirmar."})

        commit_details = []
        for detail in details:
            payload = {
                "commerce_code": detail["commerce_code"],
                "buy_order": detail["buy_order"],
                "id_query_installments": id_query_installments if id_query_installments else None,
                "deferred_period_index": deferred_period_index if deferred_period_index else None,
                "grace_period": str(grace_period).lower() == "true" if grace_period is not None else False,
            }
            commit_details.append(payload)

        resp = tx.commit(token, commit_details)

        request_data = {
            "token": token,
            "idQueryInstallments": id_query_installments,
            "deferredPeriodIndex": deferred_period_index,
            "gracePeriod": grace_period,
        }

        context = {
            "request_data": request_data,
            "response_data": resp,
            "navigation": navigation,
        }

        return render(request, "transaccion_completa_mall/commit.html", context)

    except Exception as e:
        logger.error(f"Error en Transacción Completa Mall - Commit: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def status(request):
    tx = get_transbank_transaction()
    navigation = {
        "request": REQUEST_LABEL,
        "response": RESPONSE_LABEL,
    }
    try:
        token = request.GET.get("token")

        resp = tx.status(token)

        request_data = {
            "token": token,
        }

        context = {
            "request_data": request_data,
            "response_data": resp,
            "navigation": navigation,
        }

        return render(request, "transaccion_completa_mall/status.html", context)

    except Exception as e:
        logger.error(f"Error en Transacción Completa Mall - Status: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})


@require_GET
def refund(request):
    tx = get_transbank_transaction()
    navigation = {
        "request": REQUEST_LABEL,
        "response": RESPONSE_LABEL,
    }
    try:
        token = request.GET.get("token")
        buy_order = request.GET.get("buy_order")
        commerce_code = request.GET.get("commerce_code")
        amount = int(request.GET.get("amount", "0"))

        resp = tx.refund(token, buy_order, commerce_code, amount)

        request_data = {
            "token": token,
            "buy_order": buy_order,
            "commerce_code": commerce_code,
            "amount": amount,
        }

        context = {
            "request_data": request_data,
            "response_data": resp,
            "navigation": navigation,
        }

        return render(request, "transaccion_completa_mall/refund.html", context)

    except Exception as e:
        logger.error(f"Error en Transacción Completa Mall - Refund: {str(e)}")
        return render(request, ERROR_TEMPLATE, {"error": str(e)})
