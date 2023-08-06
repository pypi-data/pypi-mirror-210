from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("list/", views.OrderListView.as_view(), name="list_orders"),
    path("list/<int:pk>/", views.OrderDetailView.as_view(), name="show_order"),
    path("list/<int:pk>/edit/", views.OrderEditView.as_view(), name="edit_order"),
    path("list/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="delete_order"),
    path("confirm/<str:key>/", views.OrderConfirmView.as_view(), name="confirm_order"),
    path(
        "digital_products/",
        TemplateView.as_view(template_name="core/empty.html"),
        name="digital_products",
    ),
    path(
        "digital_products/<str:key>/",
        TemplateView.as_view(template_name="core/empty.html"),
        name="digital_products",
    ),
    path("pick_up/", views.OrderPickUpFormView.as_view(), name="pick_up_order"),
]
