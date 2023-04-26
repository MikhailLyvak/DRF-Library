import asyncio
from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from .telegram_bot import bot_notification

from book.models import Book
from borrowing.models import Borrowing


def get_borrowings_overdue():
    tomorrow = datetime.today().date() - timedelta(days=1)
    borrowings = Borrowing.objects.filter(expected_return_date__lte=tomorrow)
    for borrowing in borrowings.values():
        borrowing_data = {
            "borrow_date": str(borrowing["borrow_date"]),
            "is_overdue_for": (
                datetime.today().date() - borrowing["expected_return_date"]
            ).days,
            "user": get_user_model().objects.get(pk=borrowing["user_id"]).email,
            "book": Book.objects.get(pk=borrowing["book_id"]).title,
        }
        asyncio.run(bot_notification(borrowing_data))
