from datetime import date

import stripe
from django.conf import settings
from django.urls import reverse
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from stripe.error import SignatureVerificationError
from payment.models import Payment, PaymentStatus
from payment.permissions import PaymentPermission
from payment.serializers import PaymentSerializer

CONST_PAYMENT_FEE_DAYS = 7

FINE_MULTIPLIER = 2

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, PaymentPermission]

    def get_queryset(self):
        queryset = Payment.objects.all()
        if self.request.user.is_staff:
            return queryset
        return Payment.objects.filter(
            borrowing_id__user=self.request.user.id
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        borrowing = serializer.validated_data["borrowing_id"]
        total_price = borrowing.book.daily_fee * CONST_PAYMENT_FEE_DAYS
        name = serializer.validated_data["borrowing_id"]
        success_url = (
            request.build_absolute_uri(reverse("payment:payment-success"))
            + f"?session_id={{CHECKOUT_SESSION_ID}}"
        )

        cancel_url = request.build_absolute_uri(
            reverse("payment:payment-cancel")
        )
        borrowing.actual_return_date = date.today()
        if borrowing.actual_return_date > borrowing.expected_return_date:
            days_overdue = (borrowing.actual_return_date - borrowing.expected_return_date).days
            fine_amount = days_overdue * borrowing.book.daily_fee * FINE_MULTIPLIER
            total_price += fine_amount
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": name,
                        },
                        "unit_amount": int(total_price) * 100,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        payment = Payment.objects.create(
            status=PaymentStatus.PENDING.value,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=total_price,
            borrowing_id=name,
        )
        payment.save()
        return Response(
            {"payment_id": payment.id, "session_url": payment.session_url},

            status=status.HTTP_201_CREATED,
        )

    def payment_success(self, request):
        try:
            session_id = request.query_params.get("session_id")
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                payment = Payment.objects.get(session_id=session_id)
                if payment.status == PaymentStatus.PAID.value:
                    return Response(
                        "Payment already marked as PAID",
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                payment.status = PaymentStatus.PAID.value
                payment.save()
                return Response(
                    "Payment marked as PAID",
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    "Payment not paid",
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (KeyError,
                Payment.DoesNotExist,
                SignatureVerificationError):
            raise Http404

    def payment_cancel(self, request):
        return Response(
            "Payment canceled. You can pay later within 24 hours.",
            status=status.HTTP_200_OK,
        )
