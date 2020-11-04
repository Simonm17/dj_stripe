from django.urls import path
from .views import (
    profile,
    create_checkout_session,
    success,
    cancel,
    subscribe,
    stripe_config,
    stripe_webhook,
    confirm_cancel,
    # delete_membership
)


urlpatterns = [
    path('profile/', profile, name='profile'),
    path('create-checkout-session/', create_checkout_session),
    path('subscribe', subscribe, name='subscribe'),
    path('success/', success),
    path('cancel/', cancel),
    path('confirm-cancel/', confirm_cancel, name='confirm_cancel'),
    path('config/', stripe_config),
    # path('delete-membership/', delete_membership, name='delete_membership'),
    path('webhook/', stripe_webhook),
]
