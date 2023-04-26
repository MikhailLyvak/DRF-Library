import unittest
from borrowing.telegram_bot import bot_notification, bot_borrowing_message


class TestTelegramBot(unittest.TestCase):
    async def test_bot_notification(self):
        message = {
            "borrow_date": "2022-01-01",
            "user": "test_user",
            "book": "test_book",
            "is_overdue_for": 5,
        }
        await bot_notification(message)
        expected_text = (
            "==== Borrow overdue for 2022-01-01 ===="
            "Username: test_user"
            "Book name: test_book"
            "Book returns was overdue for 5 days"
        )
        self.assertTrue(
            expected_text in bot_notification.sent_messages["@echo_library"]
        )

    async def test_bot_borrowing_message(self):
        book_info = ("test_book", 1.0, "test_author")
        user_data = ("test@test.com", "test_user")
        borrowing_date = "2022-01-01"
        borrowing_return = "2022-01-08"
        await bot_borrowing_message(
            book_info, user_data, borrowing_date, borrowing_return
        )
        expected_text = (
            "===== User info ====="
            "Username: test_user"
            "User-email: test@test.com"
            "===== Borrowed book ===="
            "Book title: test_book"
            "Author: test_author"
            "Price: 1.0 $"
            "==== Time info ===="
            "Borrowing date: 2022-01-01"
            "Returning date: 2022-01-08"
        )
        self.assertTrue(
            expected_text in bot_borrowing_message.sent_messages["@echo_library"]
        )
