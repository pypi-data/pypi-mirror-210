from django.contrib import admin

from guardian.admin import GuardedModelAdminMixin

from .models import (
    DigitalProduct,
    Item,
    NextcloudProvider,
    Order,
    OrderForm,
    OrderItem,
    PaymentOption,
    ShippingOption,
    ShippingOptionPrice,
)


class ItemInline(admin.TabularInline):
    model = Item


class ItemAdmin(admin.ModelAdmin):
    model = Item


admin.site.register(Item, ItemAdmin)


class OrderFormAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    model = OrderForm


admin.site.register(OrderForm, OrderFormAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["confirm_key", "form"]
    list_display = ["__str__", "submitted", "confirmed", "paid", "sent"]
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)


class ShippingOptionPriceInline(admin.TabularInline):
    model = ShippingOptionPrice


class ShippingOptionAdmin(admin.ModelAdmin):
    model = ShippingOption
    inlines = [ShippingOptionPriceInline]


admin.site.register(ShippingOption, ShippingOptionAdmin)


class PaymentOptionAdmin(admin.ModelAdmin):
    model = PaymentOption


admin.site.register(PaymentOption, PaymentOptionAdmin)

admin.site.register(NextcloudProvider)
admin.site.register(DigitalProduct)
