from datetime import datetime

from .tasks import get_borrowings_overdue
from .telegram_bot import bot_borrowing_message
import asyncio

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from datetime import date, timedelta
from typing import Type

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from .models import Borrowing, User
from .permissions import IsBorrower
from .serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from book.models import Book


class BorrowingViewSet(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user").all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated, IsBorrower)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5

    def create(self, request, *args, **kwargs):
        book_id = request.data.get("book")
        book = Book.objects.get(id=book_id)

        if book.inventory == 0:
            return Response(
                {"notification": "Book is out of stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book.inventory -= 1
        book.save()

        expected_return_date = date.today() + timedelta(days=7)

        borrowing = Borrowing(
            user=request.user, book=book, expected_return_date=expected_return_date
        )
        borrowing.save()

        serializer = self.get_serializer(borrowing)

        book_info = Book.objects.values_list("title", "daily_fee", "author").get(
            pk=serializer.data.get("book")
        )

        user_data = User.objects.values_list("email", "username").get(
            pk=serializer.data.get("user")
        )

        borrowing_date = serializer.data.get("borrow_date")
        borrowing_return = serializer.data.get("expected_return_date")

        asyncio.run(
            bot_borrowing_message(
                book_info, user_data, borrowing_date, borrowing_return
            )
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def get_queryset(self) -> QuerySet:
        user_id = self.request.query_params.get("user_id", None)
        is_active = self.request.query_params.get("is_active", None)

        if self.request.user.is_superuser:
            if user_id:
                queryset = Borrowing.objects.filter(user_id=user_id)
            else:
                queryset = Borrowing.objects.all()
        else:
            queryset = Borrowing.objects.filter(user=self.request.user)

        queryset = queryset.select_related("book", "user")

        if is_active == "true":
            queryset = queryset.filter(actual_return_date=None)
        elif is_active == "false":
            queryset = queryset.exclude(actual_return_date=None)

        return queryset

    def get_serializer_class(self) -> Type[BorrowingSerializer]:
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        return BorrowingSerializer


@api_view(["POST"])
def return_borrowing(request, pk=None):
    current_user = request.user
    try:
        borrowing = Borrowing.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response(
            data="Such a borrowing doesn't exists. Check the url please",
            status=status.HTTP_400_BAD_REQUEST,
        )
    if borrowing.user.id != current_user.id:
        return Response(
            data="It's not your borrowing, you cannot return it",
            status=status.HTTP_403_FORBIDDEN,
        )
    if borrowing.actual_return_date:
        return Response(
            data="This borrowing has been already returned",
            status=status.HTTP_403_FORBIDDEN,
        )
    today = datetime.today()
    book = Book.objects.get(pk=borrowing.book.id)
    book.inventory += 1
    borrowing.actual_return_date = today
    book.save()
    borrowing.save()
    return Response(data="Borrowing returned successful", status=status.HTTP_200_OK)
