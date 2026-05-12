import os
import secrets
from decimal import Decimal, InvalidOperation

from django.shortcuts import render
from django.views.decorators.http import require_GET
from transbank.error.transbank_error import TransbankError
from transbank.webpay.oneclick.mall_bin_info import MallBinInfo
from transbank.webpay.oneclick.mall_inscription import MallInscription
from transbank.webpay.oneclick.mall_transaction import MallTransaction
from transbank.webpay.oneclick.request import MallTransactionAuthorizeDetails

ERROR_TEMPLATE = "error_pages/general_error.html"
APP_PATH = "/promotions-oneclick-mall"
APP_NAME = "promotions_oneclick_mall"
APP_TITLE = "Webpay Oneclick Mall Promociones"
APP_URL = f"{APP_PATH}/"
APP_BREADCRUMB = {"name": APP_TITLE, "url": APP_URL}
APPROVED_CODE = 0


def get_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"La variable de entorno {name} es obligatoria.")
    return value


def get_commerce_options():
    return (
        get_env("ONECLICK_MALL_PROMOTIONS_COMMERCE_CODE"),
        get_env("ONECLICK_MALL_PROMOTIONS_API_KEY"),
    )


def get_transbank_inscription():
    commerce_code, api_key = get_commerce_options()
    return MallInscription.build_for_integration(commerce_code, api_key)


def get_transbank_transaction():
    commerce_code, api_key = get_commerce_options()
    return MallTransaction.build_for_integration(commerce_code, api_key)


def get_transbank_bin_info():
    commerce_code, api_key = get_commerce_options()
    return MallBinInfo.build_for_integration(commerce_code, api_key)


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


def render_error(request, exception):
    return render(request, ERROR_TEMPLATE, {"error": displayable_error_message(exception)})


def displayable_error_message(exception):
    current = exception

    while current:
        if isinstance(current, TransbankError):
            return str(current)
        current = current.__cause__ or current.__context__

    return "Ocurrió un error inesperado al procesar la operación."


@require_GET
def start(request):
    try:
        inscription = get_transbank_inscription()

        username = f"User-{secrets.randbelow(1000)}"
        email = f"user.{secrets.randbelow(1000)}@example.com"
        response_url = request.build_absolute_uri(f"{APP_PATH}/finish")

        request.session["username"] = username
        request.session["email"] = email

        resp = inscription.start(username, email, response_url)

        context = {
            "app_name": APP_NAME,
            "app_title": APP_TITLE,
            "app_url": APP_URL,
            "app_breadcrumb": APP_BREADCRUMB,
            "request_data": {
                "username": username,
                "email": email,
                "response_url": response_url,
            },
            "response_data": resp,
        }

        return render(request, "promotions_oneclick_mall/start.html", context)
    except Exception as e:
        return render_error(request, e)


@require_GET
def finish(request):
    try:
        inscription = get_transbank_inscription()
        data = {"request": request, "product": APP_TITLE}
        tbk_token = request.GET.get("TBK_TOKEN")
        tbk_orden_compra = request.GET.get("TBK_ORDEN_COMPRA")

        if tbk_orden_compra:
            return render(request, "error_pages/aborted_oneclick.html", data)

        resp = inscription.finish(tbk_token)
        request.session["tbk_user"] = resp.get("tbk_user")

        if resp.get("response_code") != APPROVED_CODE:
            data["response_data"] = resp
            return render(request, "error_pages/rejected.html", data)

        username = request.session.get("username", "")
        tbk_user = resp["tbk_user"]
        context = {
            "app_name": APP_NAME,
            "app_title": APP_TITLE,
            "app_url": APP_URL,
            "app_breadcrumb": APP_BREADCRUMB,
            "request_data": {
                "username": username,
                "tbk_user": tbk_user,
            },
            "username": username,
            "tbk_user": tbk_user,
            "token": tbk_token,
            "response_url": request.build_absolute_uri(f"{APP_PATH}/finish"),
            "response_data": resp,
            "child_commerce_code1": get_env("ONECLICK_MALL_PROMOTIONS_CHILD1_COMMERCE_CODE"),
            "child_commerce_code2": get_env("ONECLICK_MALL_PROMOTIONS_CHILD2_COMMERCE_CODE"),
        }

        return render(request, "promotions_oneclick_mall/finish.html", context)
    except Exception as e:
        return render_error(request, e)


@require_GET
def delete(request):
    try:
        inscription = get_transbank_inscription()
        username = required_text_param(request, "username")
        tbk_user = required_text_param(request, "tbk_user")

        inscription.delete(tbk_user, username)

        return render(request, "promotions_oneclick_mall/delete.html", base_context())
    except Exception as e:
        return render_error(request, e)


@require_GET
def authorize(request):
    try:
        transaction = get_transbank_transaction()

        username = required_text_param(request, "username")
        tbk_user = required_text_param(request, "tbk_user")
        child_code_1 = required_text_param(request, "child_commerce_code1")
        child_code_2 = required_text_param(request, "child_commerce_code2")
        amount1 = required_decimal_param(request, "child_commerce_amount1")
        amount2 = required_decimal_param(request, "child_commerce_amount2")
        installments1 = required_integer_param(request, "child_commerce_installments1")
        installments2 = required_integer_param(request, "child_commerce_installments2")

        buy_order = f"buyOrder_{secrets.randbelow(1000)}"
        buy_order_child1 = f"childBuyOrder1_{secrets.randbelow(1000)}"
        buy_order_child2 = f"childBuyOrder2_{secrets.randbelow(1000)}"

        details = MallTransactionAuthorizeDetails(
            child_code_1,
            buy_order_child1,
            installments1,
            amount1,
        ).add(child_code_2, buy_order_child2, installments2, amount2)

        resp = transaction.authorize(username, tbk_user, buy_order, details)

        context = base_context({"response_data": resp})
        return render(request, "promotions_oneclick_mall/authorize.html", context)
    except Exception as e:
        return render_error(request, e)


@require_GET
def status(request):
    try:
        transaction = get_transbank_transaction()
        buy_order = required_text_param(request, "buy_order")
        resp = transaction.status(buy_order)
        return render(
            request,
            "promotions_oneclick_mall/status.html",
            base_context({"response_data": resp}),
        )
    except Exception as e:
        return render_error(request, e)


@require_GET
def refund(request):
    try:
        transaction = get_transbank_transaction()
        buy_order = required_text_param(request, "buy_order")
        child_commerce_code = required_text_param(request, "child_commerce_code")
        child_buy_order = required_text_param(request, "child_buy_order")
        amount = required_decimal_param(request, "amount")

        resp = transaction.refund(buy_order, child_commerce_code, child_buy_order, amount)

        context = base_context({"response_data": resp, "buy_order": buy_order})
        return render(request, "promotions_oneclick_mall/refund.html", context)
    except Exception as e:
        return render_error(request, e)


@require_GET
def info_bin(request):
    try:
        bin_info = get_transbank_bin_info()
        tbk_user = required_text_param(request, "tbk_user")
        resp = bin_info.query_bin(tbk_user)

        context = base_context({
            "request_data": {"tbk_user": tbk_user},
            "response_data": resp,
        })
        return render(request, "promotions_oneclick_mall/info_bin.html", context)
    except Exception as e:
        return render_error(request, e)


def base_context(extra=None):
    context = {
        "app_name": APP_NAME,
        "app_title": APP_TITLE,
        "app_url": APP_URL,
        "app_breadcrumb": APP_BREADCRUMB,
    }
    if extra:
        context.update(extra)
    return context
