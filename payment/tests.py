from datetime import datetime, timedelta

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment, PaymentStatus
from django.test import RequestFactory


class PaymentViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username="testuser@tes.com", password="passtest"
        )
        self.book = Book.objects.create(
            title="testuser@tes.com",
            author="passtest",
            cover="SOFT",
            inventory=5,
            daily_fee=1,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=datetime.now(),
            expected_return_date=datetime.now() + timedelta(days=7),
        )
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse("payment:payment-success"))

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id = (
            "cs_test_a147v5m70bANbxEpmxYkEd3QF9X50UGlFSPQHcFpFCJaWoolMrQ5u48eor"
        )
        session_url = "https://checkout.stripe.com/pay/c/cs_test_a1z1ppjCmHh8PPOyJLu5xsVEaFTTzksJe6jTOAmjvDXajRCTe4mfkmQ2Bm"

        self.payment = Payment.objects.create(
            status=PaymentStatus.PENDING.value,
            session_url=session_url,
            session_id=session_id,
            money_to_pay=self.borrowing.book.daily_fee,
            borrowing_id=self.borrowing,
        )

        self.payment_data = {
            "session_id": session_id,
            "money_to_pay": self.borrowing.book.daily_fee,
            "borrowing_id": self.borrowing.id,
        }
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_payment(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("payment:payments-list"), self.payment_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(id=response.data["payment_id"])
        self.assertEqual(payment.status, PaymentStatus.PENDING.value)
        self.assertEqual(payment.borrowing_id, self.borrowing)

    def test_create_payment_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("payment:payments-list"), self.payment_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_success(self):
        url = reverse("payment:payment-success")
        url += f"?session_id={self.payment.session_id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, PaymentStatus.PAID.value)

    def test_payment_cancel(self):
        url = reverse("payment:payment-cancel")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            "Payment canceled. You can pay later within 24 hours.",
        )

    def test_fine_amount(self):

        FINE_MULTIPLIER = 2

        expected_return_date = datetime.now() - timedelta(days=7)
        actual_return_date = datetime.now()
        self.borrowing.actual_return_date = actual_return_date

        days_overdue = (actual_return_date - expected_return_date).days
        fine_amount = days_overdue * self.borrowing.book.daily_fee * FINE_MULTIPLIER
        expected_fine_amount = 7 * self.borrowing.book.daily_fee * FINE_MULTIPLIER

        self.assertEqual(fine_amount, expected_fine_amount)