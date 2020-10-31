from django.contrib import admin
from .models import StripeCustomer, Subscription


admin.site.register(StripeCustomer)
admin.site.register(Subscription)