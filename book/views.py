from rest_framework import mixins

from book.models import Book

from rest_framework import viewsets
from book.serializers import (
    BookSerializer,
    BookListSerializer,
    BookDetailSerializer,
)

from book.permissions import IsAdminOrReadOnly


class BookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        if self.action == "retrieve":
            return BookDetailSerializer

        return BookSerializer
