from book.models import Book

from rest_framework import viewsets
from book.serializers import (
    BookSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
