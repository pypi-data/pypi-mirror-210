from tempfile import TemporaryDirectory
from typing import Any

from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest, HttpResponse
from django.http.response import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView
from django.views.generic.base import View
from django.views.generic.detail import DetailView

from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin

from aleksis.apps.order.filters import OrderFilter
from aleksis.apps.order.pdf import generate_address_labels, generate_order_labels
from aleksis.apps.order.tables import OrderTable
from aleksis.core.mixins import AdvancedDeleteView, AdvancedEditView
from aleksis.core.util.core_helpers import queryset_rules_filter
from aleksis.core.util.pdf import render_pdf

from .forms import OrderActionForm, PickUpForm
from .models import Order, OrderForm


class OrderConfirmView(View):
    def get(self, request: HttpRequest, key, **kwargs: Any) -> HttpResponse:
        try:
            self.order = Order.objects.get(confirm_key=key)
        except Order.DoesNotExist:
            return HttpResponseNotFound()
        if not self.order.confirmed:
            self.order.confirm(request)
        return render(request, "order/confirmed.html", context={"order": self.order})


class OrderDetailView(PermissionRequiredMixin, DetailView):
    model = Order
    permission_required = "order.manage_order_rule"
    template_name = "order/detail.html"


class OrderEditView(PermissionRequiredMixin, AdvancedEditView):
    model = Order
    fields = (
        "full_name",
        "email",
        "notes",
        "submitted",
        "confirmed",
        "paid",
        "sent",
        "shipping_option",
        "shipping_full_name",
        "second_address_row",
        "street",
        "housenumber",
        "plz",
        "place",
        "payment_option",
    )
    permission_required = "order.manage_order_rule"
    template_name = "order/edit.html"
    success_message = _("The order has been changed successfully.")
    success_url = reverse_lazy("list_orders")

    def post(self, request, *args, **kwargs):
        r = super().post(request, *args, **kwargs)

        order = self.get_object()

        if request.POST.get("mark-as-paid"):
            order.paid = True
            order.save()

        elif request.POST.get("mark-as-paid-email"):
            order.send_pay_confirmation()

        return r


class OrderDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    model = Order
    permission_required = "order.manage_order_rule"
    template_name = "core/pages/delete.html"
    success_message = _("The order has been deleted successfully.")
    success_url = reverse_lazy("list_orders")


class OrderListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    table_class = OrderTable
    model = Order
    template_name = "order/list.html"
    permission_required = "order.view_orders_rule"
    table_pagination = {"per_page": 50}

    filterset_class = OrderFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table"].request = self.request
        context["forms"] = queryset_rules_filter(
            self.request.user, OrderForm.objects.all(), "order.manage_orders_of_form_rule"
        )
        self.action_form = OrderActionForm(
            self.request, self.request.POST or None, queryset=self.get_queryset()
        )
        context["action_form"] = self.action_form
        return context

    def post(self, request, *args, **kwargs):
        r = self.get(request, *args, **kwargs)

        if "action" in self.request.POST and self.action_form.is_valid():
            self.action_form.execute()

        if request.POST.get("all-action"):
            if request.POST.get("print"):
                return render_pdf(request, "order/list_print.html", self.get_context_data())
            elif request.POST.get("packing-lists"):
                return render_pdf(request, "order/packing_lists.html", self.get_context_data())

        # Action for a single object
        if request.POST.get("single-action-pk"):
            order = get_object_or_404(Order, pk=request.POST.get("single-action-pk"))

            if request.POST.get("mark-as-paid"):
                order.paid = True
                order.save()

            elif request.POST.get("mark-as-paid-email"):
                order.send_pay_confirmation()

            elif request.POST.get("mark-as-sent"):
                order.sent = True
                order.save()

        # Actions for all objects
        elif request.POST.get("all-action"):
            if request.POST.get("mark-as-paid"):
                self.object_list.update(paid=True)

            elif request.POST.get("mark-as-paid-email"):
                self.object_list.update(paid=True)
                for order in self.object_list:
                    order.send_pay_confirmation()
            elif request.POST.get("mark-as-sent"):
                self.object_list.update(sent=True)

            elif request.POST.get("labels"):
                with TemporaryDirectory() as temp_dir:
                    filename = generate_order_labels(self.object_list, temp_dir)
                    f = open(filename, "rb")
                    return FileResponse(f, filename="labels.pdf")
            elif request.POST.get("address-labels"):
                with TemporaryDirectory() as temp_dir:
                    filename = generate_address_labels(self.object_list, temp_dir)
                    f = open(filename, "rb")
                    return FileResponse(f, filename="labels.pdf")
        return r


class OrderPickUpFormView(PermissionRequiredMixin, FormView):
    template_name = "order/pickup.html"
    permission_required = "order.view_orders_rule"
    form_class = PickUpForm

    def post(self, request, *args, **kwargs):
        if request.POST.get("order_id_action"):
            try:
                order_id = int(request.POST["order_id_action"])
            except ValueError:
                raise SuspiciousOperation()
            try:
                order = Order.objects.get(pk=order_id)
            except Order.DoesNotExist:
                raise SuspiciousOperation()

            if request.POST.get("abort"):
                return self.get(request, *args, **kwargs)
            elif request.POST.get("collected") and order.paid and not order.sent:
                order.sent = True
                order.save()
                messages.success(request, _("The order was successfully marked as collected."))
            elif request.POST.get("manually-paid-collected") and not order.paid and not order.sent:
                order.sent = True
                order.paid = True
                order.notes += _("\nManually paid")
                order.save()
                messages.success(
                    request, _("The order was successfully marked as manually paid and collected.")
                )

            elif request.POST.get("paid-collected") and not order.paid and not order.sent:
                order.sent = True
                order.paid = True
                order.save()
                messages.success(
                    request, _("The order was successfully marked as normally paid and collected.")
                )

        return super().post(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        context = self.get_context_data()
        order = form.cleaned_data["order_id"]
        print(order)
        context["order"] = order
        context["form"] = PickUpForm()

        return self.render_to_response(context)
