from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing

RETURN_BOOK_URL = reverse("return-borrowing")


class ReturnBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.return_date = datetime.today() + timedelta(days=14)

        self.book = Book.objects.create(
            title="test_title",
            author="test_author",
            cover="SOFT",
            inventory=1,
            daily_fee=1,
        )
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test_password",
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=self.return_date,
            user_id=self.user.id,
            book_id=self.book.id,
        )

    def test_return_book_auth_required(self):
        res = self.client.get(RETURN_BOOK_URL, args=[self.book.id])
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inventory_added(self):
        self.client.force_authenticate(self.user)
        self.client.get(RETURN_BOOK_URL, args=[self.book.id])
        self.assertEqual(self.book.inventory, 2)

    def test_only_one_time_return(self):
        self.client.force_authenticate(self.user)

        res = self.client.get(RETURN_BOOK_URL, args=[self.book.id])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(RETURN_BOOK_URL, args=[self.book.id])
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_actual_return_date_added(self):
        self.client.force_authenticate(self.user)
        self.client.get(RETURN_BOOK_URL, args=[self.book.id])
        self.assertEqual(self.borrowing.actual_return_date, datetime.today())

    def test_cannot_return_other_user_borrowing(self):
        another_user = get_user_model().objects.create_user(
            email="test111@test.com",
            password="test111_password",
        )
        self.client.force_authenticate(another_user)
        res = self.client.get(RETURN_BOOK_URL, args=[self.book.id])
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
