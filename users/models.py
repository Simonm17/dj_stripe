from datetime import datetime

import stripe

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeCustomer(models.Model):
    """ Named StripeCustomer to distinguish from Stripe's Customer class. """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.user.username


class Subscription(models.Model):
    TRIALING = 'TR'
    ACTIVE = 'AC'
    INCOMPLETE = 'IN'
    INCOMPLETE_EXPIRED = 'IP'
    PAST_DUE = 'PD'
    CANCELED = 'CA'
    UNPAID = 'UN'
    STATUS = [
        (TRIALING, 'Trialing'),
        (ACTIVE, 'Active'),
        (INCOMPLETE, 'Incomplete'),
        (INCOMPLETE_EXPIRED, 'Incomplete Expired'),
        (PAST_DUE, 'Past Due'),
        (CANCELED, 'Canceled'),
        (UNPAID, 'Unpaid'),
    ]
    customer = models.OneToOneField(StripeCustomer, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=120, unique=True)

    status = models.CharField(choices=STATUS, max_length=120, default=TRIALING)

    cancel_at_period_end = models.BooleanField(default=False)
    cancel_at = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.customer}, {self.subscription_id}'
