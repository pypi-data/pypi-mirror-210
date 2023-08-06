import rules

from aleksis.core.util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
)

from .models import OrderForm, OrderItem
from .util.predicates import has_order_perm


@rules.predicate
def has_any_digital_product(user, obj):
    return OrderItem.objects.filter(
        order__person=user.person,
        order__paid=True,
        item__digital_product_object__isnull=False,
        item__digital_product_object__published=True,
    ).exists()


manage_orders_of_form_predicate = has_person & (
    has_global_perm("order.manage_orders") | has_object_perm("order.manage_orders_of_form")
)
rules.add_perm("order.manage_orders_of_form_rule", manage_orders_of_form_predicate)

view_orders_predicate = has_person & (
    has_global_perm("order.manage.orders")
    | has_any_object("order.manage_orders_of_form", OrderForm)
)
rules.add_perm("order.view_orders_rule", view_orders_predicate)

manage_order_predicate = has_person & (has_global_perm("order.manage_orders") | has_order_perm)
rules.add_perm("order.manage_order_rule", manage_order_predicate)

view_my_digital_products_predicate = has_person & (has_any_digital_product)
rules.add_perm("order.view_my_digital_products_rule", view_my_digital_products_predicate)

view_menu_predicate = view_orders_predicate | view_my_digital_products_predicate
rules.add_perm("order.view_menu_rule", view_menu_predicate)
