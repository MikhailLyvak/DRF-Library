from django.urls import path, include
from rest_framework import routers
from payment.views import PaymentViewSet
app_name = "payment"
router = routers.DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")
urlpatterns = [
    path("", include(router.urls)),
    path(
        "success/",
        PaymentViewSet.as_view({"get": "payment_success"}),
        name="payment-success",
    ),
    path(
        "cancel/",
        PaymentViewSet.as_view({"get": "payment_cancel"}),
        name="payment-cancel",
    ),
]