from datetime import datetime, date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing


class ReturnBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

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
        self.create_borrowing_url = reverse("borrowing:borrowing-list")

        self.borrowing_data = {"user": self.user.id, "book": self.book.id}

        self.return_borrowing_url = reverse(
            "borrowing:return-borrowing", args=[self.borrowing_data["book"]]
        )

    def test_return_book_auth_required(self):
        res = self.client.post(self.create_borrowing_url, data=self.borrowing_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        borrowing = Borrowing.objects.create(user=self.user, book=self.book)
        res = self.client.post(
            reverse("borrowing:return-borrowing", args=[borrowing.id])
        )
        self.assertNotEqual(res.status_code, status.HTTP_200_OK)

    def test_inventory_added(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.create_borrowing_url, data=self.borrowing_data)
        self.client.post(self.return_borrowing_url)
        self.assertEqual(self.book.inventory, 1)

    def test_only_one_time_return(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.create_borrowing_url, data=self.borrowing_data)

        res = self.client.post(self.return_borrowing_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(self.return_borrowing_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_actual_return_date_added(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.create_borrowing_url, data=self.borrowing_data)
        self.client.post(self.return_borrowing_url)

        borrowing = Borrowing.objects.get(**self.borrowing_data)
        self.assertEqual(borrowing.actual_return_date, datetime.today().date())

    def test_cannot_return_other_user_borrowing(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.create_borrowing_url, data=self.borrowing_data)
        another_user = get_user_model().objects.create_user(
            email="test111@test.com",
            password="test111_password",
        )
        self.client.force_authenticate(another_user)
        res = self.client.post(self.return_borrowing_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class CreateBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test data, such as books and users
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
        self.create_borrowing_url = reverse("borrowing:borrowing-list")

    def test_create_borrowing_inventory_decreased(self):
        self.client.force_authenticate(self.user)
        borrowing_data = {"user": self.user.id, "book": self.book.id}
        res = self.client.post(self.create_borrowing_url, data=borrowing_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 0)

    def test_create_borrowing_serializer_validated(self):
        self.client.force_authenticate(self.user)
        borrowing_data = {"user": self.user.id, "book": self.book.id}
        self.book.inventory = 0
        self.book.save()
        res = self.client.post(self.create_borrowing_url, data=borrowing_data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_borrowing_user_attached(self):
        self.client.force_authenticate(self.user)
        borrowing_data = {"user": self.user.id, "book": self.book.id}
        res = self.client.post(self.create_borrowing_url, data=borrowing_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        borrowing = Borrowing.objects.get(id=res.data["id"])
        self.assertEqual(borrowing.user, self.user)

    def test_create_borrowing_expected_return_date_set(self):
        self.client.force_authenticate(self.user)
        borrowing_data = {"user": self.user.id, "book": self.book.id}
        res = self.client.post(self.create_borrowing_url, data=borrowing_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        borrowing = Borrowing.objects.get(id=res.data["id"])
        expected_return_date = date.today() + timedelta(days=7)
        self.assertEqual(borrowing.expected_return_date, expected_return_date)
