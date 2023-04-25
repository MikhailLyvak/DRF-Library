import stripe
from django.conf import settings


from rest_framework import viewsets, status
from rest_framework.response import Response


from payment.models import Payment
from payment.permissions import PaymentPermission
from payment.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [PaymentPermission]

    def get_queryset(self):
        queryset = Payment.objects.all()
        if self.request.user.is_staff:
            return queryset
        return Payment.objects.filter(borrowing_id__user=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["money_to_pay"]
        name = serializer.validated_data["borrowing_id"]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': name,
                    },
                    'unit_amount': int(amount) * 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/api/payments/',
            # cancel_url='http://localhost:4242/cancel',
        )
        payment = Payment.objects.create(
            status="PAID",
            session_url=session.url,
            session_id=session.id,
            money_to_pay=amount,
            borrowing_id=name,
        )
        payment.save()

        return Response(session.url, status=status.HTTP_303_SEE_OTHER)

