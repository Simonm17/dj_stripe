import json
import time
from datetime import datetime

import stripe

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserUpdateForm
from .models import StripeCustomer, Subscription
from django.views.generic import View
from django.contrib.auth.mixins import UserPassesTestMixin


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been updated.')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    context = {
        'user': request.user,
        'form': form
    }
    return render(request, 'users/profile.html', context)


@login_required
def subscribe(request):
    customer = StripeCustomer.objects.get(user=request.user)
    context = {}
    try:
        """
        CONTEXT LIST FOR ACTIVE SUBSCRIPTION:
            - 'subscription': subscription model
            - 'days_until_end': subscription end date - today's date, converted to days
            - 'end_date': last day of subscription after cancellation
        """
        subscription = Subscription.objects.get(customer=customer)
        context['subscription'] = subscription
        if subscription.cancel_at:
            # convert subscription.cancel_at to naive with .replace(tzinfo=None)
            days_until_end = subscription.cancel_at.replace(tzinfo=None) - datetime.today()
            context['days_until_end'] = days_until_end.days
            context['end_date'] = subscription.cancel_at
    except Exception as e:
        print(e)
    return render(request, 'users/subscribe.html', context)


@csrf_exempt
def stripe_config(request):
    """ View for checkout session to retrieve stripe public key """
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    """ View for routing users to stripe checkout session """
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/users/'
        customer_id = StripeCustomer.objects.get(user=request.user).stripe_customer_id
        # client_reference_id=request.user.id if request.user.is_authenticated else None,
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancel/',
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': 'price_1HgEAWFnONXy6XW0sA1W3tuy',
                        'quantity': 1,
                    }
                ],
                subscription_data={
                    'trial_period_days': 30
                }
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@login_required
def success(request):
    """ View for rerouting after successful stripe checkout sesion """
    return render(request, 'users/success.html')


@login_required
def cancel(request):
    """ View for when cancelling stripe checkout session """
    return render(request, 'users/cancel.html')


@login_required
def confirm_cancel(request):
    """ View for confirming to cancel an active subscription """
    try:
        customer = StripeCustomer.objects.get(user=request.user)
        subscription = Subscription.objects.get(customer=customer)
        context = {'subscription': subscription.subscription_id}
        if request.method == 'POST':
            stripe.Subscription.modify(
                subscription.subscription_id,
                cancel_at_period_end=True
            )
            messages.success(request, f"Your subscription will be canceled at the end of the billing period.")
            return redirect('profile')
            """ IMPORTANT: Make sure webhook is set in place to capture cancel event and delete subscription model. """
    except ObjectDoesNotExist:
        pass
    return render(request, 'users/confirm_cancel.html', context)



# def delete_membership(request):
#     """ IMPORTANT: for development testing only. """
#     customer = StripeCustomer.objects.get(user=request.user)
#     sub = Subscription.objects.get(customer=customer)
#     stripe.Subscription.delete(sub.subscription_id)
#     messages.success(request, f'You have successfully deleted {sub} manually.')
#     return HttpResponseRedirect(reverse('profile'))


@csrf_exempt
def stripe_webhook(request):
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        print(f'RETRIEVD STRIPE EVENT WEBHOOK..')
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    """
    SUBSCRIPTION MODEL FIELDS (for reference):
        - customer (foreign key)
        - subscription_id
        - status (choices)
        - cancel_at_period_end (boolean)
        - cancel_at (datetime)
    """
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Fetch all the required data from session
        stripe_customer_id = session.get('customer') # returns customer id 
        stripe_subscription_id = session.get('subscription') # returns subscription id

        # Get the customer model object and create a new StripeCustomer
        customer = StripeCustomer.objects.get(stripe_customer_id=stripe_customer_id)
        try:
            Subscription.objects.create(
                customer=customer,
                subscription_id=stripe_subscription_id
            )
            print(f'{customer} just subscribed.')
        except Exception as e:
            print(e)

    """ NOTE: Initial subscription triggers checkout.session.completed, invoice.paid,
                and customer.subscription.updated on successful transaction.
                Hence use if blocks and no elif's for all event triggers.
    """

    if event['type'] == 'invoice.paid':
        # if reoccuring subscription triggers, do nothing to models and keep them active.
        pass

    if event['type'] == 'invoice.payment_failed':
        """ if automatic payment fails, delete subscription. """
        session = event['data']['object']
        try:
            subscription = Subscription.objects.get(customer=session['customer'])
            subscription.status = INCOMPLETE_EXPIRED
            subscription.delete()
        except Exception as e:
            print(e)

    if event['type'] == 'customer.subscription.updated':
        """ Update the model fields to indicate subscription was canceled. """
        session = event['data']['object']
        customer = StripeCustomer.objects.get(stripe_customer_id=session['customer'])
        if session['cancel_at_period_end'] == True:
            try:
                print(f'DELETING SUB AT PERIOD END')
                subscription = Subscription.objects.get(customer=customer)
                subscription.cancel_at_period_end=True
                subscription.cancel_at=datetime.fromtimestamp(session['cancel_at'])
                subscription.save()
                print(f'SUBSCRIPTION MODEL UPDATED')
            except Exception as e:
                print(e)


    if event['type'] == 'customer.subscription.deleted':
        session = event['data']['object']
        try:
            stripe_customer_id = session.get('customer') # returns customer id 
            stripe_subscription_id = session.get('id') # returns subscription id
            print(stripe_customer_id, stripe_subscription_id)
            customer = StripeCustomer.objects.get(stripe_customer_id=stripe_customer_id)
            sub = Subscription.objects.get(customer=customer, subscription_id=stripe_subscription_id)
            print(customer, sub)
            sub.delete()
        except Exception as e:
            print(e)

    return HttpResponse(status=200)
