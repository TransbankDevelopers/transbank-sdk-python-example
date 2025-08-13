import random
from django.shortcuts import render
from django.views.decorators.http import require_GET

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys


def get_transbank_transaction():
    return Transaction.build_for_integration(
        IntegrationCommerceCodes.WEBPAY_PLUS,
        IntegrationApiKeys.WEBPAY
    )

@require_GET
def create(request):
    try:
       
        tx = get_transbank_transaction()
        buy_order = f"O-{random.randint(1, 10000)}"
        session_id = f"S-{random.randint(1, 10000)}"
        amount = random.randint(1000, 2000)
        return_url = "https://www.google.com"
        
        resp = tx.create(buy_order, session_id, amount, return_url)
        
        context = {
            'request_data': {'buy_order': buy_order, 'session_id': session_id, 'amount': amount},
            'respond_data': resp
        }
        return render(request, 'webpay_plus/create.html', context)
       
    except Exception as e:
       
        return render(request, "webpay_plus/create.html", {'error': str(e)})
