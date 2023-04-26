from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from book.models import Book
from django.contrib.auth import get_user_model


class BookTests(APITestCase):
    def setUp(self):
        self.book1 = Book.objects.create(
            title="Book 1",
            author="Author 1",
            cover="HARD",
            inventory=10,
            daily_fee="1.99"
        )
        self.book2 = Book.objects.create(
            title="Book 2",
            author="Author 2",
            cover="SOFT",
            inventory=5,
            daily_fee="0.99"
        )
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(username='adminuser', password='adminpassword', email='admin@example.com')
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword', email='testuser@example.com')

    def test_get_all_books(self):
        url = reverse("book:book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_book_detail(self):
        url = reverse("book:book-detail", args=[self.book1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Book 1")

    def test_create_book(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("book:book-list")
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 20,
            "daily_fee": "2.99"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)

    def test_update_book(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("book:book-detail", args=[self.book1.id])
        data = {
            "title": "Updated Book",
            "author": "Updated Author",
            "cover": "SOFT",
            "inventory": 15,
            "daily_fee": "1.49"
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Updated Book")

    def test_delete_book(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("book:book-detail", args=[self.book2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)

    def test_get_all_books_unauthorized(self):
        self.client.logout()
        url = reverse("book:book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_book_detail_unauthorized(self):
        self.client.logout()
        url = reverse("book:book-detail", args=[self.book1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Book 1")

    def test_create_book_unauthorized(self):
        self.client.logout()
        url = reverse("book:book-list")
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 20,
            "daily_fee": "2.99"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)

    def test_update_book_unauthorized(self):
        data = {
            "title": "Updated Book",
            "author": "Updated Author",
            "inventory": 15,
            "daily_fee": "1.49"
        }
        url = reverse("book:book-detail", args=[self.book1.id])
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.book1.refresh_from_db()
        self.assertNotEqual(self.book1.title, "Updated Book")

    def test_delete_book_unauthorized(self):
        url = reverse("book:book-detail", args=[self.book2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)

    def test_get_all_books_unauthenticated(self):
        self.client.logout()
        url = reverse("book:book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_book_detail_unauthenticated(self):
        self.client.logout()
        url = reverse("book:book-detail", args=[self.book1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Book 1")
