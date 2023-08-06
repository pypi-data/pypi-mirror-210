from datetime import datetime, timedelta
from urllib.parse import urljoin
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

import requests
from ckeditor_uploader.fields import RichTextUploadingField
from defusedxml import ElementTree
from model_utils.models import TimeStampedModel
from templated_email import send_templated_mail

from aleksis.core.mixins import ExtensibleModel
from aleksis.core.util.core_helpers import has_person


class NextcloudProvider(ExtensibleModel):
    """Nextcloud provider for file storage."""

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    url = models.URLField(verbose_name=_("URL"))
    username = models.CharField(max_length=255, verbose_name=_("Username"))
    password = models.CharField(max_length=255, verbose_name=_("Password"))

    def __str__(self):
        return self.name

    def build_url(self, path):
        """Build URL for given path."""
        return urljoin(self.url, path)

    def do_request(self, path, method="GET", data=None):
        """Build request for given path."""
        url = self.build_url(path)
        headers = {"OCS-APIRequest": "true"}
        r = requests.request(
            method, url, data=data, auth=(self.username, self.password), headers=headers
        )
        if not r.ok:
            raise Exception(r.text)
        xml = ElementTree.fromstring(r.content)
        return xml

    def test_connection(self):
        """Test connection to Nextcloud provider."""
        r = self.do_request("/ocs/v1.php/cloud/capabilities")
        return r.find("meta").find("status").text == "ok"

    class Meta:
        verbose_name = _("Nextcloud provider")
        verbose_name_plural = _("Nextcloud providers")


class DigitalProductShare(ExtensibleModel):
    """Digital product share."""

    order_item = models.ForeignKey(
        "OrderItem", on_delete=models.CASCADE, verbose_name=_("Order item"), related_name="shares"
    )
    share_id = models.CharField(max_length=255, verbose_name=_("Share ID"))
    share_url = models.URLField(verbose_name=_("Share URL"))
    share_expiration = models.DateTimeField(verbose_name=_("Share expiration"))

    def __str__(self):
        return self.share_id

    class Meta:
        verbose_name = _("Digital product share")
        verbose_name_plural = _("Digital product shares")


class DigitalProduct(ExtensibleModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    nextcloud_provider = models.ForeignKey(
        NextcloudProvider, on_delete=models.CASCADE, verbose_name=_("Nextcloud provider")
    )
    nextcloud_path = models.TextField(verbose_name=_("Nextcloud path"))
    published = models.BooleanField(default=False, verbose_name=_("Published"))

    def get_args_for_share(self, order, expire_date=None):
        if not expire_date:
            expire_date = (timezone.now() + timedelta(days=1)).date()
        return {
            "path": self.nextcloud_path,
            "shareType": 3,
            "permissions": 1,
            "expireDate": expire_date.strftime("%Y-%m-%d"),
            "label": _("Personal download link for {name}").format(name=order.full_name),
        }

    def create_share(self, order_item):
        args = self.get_args_for_share(order_item.order)
        xml = self.nextcloud_provider.do_request(
            "/ocs/v1.php/apps/files_sharing/api/v1/shares", method="POST", data=args
        )
        share_id = xml.find("data").find("id").text
        share_url = xml.find("data").find("url").text
        share_expiration = datetime.strptime(
            xml.find("data").find("expiration").text, "%Y-%m-%d %H:%M:%S"
        )

        return DigitalProductShare.objects.create(
            order_item=order_item,
            share_id=share_id,
            share_url=share_url,
            share_expiration=share_expiration,
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Digital product")
        verbose_name_plural = _("Digital products")


class Item(ExtensibleModel):
    short_name = models.CharField(max_length=255, verbose_name=_("Short name"), unique=True)
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    notice = RichTextUploadingField(
        verbose_name=_("Notice"), help_text=_("Shown below the item"), blank=True
    )
    price = models.FloatField(validators=[MinValueValidator(0.0)])
    max_count = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], verbose_name=_("Maximum count of items")
    )
    count_for_shipping = models.BooleanField(default=True, verbose_name=_("Count for shipping"))
    image = models.ImageField(
        upload_to="order/items", blank=True, null=True, verbose_name=_("Image")
    )
    digital_product = models.BooleanField(default=False, verbose_name=_("Digital product"))
    digital_product_object = models.ForeignKey(
        DigitalProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Digital product"),
    )
    order = models.IntegerField(default=0, verbose_name=_("Order"))

    def __str__(self):
        return self.short_name

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")


