from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]

        read_only_fields = ("expected_return_date", "actual_return_date", "user")


class BorrowingListSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = "__all__"


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user",
            "book",
        ]
