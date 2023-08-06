from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext as _

from aleksis.core.forms import ActionForm

from .models import Order, OrderItem


def send_confirmation_reminder(modeladmin, request, queryset):
    qs = queryset.filter(submitted=True, confirmed=False)
    for order in qs:
        order.send_confirmation_reminder(request)


send_confirmation_reminder.short_description = _("Send confirmation reminder")


def send_pay_reminder(modeladmin, request, queryset):
    qs = queryset.filter(submitted=True, confirmed=True, paid=False)
    for order in qs:
        order.send_pay_reminder(request)


send_pay_reminder.short_description = _("Send pay reminder")


def send_digital_products_link(modeladmin, request, queryset):
    qs = queryset.annotate(
        digital_products_exist=Exists(
            OrderItem.objects.filter(
                order=OuterRef("pk"),
                item__digital_product_object__isnull=False,
                item__digital_product_object__published=True,
            )
        )
    ).filter(digital_products_exist=True, submitted=True, confirmed=True, paid=True)
    for order in qs:
        order.send_digital_products_link(request)


send_digital_products_link.short_description = _("Send digital products link")


class OrderActionForm(ActionForm):
    actions = [send_confirmation_reminder, send_pay_reminder, send_digital_products_link]


class PickUpForm(forms.Form):
    order_id = forms.CharField(
        label=_("Order id"), widget=forms.TextInput(attrs={"autofocus": "autofocus"})
    )

    def clean_order_id(self):
        order_id = self.cleaned_data["order_id"]
        order_id = order_id.strip()
        try:
            order_id = int(order_id)
        except ValueError:
            raise ValidationError(_("You must enter a valid number as order id."))
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise ValidationError(_("This order doesn't exist."))
        return order
