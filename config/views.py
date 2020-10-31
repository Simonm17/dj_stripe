import json

import stripe

from django.views.generic import TemplateView
from django.conf import settings
from django.http import JsonResponse


class HomeView(TemplateView):
    template_name = 'home.html'


def webhook_received(request):
    if request.method == 'POST':
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        request_data = json.loads(request.data)

        if webhook_secret:
            signature = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.data, sig_header=signature, secret=webhook_secret
                )
                data = event['data']
            except Exception as e:
                return e
        else:
            data = request_data['data']
            event_type = request_data['type']

        data_object = data['object']

        if event_type == 'invoice.paid':
            print(data)

        if event_type == 'invoice.payment_failed':
            print(data)

        if event_type == 'customer.subscription.deleted':
            print(data)

        return JsonResponse({'status': 'success'})