from django.db.models import Exists, OuterRef

import graphene
from graphene_django import DjangoObjectType

from aleksis.apps.order.models import (
    DigitalProduct,
    DigitalProductShare,
    Item,
    Order,
    OrderForm,
    OrderItem,
    PaymentOption,
    ShippingOption,
    ShippingOptionPrice,
)
from aleksis.core.util.core_helpers import has_person


class ItemType(DjangoObjectType):
    def resolve_image(root, info, **kwargs):
        if root.image:
            return info.context.build_absolute_uri(root.image.url)
        return ""

    class Meta:
        model = Item


class DigitalProductType(DjangoObjectType):
    class Meta:
        model = DigitalProduct


class DigitalProductShareType(DjangoObjectType):
    class Meta:
        model = DigitalProductShare


class ItemWithDigitalProductType(DjangoObjectType):
    def resolve_image(root, info, **kwargs):
        if root.image:
            return info.context.build_absolute_uri(root.image.url)
        return ""

    class Meta:
        model = Item


class OrderItemWithDigitalProductType(DjangoObjectType):
    item = graphene.Field(ItemWithDigitalProductType)
    shares_left = graphene.Int()
    shares = graphene.List(DigitalProductShareType)

    def resolve_shares(self, info, **kwargs):
        return self.current_shares

    class Meta:
        model = OrderItem


class ShippingOptionPriceType(DjangoObjectType):
    class Meta:
        model = ShippingOptionPrice


class ShippingOptionType(DjangoObjectType):
    class Meta:
        model = ShippingOption


class PaymentOptionType(DjangoObjectType):
    class Meta:
        model = PaymentOption


class OrderFormType(DjangoObjectType):
    class Meta:
        model = OrderForm


class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem


class OrderType(DjangoObjectType):
    class Meta:
        model = Order


class DigitalProductsOrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ["id", "form", "digital_products_key"]


class OrderItemInputType(graphene.InputObjectType):
    item = graphene.ID(required=True)
    count = graphene.Int(required=True)


class OrderInputType(graphene.InputObjectType):
    full_name = graphene.String(required=True)
    email = graphene.String(required=True)
    notes = graphene.String(required=False)
    shipping_option = graphene.ID(required=True)
    payment_option = graphene.ID(required=True)
    items = graphene.List(OrderItemInputType, required=True)
    shipping_full_name = graphene.String(required=False)
    second_address_row = graphene.String(required=False)
    street = graphene.String(required=False)
    housenumber = graphene.String(required=False)
    plz = graphene.String(required=False)
    place = graphene.String(required=False)


class DigitalProductsType(graphene.ObjectType):
    order = graphene.Field(DigitalProductsOrderType)
    items = graphene.List(OrderItemWithDigitalProductType)

    def resolve_order(self, info, **kwargs):
        return self

    def resolve_items(self, info, **kwargs):
        return self.items.filter(
            item__digital_product_object__isnull=False, item__digital_product_object__published=True
        )


class SendOrderMutation(graphene.Mutation):
    class Arguments:
        access_code = graphene.String(required=False)
        order_form = graphene.ID(required=True)
        order = OrderInputType(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, **kwargs):
        order_form = OrderForm.objects.get(id=int(kwargs["order_form"]))
        if not order_form.has_user_access(info.context, kwargs["access_code"]):
            raise Exception("Access denied")
        order_args = kwargs["order"]

        items = [
            (order_form.available_items.get(id=int(ordered_item["item"])), ordered_item["count"])
            for ordered_item in order_args["items"]
            if ordered_item["count"] > 0
        ]

        # Ensure that the correct shipping option is used in all cases
        items_with_normal_shipping = any(item for item in items if not item[0].digital_product)
        items_with_digital_product = any(item for item in items if item[0].digital_product)
        shipping_options = order_form.available_shipping_options.all()
        if items_with_normal_shipping:
            shipping_options = shipping_options.exclude(for_digital_products=True)
        if not items_with_normal_shipping and items_with_digital_product:
            shipping_options = shipping_options.exclude(for_digital_products=False)

        shipping_option = shipping_options.get(id=int(order_args["shipping_option"]))
        payment_option = order_form.available_payment_options.get(
            id=int(order_args["payment_option"])
        )

        order = Order.objects.create(
            form=order_form,
            full_name=order_args["full_name"],
            email=order_args["email"],
            notes=order_args["notes"],
            shipping_option=shipping_option,
            payment_option=payment_option,
        )

        if has_person(info.context):
            order.person = info.context.user.person
            order.save()

        if shipping_option.address_necessary:
            order.shipping_full_name = order_args["shipping_full_name"]
            order.second_address_row = order_args["second_address_row"]
            order.street = order_args["street"]
            order.housenumber = order_args["housenumber"]
            order.plz = order_args["plz"]
            order.place = order_args["place"]
            order.save()

        for ordered_item, count in items:
            OrderItem.objects.create(item=ordered_item, count=count, order=order)

        order.submit(info.context)

        return SendOrderMutation(ok=True)


class CreateShareMutation(graphene.Mutation):
    class Arguments:
        key = graphene.String(required=True)
        order_item = graphene.ID(required=True)

    ok = graphene.Boolean()
    share = graphene.Field(DigitalProductShareType)

    def mutate(self, info, key, order_item, **kwargs):
        order_item = OrderItem.objects.filter(
            item__digital_product_object__isnull=False,
            item__digital_product_object__published=True,
            id=order_item,
        ).first()
        if not order_item:
            raise Exception("Invalid order item")
        if order_item.order.digital_products_key != key and not (
            has_person(info.context) and order_item.order.person == info.context.user.person
        ):
            raise Exception("Access denied")

        if order_item.shares_left > 0:
            share = order_item.create_share()

        return CreateShareMutation(ok=True, share=share)


class Query(graphene.ObjectType):
    order_form_by_id = graphene.Field(
        OrderFormType, id=graphene.ID(), access_code=graphene.String(required=False)
    )
    digital_products_by_key = graphene.Field(
        DigitalProductsType, key=graphene.String(required=True)
    )
    digital_products_by_person = graphene.List(DigitalProductsType)

    def resolve_order_form_by_id(self, info, id, access_code=""):  # noqa
        order_form = OrderForm.objects.get(id=int(id))
        if order_form.has_user_access(info.context, access_code):
            return order_form
        return None

    def resolve_digital_products_by_key(self, info, key):
        order = Order.objects.filter(paid=True).get(digital_products_key=key)
        return order

    def resolve_digital_products_by_person(self, info, **kwargs):
        if not has_person(info.context):
            return []
        orders = Order.objects.annotate(
            digital_products_exist=Exists(
                OrderItem.objects.filter(
                    order=OuterRef("pk"),
                    item__digital_product_object__isnull=False,
                    item__digital_product_object__published=True,
                )
            )
        ).filter(digital_products_exist=True, paid=True, person=info.context.user.person)
        return orders


class Mutation(graphene.ObjectType):
    send_order = SendOrderMutation.Field()
    create_share = CreateShareMutation.Field()