class PaymentOption(ExtensibleModel):
    short_name = models.CharField(max_length=255, verbose_name=_("Short name"), unique=True)
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    notice = RichTextUploadingField(
        verbose_name=_("Notice"), help_text=_("Shown below the option"), blank=True
    )
    email_notice = RichTextUploadingField(
        verbose_name=_("Email notice"), help_text=_("Shown in the confirmation email"), blank=True
    )
    price = models.FloatField(validators=[MinValueValidator(0.0)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Payment option")
        verbose_name_plural = _("Payment options")


class ShippingOption(ExtensibleModel):
    short_name = models.CharField(max_length=255, verbose_name=_("Short name"), unique=True)
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    notice = RichTextUploadingField(
        verbose_name=_("Notice"), help_text=_("Shown below the option"), blank=True
    )
    email_notice = RichTextUploadingField(
        verbose_name=_("Email notice"), help_text=_("Shown in the confirmation email"), blank=True
    )
    address_necessary = models.BooleanField(default=False, verbose_name=_("Address necessary"))
    for_digital_products = models.BooleanField(
        default=False, verbose_name=_("For digital products")
    )

    def get_price(self, count):
        for price in self.prices.order_by("price"):
            if price.min_count <= count <= price.max_count:
                return price.price
        return 0

    def __str__(self):
        return self.short_name


class ShippingOptionPrice(ExtensibleModel):
    option = models.ForeignKey(
        ShippingOption, models.CASCADE, related_name="prices", verbose_name=_("Shipping option")
    )
    min_count = models.IntegerField(
        verbose_name=_("Min count of items"), validators=[MinValueValidator(0)]
    )
    max_count = models.IntegerField(
        verbose_name=_("Max count of items"), validators=[MinValueValidator(0)]
    )
    price = models.FloatField(validators=[MinValueValidator(0.0)])

    def __str__(self):
        return f"{self.option}: {self.min_count} <= x <= {self.max_count}"


class OrderForm(ExtensibleModel):
    title = models.CharField(max_length=255, verbose_name=_("Form title"))
    available_items = models.ManyToManyField(
        to=Item, related_name="forms", verbose_name=_("Available items")
    )
    available_shipping_options = models.ManyToManyField(
        to=ShippingOption, related_name="forms", verbose_name=_("Available shipping options")
    )
    available_payment_options = models.ManyToManyField(
        to=PaymentOption, related_name="forms", verbose_name=_("Available payment options")
    )
    help_text = RichTextUploadingField(
        verbose_name=_("Help text"), help_text=_("Shown in the form's footer"), blank=True
    )
    from_email = models.EmailField(verbose_name=_("From email address"))
    from_name = models.CharField(verbose_name=_("From name"), max_length=255)
    access_code = models.CharField(max_length=2555, blank=True, verbose_name=_("Access code"))
    closed = models.BooleanField(default=False, verbose_name=_("Form closed for orders"))
    sender = models.TextField(blank=True, verbose_name=_("Sender"))

    def __str__(self):
        return self.title

    @property
    def email_sender(self):
        return f"{self.from_name} <{self.from_email}>"

    @property
    def total(self):
        return sum([order.total for order in self.orders.all()])

    @property
    def items_count(self):
        return sum([order.items_count for order in self.orders.all()])

    @property
    def confirmed_count(self):
        return sum([order.items_count for order in self.orders.all() if order.confirmed])

    @property
    def paid_count(self):
        return sum([order.items_count for order in self.orders.all() if order.paid])

    @property
    def sent_count(self):
        return sum([order.items_count for order in self.orders.all() if order.sent])

    @property
    def annotated_items(self):
        item_list = []
        for item in self.available_items.all():
            item.items_count = sum(
                [
                    order_item.count
                    for order_item in OrderItem.objects.filter(order__form=self, item=item)
                ]
            )
            item.confirmed_count = sum(
                [
                    order_item.count
                    for order_item in OrderItem.objects.filter(
                        order__form=self, item=item, order__confirmed=True
                    )
                ]
            )
            item.paid_count = sum(
                [
                    order_item.count
                    for order_item in OrderItem.objects.filter(
                        order__form=self, item=item, order__paid=True
                    )
                ]
            )
            item.sent_count = sum(
                [
                    order_item.count
                    for order_item in OrderItem.objects.filter(
                        order__form=self, item=item, order__sent=True
                    )
                ]
            )
            item.items_total = sum(
                [
                    order_item.total
                    for order_item in OrderItem.objects.filter(order__form=self, item=item)
                ]
            )
            item_list.append(item)
        return item_list

    def has_user_access(self, request, access_code):
        access_granted = (
            has_person(request) or self.access_code.strip() == access_code.strip()
        ) and not self.closed
        return access_granted

    class Meta:
        verbose_name = _("Order form")
        verbose_name_plural = _("Order forms")
        permissions = [("manage_orders_of_form", _("Can manage orders of form"))]


class Order(ExtensibleModel, TimeStampedModel):
    form = models.ForeignKey(
        to=OrderForm, on_delete=models.CASCADE, verbose_name=_("Order form"), related_name="orders"
    )

    person = models.ForeignKey(
        to="core.Person", on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Person")
    )

    full_name = models.CharField(max_length=255, verbose_name=_("First and last name"))
    email = models.EmailField(verbose_name=_("Email"))
    notes = models.TextField(verbose_name=_("Notes"), blank=True)

    submitted = models.BooleanField(default=False, verbose_name=_("Submitted"))
    confirmed = models.BooleanField(default=False, verbose_name=_("Confirmed"))
    confirm_key = models.TextField(verbose_name=_("Confirm key"), blank=True)
    paid = models.BooleanField(default=False, verbose_name=_("Paid"))
    sent = models.BooleanField(default=False, verbose_name=_("Sent"))

    shipping_option = models.ForeignKey(
        ShippingOption,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Selected shipping option"),
    )
    shipping_full_name = models.CharField(
        verbose_name=_("First and last name"), max_length=255, blank=True
    )
    second_address_row = models.CharField(
        verbose_name=_("Second address row"), max_length=255, blank=True
    )
    street = models.CharField(verbose_name=_("Street"), max_length=255, blank=True)
    housenumber = models.CharField(verbose_name=_("Housenumber"), max_length=255, blank=True)
    plz = models.CharField(verbose_name=_("PLZ"), max_length=255, blank=True)
    place = models.CharField(verbose_name=_("Place"), max_length=255, blank=True)

    payment_option = models.ForeignKey(
        PaymentOption,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Selected payment option"),
    )

    digital_products_key = models.TextField(verbose_name=_("Digital products key"), blank=True)

    def get_confirm_url(self, request):
        return request.build_absolute_uri(reverse("confirm_order", args=[self.confirm_key]))

    def get_digital_products_url(self, request):
        return request.build_absolute_uri(
            reverse("digital_products", args=[self.digital_products_key])
        )

    @property
    def email_recipients(self):
        return [f'"{self.full_name}" <{self.email}>']

    def submit(self, request):
        self.submitted = True
        self.save()
        self.send_overview(request)

    def send_overview(self, request):
        send_templated_mail(
            template_name="overview",
            from_email=self.form.email_sender,
            recipient_list=self.email_recipients,
            context={"order": self, "confirm_url": self.get_confirm_url(request)},
        )

    def confirm(self, request):
        self.confirmed = True
        self.save()
        send_templated_mail(
            template_name="confirmation",
            from_email=self.form.email_sender,
            recipient_list=self.email_recipients,
            context={"order": self, "confirm_url": self.get_confirm_url(request)},
        )

    def send_pay_confirmation(self):
        self.paid = True
        self.save()
        send_templated_mail(
            template_name="pay_confirmation",
            from_email=self.form.email_sender,
            recipient_list=self.email_recipients,
            context={"order": self},
        )

    def send_confirmation_reminder(self, request):
        send_templated_mail(
            template_name="confirmation_reminder",
            from_email=self.form.email_sender,
            recipient_list=self.email_recipients,
            context={"order": self, "confirm_url": self.get_confirm_url(request)},
        )

    def send_pay_reminder(self, request):
        send_templated_mail(
            template_name="pay_reminder",
            from_email=self.form.email_sender,
            recipient_list=self.email_recipients,
            context={"order": self},
        )

    def send_digital_products_link(self, request):
        send_templated_mail(
            template_name="digital_products",
            from_email=self.form.email_sender,
            recipient_list=self.email_recipients,
            context={"order": self, "digital_products_url": self.get_digital_products_url(request)},
        )

    def __str__(self):
        return f"{self.form}: {self.full_name} [{self.created}]"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.confirm_key:
            self.confirm_key = uuid4()
        if not self.digital_products_key:
            self.digital_products_key = uuid4()

    @property
    def items_count(self):
        return self.items.aggregate(models.Sum("count")).get("count__sum") or 0

    @property
    def items_count_shipping(self):
        return (
            self.items.aggregate(
                count__sum=models.Sum("count", filter=Q(item__count_for_shipping=True))
            ).get("count__sum")
            or 0
        )

    @property
    def shipping_price(self):
        return (
            self.shipping_option.get_price(self.items_count_shipping) if self.shipping_option else 0
        )

    @property
    def payment_price(self):
        return self.payment_option.price if self.payment_option else 0

    @property
    def total(self):
        total = 0
        for item in self.items.all():
            total += item.total
        total += self.shipping_price
        total += self.payment_price
        return total

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        permissions = [("manage_orders", _("Can manage orders"))]


class OrderItem(ExtensibleModel):
    count = models.IntegerField(verbose_name=_("Count"))
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE, verbose_name=_("Item"))
    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, verbose_name=_("Order"), related_name="items"
    )

    def create_share(self):
        if self.item.digital_product_object:
            return self.item.digital_product_object.create_share(self)

    @property
    def current_shares(self):
        if self.item.digital_product_object:
            return self.shares.filter(share_expiration__gte=timezone.now())
        return self.shares.none()

    @property
    def shares_left(self) -> int:
        shares_left = self.count - self.current_shares.count()
        return shares_left if shares_left > 0 else 0

    @property
    def total(self):
        return self.count * self.item.price
