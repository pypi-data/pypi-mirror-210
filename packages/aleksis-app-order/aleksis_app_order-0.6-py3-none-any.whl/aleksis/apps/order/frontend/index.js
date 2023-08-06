export default {
  meta: {
    inMenu: true,
    titleKey: "order.menu_title",
    icon: "mdi-cart-outline",
    permission: "order.view_menu_rule",
  },
  children: [
    {
      path: "list/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "order.listOrders",
      meta: {
        inMenu: true,
        titleKey: "order.list.menu_title",
        icon: "mdi-receipt-outline",
        permission: "order.view_orders_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "list/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "order.showOrder",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "list/:pk/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "order.editOrder",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "list/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "order.deleteOrder",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: ":formId/",
      component: () => import("./components/order_form/OrderForm.vue"),
      name: "order.orderForm",
    },
    {
      path: "confirm/:key/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "order.confirmOrder",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "digital_products/",
      component: () =>
        import("./components/order_form/DigitalProductsPerson.vue"),
      name: "order.digitalProducts",
      meta: {
        inMenu: true,
        titleKey: "order.digital_products.menu_title",
        icon: "mdi-download",
        permission: "order.view_my_digital_products_rule",
      },
    },
    {
      path: "digital_products/:key/",
      component: () => import("./components/order_form/DigitalProducts.vue"),
      name: "order.digitalProducts",
    },
    {
      path: "pick_up/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "order.pickUpOrder",
      meta: {
        inMenu: true,
        titleKey: "order.pick_up.menu_title",
        icon: "mdi-receipt-outline",
        permission: "order.view_orders_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
