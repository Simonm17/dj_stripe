import stripe

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from .models import Subscription, StripeCustomer

stripe.api_key = settings.STRIPE_SECRET_KEY

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
    """ Create a signal function that will assign a stripe customer id to a user
    if user does not have an id.
    """
    user_membership, created = StripeCustomer.objects.get_or_create(
        user=instance)

    if user_membership.stripe_customer_id is None or user_membership.stripe_customer_id == '':
        new_customer_id = stripe.Customer.create(email=instance.email)
        user_membership.stripe_customer_id = new_customer_id['id']
        user_membership.save()

# TODO: it would be a good idea to check for any existing customers without a customer ID to create one if null.


